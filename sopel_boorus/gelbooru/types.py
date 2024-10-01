"""gelbooru types

Part of sopel-boorus

Copyright 2024 dgw, technobabbl.es

Licensed under the Eiffel Forum License v2.
"""
from __future__ import annotations

from datetime import datetime
from typing import Type

from sopel.formatting import colors

from ..types import AbstractBooruPost


RATING_COLOR_MAP = {
    'general': colors.LIGHT_GREEN,
    'sensitive': colors.YELLOW,
    'questionable': colors.ORANGE,
    'explicit': colors.RED,
}


class GelbooruPost(AbstractBooruPost):
    """Object holding only the Gelbooru post details we need."""

    def __init__(self,
                 id_: int,
                 rating: str,
                 tags: str,
                 score: int,
                 creation_date: str,
                 ):
        self._id = id_
        self._rating = rating
        self._tags = tags.split(' ')
        self._score = score

        # I kind of hate Gelbooru's date format:
        #     Wed Sep 18 15:00:46 -0500 2024
        # Strip off the weekday to reduce system-locale-related parse issues
        # (but they're not eliminated completely; month abbreviations vary
        # across languages, too...which is why I hate Gelbooru's date format)
        creation_date = ' '.join(creation_date.split(' ')[1:])
        self._timestamp = datetime.strptime(
            creation_date, '%b %d %H:%M:%S %z %Y')

    @classmethod
    def new_from_json(
        cls: Type[GelbooruPost],
        data: dict
    ) -> GelbooruPost:
        return cls(
            data['id'],
            data['rating'],
            data['tags'],
            data['score'],
            data['created_at'],
        )

    @property
    def id(self) -> int:
        return self._id

    @property
    def id_str(self) -> str:
        return str(self.id)

    @property
    def rating(self) -> str:
        return self._rating

    @property
    def rating_color(self) -> str:
        return RATING_COLOR_MAP.get(self._rating)

    @property
    def tags(self) -> str:
        return self._tags

    @property
    def score(self) -> int:
        return self._score

    @property
    def score_str(self) -> str:
        return str(self.score)

    @property
    def date(self) -> datetime:
        return self._timestamp

    @property
    def url(self) -> str:
        return (
            'https://gelbooru.com/index.php?page=post&s=view&id={id}'
            .format(id=self._id)
        )
