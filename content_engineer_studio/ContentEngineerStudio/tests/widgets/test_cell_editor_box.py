import typing

import numpy as np
import pandas as pd
import pytest
from pandasgui.store import PandasGuiDataFrameStore
from PyQt5 import QtCore, QtGui, QtWidgets

from ContentEngineerStudio.widgets.analysis_suite import AnalysisSuite
from ContentEngineerStudio.widgets.cell_editor_box import (
    AnalysisSelectorModel,
    CellEdit,
    CellEditorContainer,
)


class Container(QtWidgets.QWidget):
    def __init__(self, pgdf):
        super().__init__()
        self.pgdf = pgdf


@pytest.fixture
def make_df(change_test_dir):
    df = pd.read_excel(
        io="test.xlsx",
        sheet_name="Sheet1",
        header=[0, 1],
    )
    return df


@pytest.fixture
def make_pgdf(qtbot, change_test_dir):
    df = pd.read_excel(
        io="test.xlsx",
        sheet_name="Sheet1",
        header=[0, 1],
    )
    container = Container(pgdf=PandasGuiDataFrameStore(df, "Test_dummy"))
    qtbot.addWidget(container)
    return container


def test_can_make_df(make_df):
    assert isinstance(make_df, pd.DataFrame) == True


# Sanity check
def test_model(qtmodeltester):
    model = QtGui.QStandardItemModel()
    items = [QtGui.QStandardItem(str(i)) for i in range(4)]
    model.setItem(0, 0, items[0])
    model.setItem(0, 1, items[1])
    model.setItem(1, 0, items[2])
    model.setItem(1, 1, items[3])
    qtmodeltester.check(model)


def test_header_model(qtmodeltester, make_pgdf):
    assert isinstance(make_pgdf, Container)
    model = AnalysisSelectorModel(pgdf=make_pgdf.pgdf)
    qtmodeltester.check(model)


# df = pd.read_excel(
#     io="test.xlsx",
#     sheet_name="Sheet1",
#     header=[0, 1],
# )
# print(df)


# def make_pgdf_x():
#     df = pd.read_excel(
#         io="test.xlsx",
#         sheet_name="Sheet1",
#         header=[0, 1],
#     )
#     return PandasGuiDataFrameStore(df, "Test_dummy")


# print(make_pgdf_x())
