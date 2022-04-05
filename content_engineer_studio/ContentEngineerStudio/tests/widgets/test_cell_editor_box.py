import typing

import numpy as np
import pandas as pd
import pytest
from pandasgui.store import PandasGuiDataFrameStore
from pandasgui.widgets.dataframe_viewer import DataFrameViewer
from PyQt5 import QtCore, QtGui, QtWidgets

from ContentEngineerStudio.widgets.analysis_suite import AnalysisSuite
from ContentEngineerStudio.widgets.cell_editor_box import (
    AnalysisSelectorModel,
    CellEdit,
    CellEditorContainer,
)


# Sanity check
def test_model(qtmodeltester):
    model = QtGui.QStandardItemModel()
    items = [QtGui.QStandardItem(str(i)) for i in range(4)]
    model.setItem(0, 0, items[0])
    model.setItem(0, 1, items[1])
    model.setItem(1, 0, items[2])
    model.setItem(1, 1, items[3])
    qtmodeltester.check(model)


@pytest.fixture
def container(make_pgdf, qtbot):
    cell_editor_container = CellEditorContainer(parent=make_pgdf)
    qtbot.addWidget(cell_editor_container)
    return cell_editor_container


def test_can_make_df(make_df):
    assert isinstance(make_df, pd.DataFrame) == True


def test_can_make_pgdf(make_pgdf):
    assert isinstance(make_pgdf.pgdf, PandasGuiDataFrameStore) == True


def test_pgdf_can_add_viewer(make_pgdf):
    assert isinstance(make_pgdf.pgdf.dataframe_viewer, DataFrameViewer) == True


def test_header_model(qtmodeltester, make_pgdf):
    assert isinstance(make_pgdf, Suite)
    model = AnalysisSelectorModel(pgdf=make_pgdf.pgdf)
    qtmodeltester.check(model)


def test_can_populate_cell_selector(container):
    assert container.cell_selector.model().rowCount() == 0
    container.populate_cell_selector()
    assert container.cell_selector.model().rowCount() == 1


def test_populates_analysis_correctly(container):
    container.populate_cell_selector()
    assert container.cell_editor.toPlainText() == "Analysis populates correctly"


def test_can_handle_empty_strings(container):
    container.suite.row = 1
    container.populate_cell_selector()
    assert container.cell_editor.toPlainText() == ""


def test_can_handle_numbers(container):
    container.suite.row = 2
    container.populate_cell_selector()
    assert container.cell_editor.toPlainText() == "3"


def test_can_select_from_cell_selector_programmatically(container):
    container.populate_cell_selector()
    assert container.cell_editor.toPlainText() == "Analysis populates correctly"
    container.cell_selector.setCurrentIndex(1)
    assert container.cell_editor.toPlainText() == "switching is working"


def test_can_use_right_button(container):
    container.populate_cell_selector()
    assert container.cell_editor.toPlainText() == "Analysis populates correctly"
    container.btn_right()
    assert container.cell_editor.toPlainText() == "switching is working"


def test_can_use_left_button(container):
    container.populate_cell_selector()
    assert container.cell_editor.toPlainText() == "Analysis populates correctly"
    container.btn_right()
    assert container.cell_editor.toPlainText() == "switching is working"


def test_can_use_tab_to_activate_btn_right(container, qtbot):
    container.populate_cell_selector()
    assert container.cell_editor.toPlainText() == "Analysis populates correctly"
    qtbot.mouseClick(container.cell_editor, QtCore.Qt.LeftButton)
    qtbot.keyClick(container.cell_editor, QtCore.Qt.Key_Tab)
    assert container.cell_editor.toPlainText() == "switching is working"
