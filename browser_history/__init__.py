from . import generic
from . import browsers
from . import utils


def get_history():
    """This method is used to obtain browser histories of all available and supported
    browsers for the system platform.

    :return: Object of class :py:class:`browser_history.generic.Outputs` with the
        data member entries set to list(tuple(:py:class:`datetime.datetime`, str))

    :rtype: :py:class:`browser_history.generic.Outputs`
    """
    output_object = generic.Outputs(fetch_type="history")
    subclasses = generic.Browser.__subclasses__()
    for browser_class in subclasses:
        try:
            browser_object = browser_class()
            browser_output_object = browser_object.fetch_history()
            output_object.histories.extend(browser_output_object.histories)
        except AssertionError:
            utils.logger.info("%s browser is not supported", browser_class.name)
    output_object.histories.sort()
    return output_object


def get_bookmarks():
    """This method is used to obtain browser bookmarks of all available and supported
    browsers for the system platform.

    :return: Object of class :py:class:`browser_history.generic.Outputs` with the
        data member bookmark_entries set to list(tuple(:py:class:`datetime.datetime`, str,str,str))

    :rtype: :py:class:`browser_history.generic.Outputs`
    """
    output_object = generic.Outputs(fetch_type="bookmarks")
    subclasses = generic.Browser.__subclasses__()
    for browser_class in subclasses:
        try:
            browser_object = browser_class()
            assert browser_object.bookmarks_file is not None
            browser_output_object = browser_object.fetch_bookmarks()
            output_object.bookmarks.extend(browser_output_object.bookmarks)
        except AssertionError:
            utils.logger.info(
                "%s browser is not supported for bookmarks", browser_class.name
            )
    output_object.bookmarks.sort()
    return output_object
