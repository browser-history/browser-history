import inspect
import webbrowser

from . import browsers, generic, utils  # noqa: F401

if utils.get_platform() == utils.Platform.WINDOWS:
    from winreg import HKEY_CURRENT_USER, OpenKey, QueryValueEx  # type: ignore


__version__ = "0.3.0"


def get_browsers():
    """This method provides a list of all browsers implemented by
    browser_history.

    :return: A :py:class:`list` containing implemented browser classes
        all inheriting from the super class
        :py:class:`browser_history.generic.Browser`

    :rtype: :py:class:`list`
    """

    # recursively get all concrete subclasses
    def get_subclasses(browser):
        # include browser itself in return list if it is concrete
        sub_classes = []
        if not inspect.isabstract(browser):
            sub_classes.append(browser)

        for sub_class in browser.__subclasses__():
            sub_classes.extend(get_subclasses(sub_class))
        return sub_classes

    return get_subclasses(generic.Browser)


def get_history():
    """This method is used to obtain browser histories of all available and
    supported browsers for the system platform.

    :return: Object of class :py:class:`browser_history.generic.Outputs` with
        the data member histories set to
        list(tuple(:py:class:`datetime.datetime`, str))

    :rtype: :py:class:`browser_history.generic.Outputs`
    """
    output_object = generic.Outputs(fetch_type="history")
    browser_classes = get_browsers()
    for browser_class in browser_classes:
        try:
            browser_object = browser_class()
            browser_output_object = browser_object.fetch_history()
            output_object.histories.extend(browser_output_object.histories)
        except AssertionError:
            utils.logger.info("%s browser is not supported", browser_class.name)
    output_object.histories.sort()
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
    subclasses = get_browsers()
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


def default_browser():
    """This method gets the default browser of the current platform

    :return: A :py:class:`browsers.Browser` object representing the default
        browser in the current platform. If platform is not supported or
        default browser is unknown or unsupported ``None`` is returned

    :rtype: union[:py:class:`browsers.Browser`, None]
    """
    plat = utils.get_platform()

    # ---- get default from specific platform ----

    # Always try to return a lower-cased value for ease of comparison
    if plat == utils.Platform.LINUX:
        default = webbrowser.get().name.lower()
    elif plat == utils.Platform.WINDOWS:
        reg_path = (
            "Software\\Microsoft\\Windows\\Shell\\Associations\\"
            "UrlAssociations\\https\\UserChoice"
        )
        with OpenKey(HKEY_CURRENT_USER, reg_path) as key:
            default = QueryValueEx(key, "ProgId")[0].lower()
    else:
        utils.logger.warning("Default browser feature not supported on this OS")
        return None

    # ---- convert obtained default to something we understand ----
    all_browsers = get_browsers()

    # first quick pass for direct matches
    for browser in all_browsers:
        if default == browser.name.lower() or default in browser.aliases:
            return browser

    # separate pass for deeper matches
    for browser in all_browsers:
        # look for alias matches even if the default name has "noise"
        # for instance firefox on windows returns something like
        # "firefoxurl-3EEDF34567DDE" but we only need "firefoxurl"
        for alias in browser.aliases:
            if alias in default:
                return browser

    # nothing was found
    utils.logger.warning("Current default browser is not supported")
    return None
