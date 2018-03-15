# Standard imports...
from Orange.widgets import widget, gui
from Orange.widgets.settings import Setting

__version__ = "0.01"


class LexicalHunter(widget.OWWidget):
    """An Orange widget that allows addition, substraction and
    multiplication of two numbers"""

    #----------------------------------------------------------------------
    # Widget's metadata...

    name = "LexicalHunter"
    description = "Search a segment for lists of words"
    icon = "icons/mywidget.svg"
    priority = 100

    #----------------------------------------------------------------------
    # Channel definitions...

    inputs = []
    outputs = []

    #----------------------------------------------------------------------
    # GUI layout parameters...

    want_main_area = False
    resizing_enabled = False

    def __init__(self):
        super().__init__()


    #----------------------------------------------------------------------
    # User interface...



# The following code lets you execute the code outside of Orange (to view the
# resulting interface)...
if __name__ == "__main__":
    from PyQt4.QtGui import QApplication
    import sys
    my_app = QApplication(list(sys.argv))
    my_widget = LexicalHunter()
    my_widget.show()
    my_widget.raise_()
    my_app.exec_()
