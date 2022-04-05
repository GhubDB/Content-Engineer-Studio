import typing

import numpy as np
import pandas as pd
import pytest
from pandasgui.store import PandasGuiDataFrameStore
from pandasgui.widgets.dataframe_viewer import HeaderModel
from PyQt5 import QtCore, QtGui, QtWidgets

from ContentEngineerStudio.main import MainWindow
from ContentEngineerStudio.utils.stylesheets import Stylesheets
from ContentEngineerStudio.widgets.analysis_suite import AnalysisSuite
from ContentEngineerStudio.widgets.chat_widget import (
    AddVariant,
    ChatWidgetContainer,
    TextEdit,
)
from ContentEngineerStudio.widgets.testing_suite import TestingSuite


@pytest.fixture
def container(qtbot):
    container = ChatWidgetContainer()
    container.populate_chat_analysis(
        chat=[
            ["bot", "Hello there!"],
            ["customer", "hi"],
            ["customer", "My phonenumber is 0762211224."],
            ["customer", "My email is me@example.com."],
        ]
    )
    qtbot.addWidget(container)
    return container


def test_assigns_participants_correctly(container, qtbot):
    assert container.chat.cellWidget(0, 0).participant == "bot"
    assert container.chat.cellWidget(1, 0).participant == "customer"


def test_can_call_populate_chat_analysis(container, qtbot):
    textedit = container.chat.cellWidget(0, 0)
    assert textedit.toPlainText() == "Hello there!"


def test_can_get_chat_text(container, qtbot):
    container.chat.cellWidget(0, 0).selected = True
    container.chat.cellWidget(1, 0).selected = True
    customer, bot = container.get_chat_text()
    assert customer == "hi"
    assert bot == "Hello there!"


def test_anonymizes_phone_numbers_correctly(container, qtbot):
    container.chat.cellWidget(2, 0).selected = True
    customer, bot = container.get_chat_text()
    assert customer == "My phonenumber is ***."


def test_anonymizes_email_correctly(container, qtbot):
    container.chat.cellWidget(3, 0).selected = True
    customer, bot = container.get_chat_text()
    assert customer == "My email is ***"


def test_can_clear_chat(container, qtbot):
    container.clear_chat()
    assert container.chat.rowCount() == 0


def test_handles_no_input(container, qtbot):
    customer, bot = container.get_chat_text()
    assert customer == False
    assert bot == False


@pytest.fixture
def setup_text_edit(qtbot):
    edit = TextEdit(objectName="test_textedit", participant="bot", index=0)
    qtbot.addWidget(edit)
    return edit


# def test_can_rightclick_select_text_edit(setup_text_edit, qtbot):
#     setup_text_edit.show()
#     qtbot.waitForWindowShown(setup_text_edit)
#     qtbot.mouseClick(setup_text_edit, QtCore.Qt.RightButton)
#     qtbot.mouseClick(setup_text_edit, QtCore.Qt.RightButton)
#     assert setup_text_edit.selected == True


# def test_can_rightclick_select_text_edit(container, qtbot):
#     """
#     https://stackoverflow.com/questions/68856455
#     """

#     container.show()
#     qtbot.waitForWindowShown(container)
#     container.populate_chat_analysis(chat=[["bot", "Hello there!"]])
#     item = container.chat.item(0, 0)
#     QtWidgets.QApplication.instance().processEvents()
#     assert item is not None
#     rect = container.chat.visualItemRect(item)
#     qtbot.mouseClick(
#         container.chat.viewport(),
#         QtCore.Qt.RightButton,
#         pos=rect.center(),
#     )
#     editor = container.chat.cellWidget(0, 0)
#     assert editor.selected == True


# def test_can_middleclick_to_add_variant(make_test_textedit, qtbot):
#     qtbot.mouseClick(make_test_textedit, QtCore.Qt.MiddleButton)
#     assert isinstance(make_test_textedit.new_variant, AddVariant) == True
