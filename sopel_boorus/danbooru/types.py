"""danbooru types

Part of sopel-boorus

Copyright 2024 dgw, technobabbl.es

Licensed under the Eiffel Forum License v2.
"""
from __future__ import annotations

from datetime import datetime
from typing import Type

from sopel.formatting import colors

from ..types import AbstractBooruPost


RATING_MAP = {
    'g': 'general',
    's': 'sensitive',
    'q': 'questionable',
    'e': 'explicit',
}
RATING_COLOR_MAP = {
    'g': colors.LIGHT_GREEN,
    's': colors.YELLOW,
    'q': colors.ORANGE,
    'e': colors.RED,
}


class DanbooruPost(AbstractBooruPost):
    """Object holding only the Danbooru post details we need."""

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

        self._timestamp = datetime.fromisoformat(creation_date)

    @classmethod
    def new_from_json(
        cls: Type[DanbooruPost],
        data: dict
    ) -> DanbooruPost:
        return cls(
            data['id'],
            data['rating'],
            data['tag_string'],
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
        return RATING_MAP.get(self._rating)

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
            'https://danbooru.donmai.us/posts/{id}'
            .format(id=self._id)
        )
