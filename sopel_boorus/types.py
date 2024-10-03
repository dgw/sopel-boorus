"""Abstract booru types

Part of sopel-boorus

Copyright 2024 dgw, technobabbl.es

Licensed under the Eiffel Forum License v2.
"""
from __future__ import annotations

from datetime import datetime

from html import unescape


class AbstractBooruPost:
    """Interface definition of a booru post.

    Defines properties that are expected to be common across all supported
    booru types/backends.
    """

    def __init__(self,
                 id_: int,
                 rating: str,
                 tags: str,
                 score: int,
                 creation_date: str,
                 ):
        raise NotImplementedError

    @classmethod
    def new_from_json(cls, data):
        """Create and return a new post object using JSON ``data``."""
        raise NotImplementedError

    @property
    def id(self) -> int:
        """ID of the post on the site, usually a number in its URL."""
        raise NotImplementedError

    @property
    def rating(self) -> str:
        """The post's content rating.

        Sometimes one of "general", "sensitive", "questionable", "Explicit".

        Sometimes shorter forms (e.g. "safe", or "g"/"s"/"q"/"e").

        This field's value is a string, but otherwise its possible values and
        their meanings are booru-dependent.
        """
        raise NotImplementedError

    @property
    def tags(self) -> list[str]:
        """The post's tags, as a list."""
        raise NotImplementedError

    @property
    def tag_string(self) -> str:
        """The post's tags, as a string for display."""
        return unescape(' '.join(self.tags))

    @property
    def date(self) -> datetime:
        """When the post was uploaded."""
        raise NotImplementedError

    @property
    def url(self) -> str:
        """The post's URL on the booru site.

        Most likely generated using a known base URL + the post's :attr:`id`.
        """
        raise NotImplementedError
