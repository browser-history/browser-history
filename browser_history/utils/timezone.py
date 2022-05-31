"""Timezone related utilities."""

from typing import cast
from datetime import datetime, tzinfo


def local_tz() -> tzinfo:
    """Retrieve a :py:class:`tzinfo` representing the local system timezone."""
    return cast(tzinfo, datetime.now().astimezone().tzinfo)
