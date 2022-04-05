import os
import typing
from time import sleep
from unittest import mock

import numpy as np
import pandas as pd
import pytest
from pandasgui.store import PandasGuiDataFrameStore
from pandasgui.widgets.dataframe_viewer import DataFrameViewer, HeaderModel
from PyQt5 import QtCore, QtGui, QtWidgets


# This sets the working dir for pytest to be the same as the dir the test is in
@pytest.fixture
def change_test_dir(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)


class Suite(QtWidgets.QWidget):
    def __init__(self, pgdf):
        super().__init__()
        self.pgdf = pgdf
        self.viewer = DataFrameViewer(pgdf=pgdf)
        self.row = 0


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
    helper = Suite(pgdf=PandasGuiDataFrameStore(df, "Test_dummy"))
    qtbot.addWidget(helper)
    return helper
