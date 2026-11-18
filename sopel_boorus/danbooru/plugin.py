"""sopel-boorus danbooru plugin

Part of sopel-boorus.

Copyright 2024 dgw, technobabbl.es

Licensed under the Eiffel Forum License v2.
"""
from __future__ import annotations

from importlib.metadata import version
from typing import TYPE_CHECKING, Any

from sopel import plugin, tools

from .. import errors
from ..util import get_json as util_get_json, normalize_ratings, QueryCache
from .types import DanbooruPost, DanbooruSettings


if TYPE_CHECKING:
    from sopel.bot import SopelWrapper
    from sopel.config import Config
    from sopel.trigger import Trigger


API_BASE = 'https://danbooru.donmai.us'
API_POST_TMPL = API_BASE + '/posts/{id}.json'
API_SEARCH = API_BASE + '/posts.json'
CACHE_KEY = 'danbooru_cache'
LOGGER = tools.get_logger('danbooru')
OUTPUT_PREFIX = '[Danbooru] '


def setup(bot):
    bot.memory[CACHE_KEY] = QueryCache(25)
    bot.settings.define_section('danbooru', DanbooruSettings)


def configure(settings):
    settings.define_section('danbooru', DanbooruSettings)
    print(
        "If set, your Danbooru username will be included in the request "
        "headers when fetching posts, so Danbooru admins can contact you "
        "about any problems with your bot.")
    settings.danbooru.configure_setting(
        'username',
        'Danbooru username:')


def shutdown(bot):
    try:
        del bot.memory[CACHE_KEY]
    except KeyError:
        pass


def _build_danbooru_headers(settings: Config) -> dict[str, str]:
    """Build Danbooru-specific HTTP headers.

    Follows Danbooru's suggested User-Agent format with booru username included,
    but falls back to a clean "sopel-boorus/<version>" if no username is set.

    Args:
        settings: Sopel's Config object, for reading from this plugin's section.

    Returns:
        A dict of HTTP headers with a Danbooru-compliant User-Agent.
    """
    agent = "sopel-boorus/{}".format(version('sopel-boorus'))
    if username := settings.danbooru.username:
        agent += " ({})".format(username)

    return {
        "User-Agent": agent,
    }


def get_json(
    settings: Config,
    url: str,
    params: dict[str, Any] | None = None,
) -> list | dict:
    """Wrapper around util.get_json() with Danbooru-specific headers.

    This is a convenience wrapper that automatically includes Danbooru's
    preferred User-Agent format and any configured authentication.

    Args:
        settings: The Sopel config object.
        url: The URL to fetch.
        params: Query parameters to pass to the endpoint.

    Returns:
        The parsed JSON data as a dict or list.

    Raises:
        ServerError: If a connection or timeout error occurs.
        APIError: If the API returns an error or the response cannot be parsed.
    """
    return util_get_json(
        url,
        params=params,
        headers=_build_danbooru_headers(settings),
    )


def fetch_post(id_: int, settings: Config) -> dict:
    """Fetch a Danbooru post by ID.

    Args:
        id_: The post ID.
        settings: The Sopel config object.

    Returns:
        The parsed JSON post data.

    Raises:
        Exceptions from :func:`get_json` can bubble up.
    """
    return get_json(settings, API_POST_TMPL.format(id=id_))


def search_tags(tags: str, settings: Config) -> list:
    """Search for random posts matching ``tags``, after normalization.

    Args:
        tags: Search tags.
        settings: The Sopel config object.

    Returns:
        A list of matching posts.

    Raises:
        Exceptions from :func:`get_json` can bubble up.
    """
    tags += ' random:10'

    data = get_json(
        settings,
        API_SEARCH,
        params={'tags': tags},
    )

    if 'error' in data:
        # Bit weird but should be safe. The expected list of post dicts will
        # never contain the literal string 'error', but for errors the API
        # returns a dict with 'error' and 'message' keys instead of a list.
        LOGGER.info(
            "Danbooru API error: %s (%s)", data['error'], data['message'])
        raise errors.APIError(data['message'])

    # thankfully, if there was no error, Danbooru just directly returns a list
    # (which is simply empty if there are no results)
    return data


def refresh_cache(cache: QueryCache, query: str, settings: Config):
    """Fetch and store a batch of results for ``query`` in the ``cache``.

    Args:
        cache: The query cache to store results in.
        query: The search query.
        settings: The Sopel config object.
    """
    posts = search_tags(query, settings)

    if not posts:
        return

    new_items: list[DanbooruPost] = []
    for post in posts:
        # no need to shuffle anything here, since `search_tags()` already adds
        # `random:10` to the search query; danbooru.donmai.us shuffles for us
        new_items.append(DanbooruPost.new_from_json(post))

    cache.store(query, new_items)


def say_post(bot: SopelWrapper, post: DanbooruPost, link=True):
    template = "ID: {id} | Score: {score} | Rating: {rating} | Tags: {tags}"

    bot.say(
        template.format(
            id=post.id,
            score=post.score_str,
            rating=post.display_rating,
            tags=post.tag_string,
        ),
        truncation=' […]',
        trailing=(' | ' + post.url) if link else '',
    )


@plugin.commands('danbooru', 'danb')
@plugin.example('.danb <tags>')
@plugin.output_prefix(OUTPUT_PREFIX)
def danbooru(bot: SopelWrapper, trigger: Trigger):
    """Get a random image post from danbooru.donmai.us, filtered by <tags>."""
    post_cache = bot.memory[CACHE_KEY]

    if (query := trigger.group(2)) is None:
        query = ''
    else:
        query = query.strip().lower()

    query = normalize_ratings(query)
    error = None

    if post_cache.size(query) < 2:
        try:
            refresh_cache(post_cache, query, bot.settings)
        except errors.APIError as exc:
            error = exc

    if error is not None:
        bot.reply('%s' % error)
        return
    elif post_cache.size(query) == 0:
        bot.reply('No results for %r.' % query)
        return

    post = post_cache.get(query)
    say_post(bot, post, link=True)


@plugin.url(r'https?://danbooru\.donmai\.us/(?:posts|post/show)/(\d+)/?(?:[?#].*|$)')
@plugin.output_prefix(OUTPUT_PREFIX)
def danbooru_url(bot: SopelWrapper, trigger: Trigger):
    """Look up a Danbooru post when linked in chat."""
    data = fetch_post(trigger.group(1), bot.settings)
    post = DanbooruPost.new_from_json(data)
    say_post(bot, post, link=False)
