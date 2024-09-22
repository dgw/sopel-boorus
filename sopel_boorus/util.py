"""sopel-boorus utility module

Part of sopel-boorus.

Copyright 2024 dgw, technobabbl.es

Licensed under the Eiffel Forum License v2.
"""
from __future__ import annotations

from typing import Any, Generator

from pylru import lrucache
import requests

from sopel.tools import get_logger

from . import errors


LOGGER = get_logger('boorus.util')


def get_json(url: str, params: dict[str, Any] | None = None) -> dict:
    """Fetch data from a JSON endpoint and return the parsed data.

    This function only deals with GET requests, but its advantage is in
    managing the user-agent, timeouts, and other boilerplate, plus translating
    the various errors ``requests`` might raise into custom types with a
    human-friendly message that can be sent to IRC.
    """
    try:
        r = requests.get(url=url,
                         params=params,
                         timeout=(10.0, 4.0),)
    except requests.exceptions.ConnectTimeout:
        raise errors.ServerError("Connection timed out.")
    except requests.exceptions.ConnectionError:
        raise errors.ServerError("Couldn't connect to server.")
    except requests.exceptions.ReadTimeout:
        raise errors.ServerError("Server took too long to send data.")
    if r.status_code == 422:
        raise errors.APIError("You probably used too many tags. (HTTP 422)")
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise errors.APIError("HTTP error " + str(e.response.status_code))
    try:
        data = r.json()
    except ValueError:
        LOGGER.error("Couldn't decode response as JSON:\n%r", r.text)
        raise errors.APIError("Couldn't decode API response.")

    # that should be all of the possible error cases handled;
    # by this point, the data should be actual data.
    return data


def normalize_ratings(tags: str) -> str:
    """Ensure there is a rating in the given ``tags`` list.

    Substitutes certain keywords (e.g. ``safe``, ``sfw``, ``lewd``, ``nsfw``)
    with ``rating:`` operators, for user convenience.

    If no rating is present after checking all substitutions, appends
    ``rating:general`` for SFW results.
    """
    if not tags:
        tags = 'rating:general'
    else:
        tags = (
            tags.replace('explicit', 'rating:explicit')
            .replace('nsfw', 'rating:explicit')
            .replace('lewd', 'rating:questionable')
            .replace('safe', 'rating:general')
            .replace('sfw', 'rating:general')
        )
    if 'rating:' not in tags:
        tags += ' rating:general'
    return tags.strip()


class QueryCache:
    """LRU cache for tag search results."""

    def __init__(self, size: int = 25):
        self._cache = lrucache(size)

    def __contains__(self, key: str) -> bool:
        return key in self._cache

    def __len__(self) -> int:
        return len(self._cache)

    def keys(self) -> Generator:
        return self._cache.keys()

    def store(self, key: str, values: list):
        if key not in self._cache:
            self._cache[key] = []

        self._cache[key].extend(values)

    def get(self, key: str):
        if self._cache.peek(key):
            values = self._cache.get(key)
            ret = values.pop()

            if len(values) == 0:
                # proactively clean up empty lists
                self._cache.pop(key)

            return ret
        return None

    def size(self, key: str) -> int:
        if key not in self:
            return 0

        if val := self._cache.peek(key):
            return len(val)

        # feels unnecessary, but also safer
        return 0
