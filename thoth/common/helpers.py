#!/usr/bin/env python3
# thoth-common
# Copyright(C) 2018, 2019, 2020 Fridolin Pokorny
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Various utilities to make your life easier."""

import datetime
import os
import re

from datetime import timezone

from typing import Any
from typing import Dict
from typing import Generator
from typing import Optional
from typing import TypeVar

from contextlib import contextmanager

T = TypeVar("T")

SERVICE_TOKEN_FILENAME = "/var/run/secrets/kubernetes.io/serviceaccount/token"
SERVICE_CERT_FILENAME = "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"

_DATETIME_FORMAT_STRING = "%Y-%m-%dT%H:%M:%S.%f"


@contextmanager
def cwd(target: str) -> Generator[str, None, None]:
    """Manage cwd in a pushd/popd fashion."""
    curdir = os.getcwd()
    os.chdir(target)
    try:
        yield curdir
    finally:
        os.chdir(curdir)


def get_default_datetime_format() -> str:
    """Return default datetime format string."""
    return _DATETIME_FORMAT_STRING


def parse_datetime(datetime_string: str) -> datetime.datetime:
    """Parse datetime string represented in ISO format."""
    parsed = datetime.datetime.strptime(datetime_string, _DATETIME_FORMAT_STRING)
    # Make all timezone unaware datetimes timezone aware.
    return parsed.replace(tzinfo=timezone.utc)


def format_datetime(dt: datetime.datetime) -> str:
    """Return datetime string in default format."""
    # We use strftime to make sure we do not propagate timezone information. We use UTC all over the places.
    return dt.strftime(_DATETIME_FORMAT_STRING)


def datetime_str2timestamp(datetime_string: str) -> int:
    """Parse datetime string represented in ISO format and return timestamp."""
    return int(parse_datetime(datetime_string).timestamp())


def datetime2datetime_str(dt: Optional[datetime.datetime] = None) -> str:
    """Create a string representation of a datetime."""
    # We use strftime to make sure we do not propagate timezone information. We use UTC all over the places.
    if dt is None:
        return datetime.datetime.utcnow().strftime(_DATETIME_FORMAT_STRING)

    return dt.strftime(_DATETIME_FORMAT_STRING)


def datetime_str_from_timestamp(timestamp: int) -> str:
    """Convert a timestamp to datetime string representation."""
    return datetime2datetime_str(timestamp2datetime(timestamp))


def timestamp2datetime(timestamp: int) -> datetime.datetime:
    """Convert a timestamp to datetime respecting UTC."""
    return datetime.datetime.fromtimestamp(timestamp).replace(tzinfo=timezone.utc)


def _get_incluster_token_file(token_file: Optional[str] = None) -> str:
    return token_file if token_file is not None else SERVICE_TOKEN_FILENAME


def _get_incluster_ca_file(ca_file: Optional[str] = None) -> str:
    return ca_file if ca_file is not None else SERVICE_CERT_FILENAME


def get_service_account_token() -> str:
    """Get token from service account token file."""
    try:
        with open(_get_incluster_token_file(), "r") as token_file:
            return token_file.read()
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            "Unable to get service account token, please check "
            "that service has service account assigned with exposed token"
        ) from exc


def to_camel_case(obj: T) -> T:
    """Convert dictionary keys to camelCase."""
    if isinstance(obj, dict):
        aux = dict()
        for key, value in obj.items():
            new_key = re.sub(r"(?<=.{1})_([a-z])", lambda m: f"{m.group(1).upper()}", key)
            aux[new_key] = to_camel_case(value)

        return aux  # type: ignore

    return obj


def to_snake_case(obj: T) -> T:
    """Convert dictionary keys to snake_case."""
    if isinstance(obj, dict):
        aux = dict()
        for key, value in obj.items():
            new_key = re.sub(r"(?<=.{1})([A-Z])", lambda m: f"_{m.group(0)}", key).lower()
            aux[new_key] = to_snake_case(value)

        return aux  # type: ignore

    return obj
