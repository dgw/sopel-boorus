"""sopel-boorus error types

Part of sopel-boorus.

Copyright 2024 dgw, technobabbl.es

Licensed under the Eiffel Forum License v2.
"""
from __future__ import annotations


class BooruError(Exception):
    """Base type."""


class ServerError(BooruError):
    """Error happened trying to connect to API server."""


class APIError(BooruError):
    """Request succeeded, but the API result was erroneous."""
