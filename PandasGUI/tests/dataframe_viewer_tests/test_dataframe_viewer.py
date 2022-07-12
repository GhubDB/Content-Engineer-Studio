import typing
import pandas as pd
import numpy as np
import pytest
from PyQt5 import QtWidgets

from pandasgui.store import (
    PandasGuiDataFrameStore,
)
from pandasgui.widgets.dataframe_viewer import (
    HeaderModel,
)
from ContentEngineerStudio.main import MainWindow


class TestDummyWidget(QtWidgets.QWidget):
    def __init__(
        self,
        pgdf: PandasGuiDataFrameStore,
        parent: typing.Optional[QtWidgets.QWidget] = ...,
    ) -> None:
        super().__init__(parent)
        self.pgdf = pgdf


@pytest.fixture
def setUp():
    df = pd.DataFrame(
        np.random.randint(low=0, high=10, size=(5, 5)),
        columns=["a", "b", "c", "d", "e"],
    )
    pgdf = PandasGuiDataFrameStore(df, "Test_dummy")
    return pgdf


def init_test_dummy(setUp, qtbot):
    tdw = TestDummyWidget(pgdf=setUp, parent=None)
    qtbot.addWidget(tdw)


def test_header_model(qtmodeltester, setUp, init_test_dummy):
    model = HeaderModel(init_test_dummy)
    qtmodeltester.check(model)


# def test_can_edit_data(setUp):
# original_value = setUp.df_unfiltered.loc[0, "a"]
# assert original_value == 7
# assert 1 == 2


# def test_testit():
#     assert 1 == 1
