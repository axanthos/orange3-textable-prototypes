"""
Widget poetica by LOLS
"""

# Import the necessary packages...
from Orange.widgets import widget, gui, utils

# Informations...
__version__ = "0.01"


# Create the poetica class...
class poetica(widget.OWWidget):
    """
    This is the poetica class
    """

    # Widget's metadata...
    name = "Poetica"
    description = "Poetica's poems importation"
#    icon = ""
    priority = 20

    # Channel definitions...
    inputs = []
    outputs = [("Poetica's poems importation", str)]

    # Gui layout parameters...
    want_main_area = False
    resizing_enabled = False

    # Define the init function...
    def __init__(self):
        """
        This is the init function
        """

# ETC.




if __name__ == "__main__" :
#    ...
