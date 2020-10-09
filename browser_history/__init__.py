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
    output_object = generic.Outputs()
    subclasses = generic.Browser.__subclasses__()
    for browser_class in subclasses:
        try:
            browser_object = browser_class()
            browser_output_object = browser_object.fetch()
            output_object.history_entries.extend(browser_output_object.get_history())
        except AssertionError:
            utils.logger.info("%s browser is not supported", browser_class.name)
    output_object.history_entries.sort()
    return output_object

def get_bookmarks():
    """This method is used to obtain browser bookmarks of all available and supported
    browsers for the system platform.

    :return: Object of class :py:class:`browser_history.generic.Outputs` with the
        data member bookmark_entries set to list(tuple(:py:class:`datetime.datetime`, str,str,str))

    :rtype: :py:class:`browser_history.generic.Outputs`
    """
    output_object = generic.Outputs()
    subclasses = generic.Browser.__subclasses__()
    for browser_class in subclasses:
        if('Firefox' in str(browser_class)):
            try:
                browser_object = browser_class()
                browser_output_object = browser_object.fetch(fetch_type='bookmarks')
                output_object.bookmark_entries.extend(browser_output_object.get_bookmarks())
            except AssertionError:
                utils.logger.info("%s browser is not supported", browser_class.name)
    output_object.bookmark_entries.sort()
    return output_object
