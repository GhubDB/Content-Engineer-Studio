from dataclasses import dataclass
from enum import Enum, auto

import pandas as pd
from PyQt5 import QtCore, QtWidgets


class Data:

    # Sets the number of prebuffered windows for auto mode
    BUFFER = 2

    # Defines what window to show on startup
    START_INDEX = 3

    LIVECHAT_URL = "https://www.cleverbot.com/"

    ROLES = {
        "NONE": "None",
        "CUSTOMER": "Customer",
        "BOT": "Bot",
        "MULTI_CHOICE": "Multi-Choice",
        "EDITABLE": "Editable",
        "CORRECT_FAQ": "Correct FAQ",
        "LINK": "Link",
    }

    MULTIPLE_CHOICE = ["", "Ja", "Nein", "Teilweise"]

    EXAMPLE_FLOWS = ["Some flow", "Some other flow", "Example flow", "Some FAQ"]

    EXAMPLE_ACTIONS = [
        "Some action",
        "Some other action",
        "Example action",
        "Example FAQ",
    ]

    DEV = {"host": "localhost", "user": "developer", "password": "root"}


class GuiSignals(QtWidgets.QWidget):
    editing_done = QtCore.pyqtSignal()
    faq_search_selector_index_changed = QtCore.pyqtSignal(int)
