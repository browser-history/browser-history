from . import browsers, generic, utils  # noqa: F401

__version__ = "0.4.1"


def get_history():
    """This method is used to obtain browser histories of all available and
    supported browsers for the system platform.

    :return: Object of class :py:class:`browser_history.generic.Outputs` with
        the data member histories set to
        list(tuple(:py:class:`datetime.datetime`, str))

    :rtype: :py:class:`browser_history.generic.Outputs`
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
    # Can't sort tuples with None values, and some titles
    # are None, so replace them with ''
    output_object.histories.sort(key=lambda h: tuple(el or "" for el in h))
    return output_object


def get_bookmarks():
    """This method is used to obtain browser bookmarks of all available and
    supported browsers for the system platform.

    :return: Object of class :py:class:`browser_history.generic.Outputs` with
        the data member bookmarks set to
        list(tuple(:py:class:`datetime.datetime`, str, str, str))

    :rtype: :py:class:`browser_history.generic.Outputs`
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
        except AssertionError as e:
            utils.logger.info("%s", e)
    output_object.bookmarks.sort()
    return output_object
