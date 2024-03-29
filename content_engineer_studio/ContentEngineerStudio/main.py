# PandasGUI imports
import logging
import sys
from dataclasses import dataclass
from typing import Callable, List, Optional, Union

import numpy as np
import pandas as pd
# Pandasgui needs to be pip -e <filepath> installed for development mode
import pandasgui
import pkg_resources
import qtstylish
from IPython.core.magic import register_line_magic
from pandasgui.store import PandasGuiStore
from pandasgui.utility import as_dict, fix_ipython
from pandasgui.widgets.find_toolbar import FindToolbar
from pandasgui.widgets.json_viewer import JsonViewer
from pandasgui.widgets.navigator import Navigator
from pandasgui.widgets.settings_editor import SettingsEditor
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSortFilterProxyModel, Qt, QThreadPool
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QApplication, QGridLayout, QMainWindow, QWidget

from ContentEngineerStudio.data.data_variables import Data, GuiSignals
from ContentEngineerStudio.utils.excel_helpers import Excel
from ContentEngineerStudio.utils.stylesheets import Stylesheets
from ContentEngineerStudio.widgets.analysis_suite import AnalysisSuite
from ContentEngineerStudio.widgets.drag_drop import DragDrop
from ContentEngineerStudio.widgets.faq_search_tab import FaqSearchTabContainer
from ContentEngineerStudio.widgets.testing_suite import TestingSuite


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.analysis_df_name = None
        self.testing_df_name = None
        self.current_work_area = 0

        self.load_excel_sheets()

        self.threadpool = QThreadPool()
        self.signals = GuiSignals()

        self.setup_ui()
        self.setup_main_components()
        self.setup_menubar()
        self.setStyleSheet(Stylesheets.custom_dark)

        self.central_stacked_widget.currentChanged.connect(self.workingView)

        """
        Start PandasGUI init
        Provides a viewer and editor for dataframes
        https://github.com/adrotog/PandasGUI
        """
        logger = logging.getLogger(__name__)

        def except_hook(cls, exception, traceback):
            sys.__excepthook__(cls, exception, traceback)

        # Set the exception hook to our wrapping function
        sys.excepthook = except_hook

        # Keep a list of widgets so they don't get garbage collected
        self.refs = []

        self.navigator = None
        self.splitter = None
        self.find_bar = None
        self.code_history_viewer = None

        self.refs.append(self)

        self.store = PandasGuiStore()
        self.store.gui = self

        self.add_user_provided_settings_to_data_store()
        self.create_all_widgets()
        self.add_pandasgui_to_main_window()
        self.add_find_toolbar()
        self.add_dataframes()
        self.add_menu_bar()
        self.apply_settings()

        # Signals
        self.store.settings.settingsChanged.connect(self.apply_settings)

        # Default to first item
        self.navigator.setCurrentItem(self.navigator.topLevelItem(0))


    def add_user_provided_settings_to_data_store(self):
        settings = {}
        for key, value in settings.items():
            setting = self.store.settings[key]
            setting.value = value

    def create_all_widgets(self):
        # This adds the drag_drop area for testing/analysis dataframes
        self.drag_drop = DragDrop(self)

        # This holds the DataFrameExplorer for each DataFrame
        self.stacked_widget = QtWidgets.QStackedWidget()

        self.drag_drop_splitter = QtWidgets.QSplitter(Qt.Vertical)
        self.navigator = Navigator(self.store)

        # Make splitter to hold nav and DataFrameExplorers
        self.pandasgui_splitter = QtWidgets.QSplitter(Qt.Horizontal)
        self.pandasgui_splitter.addWidget(self.drag_drop_splitter)
        self.drag_drop_splitter.addWidget(self.drag_drop)
        self.drag_drop_splitter.addWidget(self.navigator)
        self.pandasgui_splitter.addWidget(self.stacked_widget)
        self.pandasgui_splitter.setStretchFactor(0, 1)

    def add_pandasgui_to_main_window(self):
        self.pandasgui_container = QWidget()
        self.pandasgui_grid = QGridLayout(self.pandasgui_container)
        self.pandasgui_grid.setContentsMargins(0, 0, 0, 0)
        self.pandasgui_grid.addWidget(self.pandasgui_splitter, 0, 0, 0, 0)
        self.central_stacked_widget.addWidget(self.pandasgui_container)
        self.central_stacked_widget.setCurrentIndex(Data.START_INDEX)

    def add_find_toolbar(self):
        self.find_bar = FindToolbar(self)
        self.addToolBar(self.find_bar)

    def add_dataframes(self):
        dataframe_kwargs = {"Analysis": self.df, "Testing": self.df_2}
        for df_name, df in dataframe_kwargs.items():
            self.store.add_dataframe(df, df_name)

    def add_menu_bar(self):
        @dataclass
        class MenuItem:
            name: str
            func: Callable
            shortcut: str = ""

        items = {
            "Switch View": [
                MenuItem(
                    name="Analysis",
                    func=lambda: self.central_stacked_widget.setCurrentWidget(
                        self.analysis_suite
                    ),
                ),
                MenuItem(
                    name="Testing",
                    func=lambda: self.central_stacked_widget.setCurrentWidget(
                        self.testing_suite
                    ),
                ),
                MenuItem(
                    name="FAQ",
                    func=lambda: self.central_stacked_widget.setCurrentWidget(
                        self.faq_search_tab
                    ),
                ),
                MenuItem(
                    name="Dataframe Viewer",
                    func=lambda: self.central_stacked_widget.setCurrentWidget(
                        self.pandasgui_container
                    ),
                ),
            ],
            "Edit": [
                MenuItem(
                    name="Find", func=self.find_bar.show_find_bar, shortcut="Ctrl+F"
                ),
                MenuItem(name="Import", func=self.import_dialog),
                MenuItem(name="Import From Clipboard", func=self.import_from_clipboard),
                MenuItem(name="Export", func=self.export_dialog),
                MenuItem(name="Code Export", func=self.show_code_export),
            ],
            "DataFrame": [
                MenuItem(
                    name="Delete Selected DataFrames",
                    func=self.delete_selected_dataframes,
                ),
                MenuItem(
                    name="Reload DataFrames", func=self.reload_data, shortcut="Ctrl+R"
                ),
                MenuItem(
                    name="Parse All Dates",
                    func=lambda: self.store.selected_pgdf.parse_all_dates(),
                ),
            ],
            "Settings": [
                MenuItem(name="Preferences...", func=self.edit_settings),
            ],
            "Debug": [
                MenuItem(name="About", func=self.about),
                MenuItem(name="Browse Sample Datasets", func=self.show_sample_datasets),
                MenuItem(name="View PandasGuiStore", func=self.view_store),
                MenuItem(name="View DataFrame History", func=self.view_history),
            ],
        }

        self.add_menus(items, self.menubar)

    def add_menus(self, dic, root):
        # Add menu items and actions to UI using the schema defined above
        for menu_name in dic.keys():
            menu = root.addMenu(menu_name)
            for x in dic[menu_name]:
                if type(x) == dict:
                    self.add_menus(x, menu)
                else:
                    action = QtWidgets.QAction(x.name, self)
                    action.setShortcut(x.shortcut)
                    action.triggered.connect(x.func)
                    menu.addAction(action)

    def apply_settings(self):
        theme = self.store.settings.theme.value
        if theme == "classic":
            self.setStyleSheet("")
            self.store.settings.theme.value = "classic"
        elif theme == "dark":
            self.setStyleSheet(qtstylish.dark())
            self.store.settings.theme.value = "dark"
        elif theme == "light":
            self.setStyleSheet(qtstylish.light())
            self.store.settings.theme.value = "light"

    def show_code_export(self):
        self.store.selected_pgdf.dataframe_explorer.code_history_viewer.show()

    def update_code_export(self):
        self.store.selected_pgdf.dataframe_explorer.code_history_viewer.refresh()

    def delete_selected_dataframes(self):
        for name in [item.text(0) for item in self.navigator.selectedItems()]:
            self.store.remove_dataframe(name)

    def reorder_columns(self):
        self.store.selected_pgdf

    def view_history(self):
        d = self.store.selected_pgdf.history
        self.viewer = JsonViewer(d)
        self.viewer.show()

    def view_store(self):
        d = as_dict(self.store)
        self.viewer = JsonViewer(d)
        self.viewer.show()

    def get_dataframes(self, names: Union[None, str, list] = None):
        # Return all DataFrames, or a subset specified by names.
        # Returns a dict of name:df or a single df if there's only 1
        return self.store.get_dataframes(names)

    def __getitem__(self, key):
        return self.get_dataframes(key)

    def import_dialog(self):
        dialog = QtWidgets.QFileDialog()
        paths, _ = dialog.getOpenFileNames(filter="*.csv *.xlsx *.parquet *.json")
        for path in paths:
            self.store.import_file(path)

    def export_dialog(self):
        dialog = QtWidgets.QFileDialog()
        pgdf = self.store.selected_pgdf
        path, _ = dialog.getSaveFileName(directory=pgdf.name, filter="*.csv")
        if path:
            pgdf.df.to_csv(path, index=False)

    def import_from_clipboard(self):
        df = pd.read_clipboard(
            sep=",|\t",
            engine="python",
            na_values='""',  # https://stackoverflow.com/a/67915100/3620725
            skip_blank_lines=False,
        )
        self.store.add_dataframe(df)

    def edit_settings(self):

        dialog = QtWidgets.QDialog(self)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(SettingsEditor(self.store.settings))
        dialog.setLayout(layout)
        dialog.resize(700, 800)
        dialog.show()

    def about(self):
        import pandasgui

        dialog = QtWidgets.QDialog(self)
        layout = QtWidgets.QVBoxLayout()
        dialog.setLayout(layout)
        layout.addWidget(QtWidgets.QLabel(f"Version: {pandasgui.__version__}"))
        layout.addWidget(
            QtWidgets.QLabel(
                f"""GitHub: <a style="color: #1e81cc;"
            href="https://github.com/adamerose/PandasGUI">https://github.com/adamerose/PandasGUI</a>"""
            )
        )
        # dialog.resize(500, 500)
        dialog.setWindowTitle("About")
        dialog.show()

    def show_sample_datasets(self):
        import os

        from pandasgui.datasets import LOCAL_DATASET_DIR

        os.startfile(LOCAL_DATASET_DIR, "explore")

    def closeEvent(self, e: QtGui.QCloseEvent) -> None:
        self.refs.remove(self)
        super().closeEvent(e)

    # Replace all GUI DataFrames with the current DataFrame of the same name from the scope show was called
    def reload_data(self):
        callers_local_vars = self.caller_stack.f_locals.items()
        refreshed_names = []
        for var_name, var_val in callers_local_vars:
            for ix, name in enumerate([pgdf.name for pgdf in self.store.data.values()]):
                if var_name == name:
                    none_found_flag = False
                    self.store.remove_dataframe(var_name)
                    self.store.add_dataframe(var_val, name=var_name)
                    refreshed_names.append(var_name)

        if not refreshed_names:
            print("No matching DataFrames found to reload")
        else:
            print(f"Refreshed {', '.join(refreshed_names)}")

    """Main Methods"""
    def load_excel_sheets(self):
        self.df = pd.read_excel(
            io="data/csv/transcripts.xlsx", sheet_name="Sheet1", header=0
        )
        self.df_2 = pd.read_excel(
            io="data/csv/testing.xlsx", sheet_name="Sheet1", header=0
        )
        self.faq_df = pd.read_excel(
            io="data/csv/recipes.xlsx", sheet_name="Sheet1", header=0
        )

    def setup_ui(self):
        self.setObjectName("MainWindow")
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.setCentralWidget(self.centralwidget)
        self.central_grid = QtWidgets.QGridLayout(self.centralwidget)
        self.central_grid.setObjectName("central_grid")
        self.central_stacked_widget = QtWidgets.QStackedWidget(self.centralwidget)
        self.central_stacked_widget.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.central_stacked_widget.setLineWidth(0)
        self.central_stacked_widget.setObjectName("central_stacked_widget")
        self.central_grid.addWidget(self.central_stacked_widget, 0, 0, 1, 1)
        self.faq_search_tab = FaqSearchTabContainer(parent=self)
        self.central_stacked_widget.insertWidget(2, self.faq_search_tab)

    def setup_main_components(self):
        self.analysis_suite = AnalysisSuite(parent=self)
        self.central_stacked_widget.insertWidget(0, self.analysis_suite)

        self.testing_suite = TestingSuite(parent=self)
        self.central_stacked_widget.insertWidget(1, self.testing_suite)

        self.populate_search_box()

    def setup_menubar(self):
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1449, 26))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)

    def populate_search_box(self):
        # Initializing FAQ search window item model
        model = QStandardItemModel(len(self.faq_df.index), len(self.faq_df.columns))
        for i, row in self.faq_df.iterrows():
            for j, string in enumerate(row):
                item = QStandardItem(str(string) if string else "")
                model.setItem(i, j, item)  # check this
        self.faq_auto_search_model = QSortFilterProxyModel()
        self.faq_auto_search_model.setSourceModel(model)
        self.faq_auto_search_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.faq_auto_search_model.setFilterKeyColumn(-1)

        # Adding search box models
        # TODO: move some of these to base_suite
        self.analysis_suite.faq_search_box.search_box.setModel(
            self.faq_auto_search_model
        )
        self.testing_suite.faq_search_box.search_box.setModel(
            self.faq_auto_search_model
        )
        self.faq_search_tab.search_box.setModel(self.faq_auto_search_model)

        # Connecting regxp filters
        self.analysis_suite.faq_search_box.searchbar.textChanged.connect(
            self.faq_auto_search_model.setFilterRegExp
        )
        self.testing_suite.faq_search_box.searchbar.textChanged.connect(
            self.faq_auto_search_model.setFilterRegExp
        )
        self.faq_search_tab.searchbar.textChanged.connect(
            self.faq_auto_search_model.setFilterRegExp
        )

        self.update_search_box(idx=0)
        self.populate_search_column_select()

    def update_search_box(self, idx: int):
        """
        Updates the search box with values from FAQ excel sheet
        """
        # Synchronize selectors
        page = self.central_stacked_widget.currentIndex()

        widgets = {
            0: self.analysis_suite.faq_search_box.search_column_select,
            1: self.testing_suite.faq_search_box.search_column_select,
            2: self.faq_search_tab.search_column_select,
        }

        for i, widget in enumerate(widgets.values()):
            if i != page:
                widget.blockSignals(True)
                widget.setCurrentIndex(idx)
                widget.blockSignals(False)

        # Set table column to filter by
        try:
            if idx == len(self.faq_df.columns):
                # Set to filter by all columns
                self.faq_auto_search_model.setFilterKeyColumn(-1)
            else:
                self.faq_auto_search_model.setFilterKeyColumn(idx)
        except UnboundLocalError:
            pass

        # Show/hide columns according to current selection
        if (page == 0 or page == 1) and idx != len(self.faq_df.columns):
            for i in range(0, len(self.faq_df.columns)):
                if i != idx:
                    if page == 0:
                        self.analysis_suite.faq_search_box.search_box.hideColumn(i)
                    else:
                        self.testing_suite.faq_search_box.search_box.hideColumn(i)
                else:
                    if page == 0:
                        self.analysis_suite.faq_search_box.search_box.showColumn(i)
                    else:
                        self.testing_suite.faq_search_box.search_box.showColumn(i)

    def populate_search_column_select(self):
        """Set model for FAQ search selector"""

        model = QStandardItemModel(len(self.faq_df.columns), 0)
        for idx, item in enumerate(list(self.faq_df.columns.values)):
            item = QStandardItem(item)
            model.setItem(idx, 0, item)

        item = QStandardItem("Search in all columns")
        model.setItem(len(self.faq_df.columns), 0, item)

        self.analysis_suite.faq_search_box.search_column_select.setModel(model)
        self.testing_suite.faq_search_box.search_column_select.setModel(model)
        self.faq_search_tab.search_column_select.setModel(model)

    def set_df(self, df_title: str, mode: str):
        """
        Assigns dataframe_viewers to analysis and testing suite and switches out models
        """
        if mode == "analysis":
            # Assign viewers
            self.analysis_suite.viewer = self.store.data[df_title].dataframe_viewer
            self.analysis_df_name = df_title

            # Switch out models
            self.analysis_suite.roles_view.replace_model(
                pgdf=self.store.data[df_title],
                parent=self,
                dataframe_explorer=self.store.data[df_title].dataframe_explorer,
            )
            self.analysis_suite.sidebar.populate_sidebar()
            self.analysis_suite.cell_editor_box.populate_cell_selector()
            self.analysis_suite.canned.populate_canned()

        elif mode == "testing":
            self.testing_suite.viewer = self.store.data[df_title].dataframe_viewer
            self.testing_df_name = df_title

            self.testing_suite.roles_view.replace_model(
                pgdf=self.store.data[df_title],
                parent=self,
                dataframe_explorer=self.store.data[df_title].dataframe_explorer,
            )
            self.testing_suite.sidebar.populate_sidebar()
            self.testing_suite.cell_editor_box.populate_cell_selector()
            self.testing_suite.canned.populate_canned()

    def keyPressEvent(self, event):
        """Hotkeys"""
        mods = event.modifiers()

        # Switch to Analysis
        if event.key() == Qt.Key_G and (mods & Qt.ControlModifier):
            self.central_stacked_widget.setCurrentIndex(0)

        # Switch to Testing
        if event.key() == Qt.Key_T and (mods & Qt.ControlModifier):
            self.central_stacked_widget.setCurrentIndex(1)

        # Switch to Dataframe Viewer
        if event.key() == Qt.Key_D and (mods & Qt.ControlModifier):
            self.central_stacked_widget.setCurrentIndex(3)

        QtWidgets.QWidget.keyPressEvent(self, event)

    def workingView(self, idx: int):
        """
        Switches in dataframe viewers and keeps track of the current working view
        """
        # Switch viewer to workarea
        if idx in [1, 0]:
            self.current_work_area = idx
            if idx == 0 and self.analysis_suite.viewer is not None:
                self.analysis_suite.switch_in_dataframe_viewer()
            elif idx == 1 and self.testing_suite.viewer is not None:
                self.testing_suite.switch_in_dataframe_viewer()

        # Switch viewers back to dataframe_viewer
        if idx == 3:
            if self.analysis_df_name:
                self.store.data[self.analysis_df_name].switch_back_dataframe_viewer(
                    mode="analysis"
                )
            if self.testing_df_name:
                self.store.data[self.testing_df_name].switch_back_dataframe_viewer(
                    mode="testing"
                )

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.testing_suite.shutdown_browsers()
        self.analysis_suite.shutdown_browser()
        return super().closeEvent(a0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qtstylish.dark())
    win = MainWindow()
    win.resize(1920, 1080)
    win.show()
    sys.exit(app.exec_())
