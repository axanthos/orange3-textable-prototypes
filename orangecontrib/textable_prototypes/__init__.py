import sysconfig

WIDGET_HELP_PATH = (
    ("{DEVELOP_ROOT}/doc/_build/index.html", None),

    # Documentation included in wheel
    # Correct DATA_FILES entry is needed in setup.py and documentation has to be built
    # before the wheel is created.
    ("{}/help/orange3-textable-prototypes/index.html".format(sysconfig.get_path("data")), None),

    # Online documentation url, used when the local documentation is not available.
    # Url should point to a page with a section Widgets. This section should
    # includes links to documentation pages of each widget. Matching is
    # performed by comparing link caption to widget name.
    ("http://orange3-textable-prototypes.readthedocs.io/en/latest/index.html", "")

)