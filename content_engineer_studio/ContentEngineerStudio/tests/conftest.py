import typing
from time import sleep
from unittest import mock

import numpy as np
import pandas as pd
import pytest
from pandasgui.store import PandasGuiDataFrameStore
from pandasgui.widgets.dataframe_viewer import HeaderModel
from PyQt5 import QtCore, QtGui, QtWidgets


@pytest.fixture
def pgdf():
    df = pd.DataFrame(
        np.random.randint(low=0, high=10, size=(5, 5)),
        columns=["a", "b", "c", "d", "e"],
    )
    pgdf = PandasGuiDataFrameStore(df, "Test_dummy")
    return pgdf
