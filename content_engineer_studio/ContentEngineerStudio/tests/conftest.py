import os
import typing
from time import sleep
from unittest import mock

import numpy as np
import pandas as pd
import pytest
from pandasgui.store import PandasGuiDataFrameStore
from pandasgui.widgets.dataframe_viewer import HeaderModel
from PyQt5 import QtCore, QtGui, QtWidgets


# This sets the working dir for pytest to be the same as the dir the test is in
@pytest.fixture
def change_test_dir(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)


# @pytest.fixture
# def change_test_dir_old(request):
#     os.chdir(request.fspath.dirname)
#     yield
#     os.chdir(request.config.invocation_dir)
