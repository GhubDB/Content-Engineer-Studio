import pandas as pd
import numpy as np
import pytest

from pandasgui.store import (
    PandasGuiDataFrameStore,
)
from pandasgui.widgets.dataframe_viewer import (
    HeaderModel,
)
from main import MainWindow

# class TestPandasGuiDataFrameStore:


@pytest.fixture
def setUp(qtbot):
    # df = pd.DataFrame(
    #     np.random.randint(low=0, high=10, size=(5, 5)),
    #     columns=["a", "b", "c", "d", "e"],
    # )
    # pgdf = PandasGuiDataFrameStore(df, "Test_dummy")
    mw = MainWindow()
    qtbot.addWidget(mw)
    # print(pgdf.df_unfiltered)
    return mw


def test_header_model(qtmodeltester):
    model = HeaderModel()
    qtmodeltester.check(model)


# def test_can_edit_data(setUp):
# original_value = setUp.df_unfiltered.loc[0, "a"]
# assert original_value == 7
# assert 1 == 2


# def test_testit():
#     assert 1 == 1
