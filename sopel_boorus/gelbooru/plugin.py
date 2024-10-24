"""sopel-boorus gelbooru plugin

Part of sopel-boorus.

Copyright 2024 dgw, technobabbl.es

Based on work by Max Gurela (c) 2014,
https://github.com/maxpowa/inumuta-modules/blob/master/gelbooru.py

Adapted for use with Sopel 8 and Python 3 by dgw (c) 2024

Licensed under the Eiffel Forum License v2.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sopel import plugin, tools

from ..util import get_json, normalize_ratings, QueryCache
from .types import GelbooruPost


if TYPE_CHECKING:
    from sopel.bot import SopelWrapper


API_BASE = 'https://gelbooru.com/index.php'
CACHE_KEY = 'gelbooru_cache'
LOGGER = tools.get_logger('gelbooru')
OUTPUT_PREFIX = '[Gelbooru] '


def setup(bot):
    bot.memory[CACHE_KEY] = QueryCache(25)


def shutdown(bot):
    try:
        del bot.memory[CACHE_KEY]
    except KeyError:
        pass


def fetch_post(id_: int) -> dict:
    """Fetch a Gelbooru post by ID.

    Exceptions from :func:`..util.get_json` can bubble up.
    """
    return get_json(API_BASE, params={
        'page': 'dapi',
        's': 'post',
        'q': 'index',
        'id': id_,
        'json': 1,
    })['post'][0]


def search_tags(tags: str) -> dict:
    """Search for random posts matching ``tags``, after normalization.

    Exceptions from :func:`..util.get_json` can bubble up.
    """
    tags += ' sort:random'

    return get_json(API_BASE, params={
        'page': 'dapi',
        's': 'post',
        'q': 'index',
        'limit': 10,
        'tags': tags,
        'json': 1,
    })


def refresh_cache(cache: QueryCache, query: str):
    """Fetch and store a batch of results for ``query`` in the ``cache``."""
    data = search_tags(query)
    posts = data.get('post', [])

    if not posts:
        return

    new_items: list[GelbooruPost] = []
    for post in posts:
        # no need to shuffle anything here, since `search_tags()` already adds
        # `sort:random` to the search query; gelbooru.com shuffles for us
        new_items.append(GelbooruPost.new_from_json(post))

    cache.store(query, new_items)


def say_post(bot: SopelWrapper, post: GelbooruPost, link=True):
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


@plugin.commands('gelbooru', 'gelb')
@plugin.example('.gelb <tags>')
@plugin.output_prefix(OUTPUT_PREFIX)
def gelbooru(bot, trigger):
    """Get a random image post from gelbooru.com, filtered by <tags>."""
    post_cache = bot.memory[CACHE_KEY]

    if (query := trigger.group(2)) is None:
        query = ''
    else:
        query = query.strip().lower()

    query = normalize_ratings(query)

    if post_cache.size(query) < 2:
        refresh_cache(post_cache, query)

    if post_cache.size(query) == 0:
        bot.reply('No results for %r.' % query)
        return

    post = post_cache.get(query)
    say_post(bot, post, link=True)


@plugin.url(r'https?://gelbooru\.com.*(?:\?|&)id\=([-_a-zA-Z0-9]+)')
@plugin.output_prefix(OUTPUT_PREFIX)
def gelbooru_url(bot, trigger):
    """Look up a Gelbooru post when linked in chat."""
    # first, skip anything that isn't actually a post
    # like a tracker issue or forum thread
    # (WAY easier to do it this way than in regex)
    if 'page=post' not in trigger:
        return plugin.NOLIMIT

    data = fetch_post(trigger.group(1))
    post = GelbooruPost.new_from_json(data)
    say_post(bot, post, link=False)
