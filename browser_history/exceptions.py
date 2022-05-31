"""Exceptions used in browser-history."""


class BookmarksNotSupportedError(Exception):
    """Indicates that bookmarks are not supported for this browser."""

    def __init__(self, browser_name: str, *args: object) -> None:
        """Initialize a BookmarksNotSupportedError.

        Args:
            browser_name: name of browser in which this exception was triggered.
        """
        super().__init__(f"Bookmarks are not yet supported for: {browser_name}", *args)
        self.browser_name = browser_name
