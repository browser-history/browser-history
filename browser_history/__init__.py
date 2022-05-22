"""A module to retrieve web browser history."""
from . import generic, utils

# needed to ensure that implemented browsers are recognized
from . import browsers  # noqa: F401


__version__ = "0.3.2"


def get_history() -> generic.Outputs:
    """Obtain browser history of all available and supported browsers.

    Returns:
        Object of class :py:class:`browser_history.generic.Outputs` with
        the data member histories set to
        list(tuple(:py:class:`datetime.datetime`, str)).
    """
    output_object = generic.Outputs(fetch_type="history")
    browser_classes = utils.get_browsers()
    for browser_class in browser_classes:
        try:
            browser_object = browser_class()
            browser_output_object = browser_object.fetch_history()
            output_object.histories.extend(browser_output_object.histories)
        except AssertionError:
            utils.logger.info("%s browser is not supported", browser_class.name)
    output_object.histories.sort()
    return output_object


def get_bookmarks() -> generic.Outputs:
    """Obtain browser bookmarks of all available and supported browsers.

    Returns:
        Object of class :py:class:`browser_history.generic.Outputs` with
        the data member bookmarks set to
        list(tuple(:py:class:`datetime.datetime`, str, str, str)).
    """
    output_object = generic.Outputs(fetch_type="bookmarks")
    subclasses = utils.get_browsers()
    for browser_class in subclasses:
        try:
            browser_object = browser_class()
            assert (
                browser_object.bookmarks_file is not None
            ), f"Bookmarks are not supported on {browser_class.name}"
            browser_output_object = browser_object.fetch_bookmarks()
            output_object.bookmarks.extend(browser_output_object.bookmarks)
        # TODO: use a more specific error
        # or is an exception even needed here?
        except AssertionError as e:
            utils.logger.info("%s", e)
    output_object.bookmarks.sort()
    return output_object
