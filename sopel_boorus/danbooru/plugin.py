"""sopel-boorus danbooru plugin

Part of sopel-boorus.

Copyright 2024 dgw, technobabbl.es

Licensed under the Eiffel Forum License v2.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sopel import plugin, tools

from .. import errors
from ..util import get_json, normalize_ratings, QueryCache
from .types import DanbooruPost


if TYPE_CHECKING:
    from sopel.bot import SopelWrapper


API_BASE = 'https://danbooru.donmai.us'
API_POST_TMPL = API_BASE + '/posts/{id}.json'
API_SEARCH = API_BASE + '/posts.json'
CACHE_KEY = 'danbooru_cache'
LOGGER = tools.get_logger('danbooru')
OUTPUT_PREFIX = '[Danbooru] '


def setup(bot):
    bot.memory[CACHE_KEY] = QueryCache(25)


def shutdown(bot):
    try:
        del bot.memory[CACHE_KEY]
    except KeyError:
        pass


def fetch_post(id_: int) -> dict:
    """Fetch a Danbooru post by ID.

    Exceptions from :func:`..util.get_json` can bubble up.
    """
    return get_json(API_POST_TMPL.format(id=id_))


def search_tags(tags: str) -> dict:
    """Search for random posts matching ``tags``, after normalization.

    Exceptions from :func:`..util.get_json` can bubble up.
    """
    tags += ' random:10'

    data = get_json(API_SEARCH, params={
        'tags': tags,
    })

    if 'error' in data:
        LOGGER.info(
            "Danbooru API error: %s (%s)", data['error'], data['message'])
        raise errors.APIError(data['message'])


def refresh_cache(cache: QueryCache, query: str):
    """Fetch and store a batch of results for ``query`` in the ``cache``."""
    posts = search_tags(query)
    new_items: list[DanbooruPost] = []

    for post in posts:
        # no need to shuffle anything here, since `search_tags()` already adds
        # `random:10` to the search query; danbooru.donmai.us shuffles for us
        new_items.append(DanbooruPost.new_from_json(post))

    cache.store(query, new_items)


def say_post(bot: SopelWrapper, post: DanbooruPost, link=True):
    template = "Score: {score} | Rating: {rating} | Tags: {tags}"

    bot.say(
        template.format(
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
def danbooru(bot, trigger):
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
            refresh_cache(post_cache, query)
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


@plugin.url(r'https?://danbooru\.donmai\.us/posts/(\d+)/?$')
@plugin.output_prefix(OUTPUT_PREFIX)
def danbooru_url(bot, trigger):
    """Look up a Danbooru post when linked in chat."""
    data = fetch_post(trigger.group(1))
    post = DanbooruPost.new_from_json(data)
    say_post(bot, post, link=False)
