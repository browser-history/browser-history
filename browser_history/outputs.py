"""Class to store history, bookmarks, etc. outputs."""

import abc
import csv
import datetime
import json
import os
from collections import defaultdict
from functools import partial
from io import StringIO
from typing import (
    Any,
    Callable,
    DefaultDict,
    Dict,
    Generic,
    List,
    Optional,
    Tuple,
    TypeVar,
)
from urllib.parse import urlparse

T = TypeVar("T", bound=Tuple)


class Outputs(abc.ABC, Generic[T]):
    """Base class for storing outputs, provides helpers for conversion."""

    def __init__(self):
        """Initialize Outputs with no data."""
        # TODO: take data as input here and make it private

        self.data: List[T] = []
        """List of all history/bookmarks/whatever data."""

    @staticmethod
    @abc.abstractmethod
    def _fetch_type() -> str:
        """Name for the type of data this class is expected to store."""
        ...

    @staticmethod
    @abc.abstractmethod
    def _fields() -> Tuple[str, ...]:
        ...

    def group_by_domain(self) -> Dict[str, List[T]]:
        """Return the history/bookamarks sorted according to the domain-name.

        Examples:
            .. testsetup:: *

                import datetime
                from browser_history import generic
                entries = [
                    [datetime.datetime(2020, 1, 1), 'https://google.com'],
                    [datetime.datetime(2020, 1, 1), 'https://google.com/imghp?hl=EN'],
                    [datetime.datetime(2020, 1, 1), 'https://example.com'],
                ]
                history_outputs = generic.HistoryOutputs()
                history_outputs.data = entries

            Example of a return value:

                >>> history_outputs.group_by_domain() == {
                ...     'google.com': [
                ...         [datetime.datetime(2020, 1, 1, 0, 0), 'https://google.com'],
                ...         [datetime.datetime(2020, 1, 1, 0, 0), 'https://google.com/imghp?hl=EN']
                ...     ],
                ...     'example.com': [
                ...         [datetime.datetime(2020, 1, 1, 0, 0), 'https://example.com']
                ...     ]
                ... }
                True
        """  # noqa: E501
        domain_histories: DefaultDict[Any, List[T]] = defaultdict(list)
        for entry in self.data:
            domain_histories[urlparse(entry[1]).netloc].append(entry)
        return dict(domain_histories)

    def formatted(self, output_format: str = "csv") -> str:
        """Return history or bookmarks formatted as ``output_format``.

        Args:
            output_format: One of {}.
        """
        # convert to lower case since the formats tuple is enforced in
        # lowercase
        output_format = output_format.lower()
        if output_format in self._format_map:
            # fetch the required formatter and call it. The formatters are
            # instance methods so no need to pass any arguments
            formatter = self._format_map[output_format]
            return formatter(self)
        raise ValueError(
            f"Invalid format {output_format}. Should be one of \
            {self._format_map.keys()}"
        )

    def to_csv(self) -> str:
        """Return history or bookmarks formatted as a comma separated string.

        The first row has the fields names.

        Examples:
            .. testsetup:: *

                import datetime
                from browser_history import generic
                entries = [
                    [datetime.datetime(2020, 1, 1), 'https://google.com'],
                    [datetime.datetime(2020, 1, 1), 'https://google.com/imghp?hl=EN'],
                    [datetime.datetime(2020, 1, 1), 'https://example.com'],
                ]
                history_outputs = generic.HistoryOutputs()
                history_outputs.data = entries

            Example of a return value:

                >>> print(history_outputs.to_csv()) # doctest: +NORMALIZE_WHITESPACE
                Timestamp,URL
                2020-01-01 00:00:00,https://google.com
                2020-01-01 00:00:00,https://google.com/imghp?hl=EN
                2020-01-01 00:00:00,https://example.com
                <BLANKLINE>
        """
        # we will use csv module and let it do all the heavy lifting such as
        # special character escaping and correct line termination escape
        # sequences
        # The catch is, we need to return a string but the csv module only
        # works with files so we will use StringIO to build the csv in
        # memory first
        with StringIO() as output:
            writer = csv.writer(output)
            writer.writerow(self._fields())
            for row in self.data:
                writer.writerow(row)
            return output.getvalue()

    def to_json(self, json_lines: bool = False) -> str:
        """Return history or bookmarks formatted as a JSON or JSON Lines.

        Args:
            json_lines: whether JSON lines format should be used instead of JSON.

        Examples:
            .. testsetup:: *

                import datetime
                from browser_history import generic
                entries = [
                    [datetime.datetime(2020, 1, 1), 'https://google.com'],
                    [datetime.datetime(2020, 1, 1), 'https://google.com/imghp?hl=EN'],
                    [datetime.datetime(2020, 1, 1), 'https://example.com'],
                ]
                history_outputs = generic.HistoryOutputs()
                history_outputs.data = entries

            Example of a return value:

                >>> print(history_outputs.to_json()) # doctest: +NORMALIZE_WHITESPACE
                {
                    "history": [
                        {
                            "Timestamp": "2020-01-01T00:00:00",
                            "URL": "https://google.com"
                        },
                        {
                            "Timestamp": "2020-01-01T00:00:00",
                            "URL": "https://google.com/imghp?hl=EN"
                        },
                        {
                            "Timestamp": "2020-01-01T00:00:00",
                            "URL": "https://example.com"
                        }
                    ]
                }
        """
        # custom json encoder for datetime objects
        class DateTimeEncoder(json.JSONEncoder):
            """Custom JSON encoder to encode datetime objects."""

            # Override the default method
            def default(self, o):
                if isinstance(o, (datetime.date, datetime.datetime)):
                    return o.isoformat()
                # skip coverage for this line (tested but not detected)
                return super().default(o)  # pragma: no cover

        # fetch lines
        lines = []
        for entry in self.data:
            json_record = {}
            for field, value in zip(self._fields(), entry):
                json_record[field] = value
            lines.append(json_record)

        if json_lines:
            json_string = "\n".join(
                [json.dumps(line, cls=DateTimeEncoder) for line in lines]
            )
        else:
            json_string = json.dumps(
                {self._fetch_type(): lines}, cls=DateTimeEncoder, indent=4
            )

        return json_string

    def save(self, filename: str, output_format: Optional[str] = None):
        """Save history or bookmarks to a file.

        Infers the type from the given filename extension.
        If the type could not be inferred, it defaults to ``csv``.

        Args:
            filename: the name of the file.
            output_format: One of {}.
                If not given, it will automatically be inferred from the file's
                extension.
        """
        if output_format is None:
            output_format = os.path.splitext(filename)[1][1:]
            if output_format not in self._format_map:
                raise ValueError(
                    f"Invalid extension .{output_format}. Should be one of "
                    f"{', '.join(self._format_map.keys())}"
                )

        with open(filename, "w") as out_file:
            out_file.write(self.formatted(output_format))

    _format_map: Dict[str, Callable[["Outputs[T]"], str]] = {
        "csv": to_csv,
        "json": to_json,
        "jsonl": partial(to_json, json_lines=True),
    }


Outputs.formatted.__doc__ = (Outputs.formatted.__doc__ or "").format(
    ", ".join(Outputs._format_map.keys())
)
Outputs.save.__doc__ = (Outputs.save.__doc__ or "").format(
    ", ".join(Outputs._format_map.keys())
)


class HistoryOutputs(Outputs[Tuple[datetime.datetime, str]]):
    """Encapsulates history output with methods for conversion and extraction."""

    # TODO: document the fields in some docstring - their names

    @staticmethod
    def _fields() -> Tuple[str, str]:
        return ("Timestamp", "URL")

    @staticmethod
    def _fetch_type() -> str:
        return "history"

    @property
    def histories(self):
        """List of history data."""
        return self.data


class BookmarksOutputs(Outputs[Tuple[datetime.datetime, str, str, str]]):
    """Encapsulates bookmarks output with methods for conversion and extraction."""

    @staticmethod
    def _fields() -> Tuple[str, str, str, str]:
        return ("Timestamp", "URL", "Title", "Folder")

    @staticmethod
    def _fetch_type() -> str:
        return "bookmarks"

    @property
    def bookmarks(self):
        """List of bookmarks data."""
        return self.data
