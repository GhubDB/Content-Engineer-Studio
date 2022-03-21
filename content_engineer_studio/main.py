import sys
import re
import time
import traceback
from warnings import filters

from PyQt5.uic import loadUi
from PyQt5.QtCore import (
    QEvent,
    QItemSelectionModel,
    Qt,
    QObject,
    pyqtSignal,
    pyqtSlot,
    QThreadPool,
    QSortFilterProxyModel,
    QTimer,
)
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
    QTextEdit,
    QLabel,
    QPushButton,
    QWidget,
    QGridLayout,
    QMainWindow,
    QHeaderView,
    QTableWidgetItem,
    QButtonGroup,
    QRadioButton,
    QApplication,
)
from PyQt5.QtGui import (
    QStandardItemModel,
    QStandardItem,
    QFont,
    QFontDatabase,
    QColor,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextCursor,
)
from utils.model_test import ModelTest
import qtstylish

from bs4 import BeautifulSoup

# PandasGUI imports
import inspect
import os
import pprint
from typing import Callable, Union, List, Optional
from dataclasses import dataclass
import pandas as pd
import pkg_resources
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

# This needs to be pip -e filepath installed for development mode
import pandasgui

from pandasgui.store import PandasGuiStore
from pandasgui.utility import as_dict, fix_ipython, get_figure_type, resize_widget
from pandasgui.widgets.find_toolbar import FindToolbar
from pandasgui.widgets.json_viewer import JsonViewer
from pandasgui.widgets.navigator import Navigator
from pandasgui.widgets.figure_viewer import FigureViewer
from pandasgui.widgets.settings_editor import SettingsEditor
from pandasgui.widgets.python_highlighter import PythonHighlighter
from pandasgui.widgets.dataframe_explorer import (
    DataFrameViewer,
    HeaderRolesViewContainer,
)

from IPython.core.magic import register_line_magic
import logging

# My packages
from utils.excel_helpers import Excel
from utils.selenium_helpers import Browser
from utils.data_variables import Data
from widgets.analysis_suite import AnalysisSuite
from widgets.drag_drop import DragDrop
from utils.stylesheets import Stylesheets
from utils.worker_thread import Worker, WorkerSignals
from widgets.faq_search_tab import FaqSearchTabContainer
from widgets.testing_suite import TestingSuite

############################################################################
# Main
############################################################################
class MainWindow(QMainWindow):
    """
    Main application
    """

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        #####################################################
        """Initializing variables"""
        #####################################################

        # Loading excel sheets for test purposes
        self.analysis_excel = Excel()
        self.testing_excel = Excel()
        self.faq_excel = Excel()
        self.df = self.analysis_excel.load("csv/transcripts.xlsx", "Sheet1")
        self.df_2 = self.testing_excel.load("csv/testing.xlsx", "Sheet1")
        self.faq_df = self.faq_excel.load("csv/recipes.xlsx", "Sheet1")

        self.threadpool = QThreadPool()

        # Stores what view the user has worked in last
        self.current_work_area = 0

        #####################################################
        """Seting up components"""
        #####################################################

        # Setup UI
        self.setDocumentMode(False)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.setCentralWidget(self.centralwidget)
        self.central_grid = QtWidgets.QGridLayout(self.centralwidget)
        self.central_grid.setObjectName("central_grid")
        self.stackedWidget = QtWidgets.QStackedWidget(self.centralwidget)
        self.stackedWidget.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.stackedWidget.setLineWidth(0)
        self.stackedWidget.setObjectName("stackedWidget")

        # Setup main components
        self.analysis_suite = AnalysisSuite(parent=self)
        self.stackedWidget.addWidget(self.analysis_suite)

        self.testing_suite = TestingSuite(parent=self)
        self.stackedWidget.addWidget(self.testing_suite)

        self.faq_search_tab = FaqSearchTabContainer(parent=self)
        self.stackedWidget.addWidget(self.faq_search_tab)

        # Setup menubar
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1449, 26))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuSwitch_View = QtWidgets.QMenu(self.menubar)
        self.menuSwitch_View.setObjectName("menuSwitch_View")
        MainWindow.setMenuBar(self.menubar)
        self.open = QtWidgets.QAction(MainWindow)
        self.open.setObjectName("open")
        self.actionSet_Browser_Position = QtWidgets.QAction(MainWindow)
        self.actionSet_Browser_Position.setObjectName("actionSet_Browser_Position")
        self.select_open = QtWidgets.QAction(MainWindow)
        self.select_open.setObjectName("select_open")
        self.open_from_disk = QtWidgets.QAction(MainWindow)
        self.open_from_disk.setObjectName("open_from_disk")
        self.actionAnalysis = QtWidgets.QAction(MainWindow)
        self.actionAnalysis.setObjectName("actionAnalysis")
        self.actionTesting = QtWidgets.QAction(MainWindow)
        self.actionTesting.setObjectName("actionTesting")
        self.actionFAQ = QtWidgets.QAction(MainWindow)
        self.actionFAQ.setObjectName("actionFAQ")
        self.actionSettings = QtWidgets.QAction(MainWindow)
        self.actionSettings.setObjectName("actionSettings")
        self.analysis_menu = QtWidgets.QAction(MainWindow)
        self.analysis_menu.setObjectName("analysis_menu")
        self.testing_menu = QtWidgets.QAction(MainWindow)
        self.testing_menu.setObjectName("testing_menu")
        self.faq_menu = QtWidgets.QAction(MainWindow)
        self.faq_menu.setObjectName("faq_menu")
        self.settings_menu = QtWidgets.QAction(MainWindow)
        self.settings_menu.setObjectName("settings_menu")
        self.settings_menu_2 = QtWidgets.QAction(MainWindow)
        self.settings_menu_2.setObjectName("settings_menu_2")
        self.data_frame_viewer_menu = QtWidgets.QAction(MainWindow)
        self.data_frame_viewer_menu.setObjectName("data_frame_viewer_menu")
        self.menuFile.addAction(self.select_open)
        self.menuFile.addAction(self.open_from_disk)
        self.menuSwitch_View.addAction(self.analysis_menu)
        self.menuSwitch_View.addAction(self.testing_menu)
        self.menuSwitch_View.addAction(self.faq_menu)
        self.menuSwitch_View.addAction(self.data_frame_viewer_menu)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuSwitch_View.menuAction())

        # Apply custom stylesheets
        self.setStyleSheet(Stylesheets.custom_dark)

        # Connecting functions
        self.stackedWidget.currentChanged.connect(self.workingView)
        self.close_faq.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(self.current_work_area)
        )
        self.analysis_menu.triggered.connect(self.switchToAnalysis)
        self.testing_menu.triggered.connect(self.switchToTesting)
        self.faq_menu.triggered.connect(lambda: self.stackedWidget.setCurrentIndex(3))
        self.settings_menu_2.triggered.connect(
            lambda: self.stackedWidget.setCurrentIndex(2)
        )
        self.data_frame_viewer_menu.triggered.connect(
            lambda: self.stackedWidget.setCurrentIndex(5)
        )
        self.add_analysis_dataframe.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(5)
        )

        #####################################################
        """Adding Pandasgui"""
        #####################################################
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

        # Enables PyQt event loop in IPython
        fix_ipython()

        # Keep a list of widgets so they don't get garbage collected
        self.refs = []

        """Start show"""
        settings = {}

        # Register IPython magic
        try:

            @register_line_magic
            def pg(line):
                self.store.eval_magic(line)
                return line

        except Exception as e:
            # Let this silently fail if no IPython console exists
            if (
                e.args[0]
                == "Decorator can only run in context where `get_ipython` exists"
            ):
                pass
            else:
                raise e

        """Start viewer init"""
        self.navigator = None
        self.splitter = None
        self.find_bar = None

        self.refs.append(self)

        self.store = PandasGuiStore()
        self.store.gui = self

        # Add user provided settings to data store
        for key, value in settings.items():
            setting = self.store.settings[key]
            setting.value = value

        self.code_history_viewer = None

        """Create all widgets"""
        # Hide the question mark on dialogs
        # self.app.setAttribute(Qt.AA_DisableWindowContextHelpButton)

        # This adds the drag_drop area for testing/analysis dataframes
        self.drag_drop = DragDrop(self)

        # This holds the DataFrameExplorer for each DataFrame
        self.stacked_widget = QtWidgets.QStackedWidget()

        # Make the analys/testing df selection splitter
        self.splitter_9 = QtWidgets.QSplitter(Qt.Vertical)

        # Make the navigation bar
        self.navigator = Navigator(self.store)

        # Make splitter to hold nav and DataFrameExplorers
        self.splitter = QtWidgets.QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.splitter_9)
        self.splitter_9.addWidget(self.drag_drop)
        self.splitter_9.addWidget(self.navigator)
        # self.splitter_9.setStretchFactor(999, 0)
        self.splitter.addWidget(self.stacked_widget)

        # self.splitter.setCollapsible(0, False)
        # self.splitter.setCollapsible(1, False)
        # self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(0, 1)

        """Addin to main_window"""
        self.verticalLayout_2.addWidget(self.splitter)

        # makes the find toolbar
        self.find_bar = FindToolbar(self)
        self.addToolBar(self.find_bar)

        # Create a copy of the settings in case the SettingsStore reference has
        # been discarded by Qt prematurely
        # https://stackoverflow.com/a/17935694/10342097
        # self.store.settings = self.store.settings.copy()

        # Signals
        self.store.settings.settingsChanged.connect(self.apply_settings)

        self.apply_settings()

        """Continue init"""
        dataframe_kwargs = {"Analysis": self.df, "Testing": self.df_2}
        for df_name, df in dataframe_kwargs.items():
            self.store.add_dataframe(df, df_name)

        # Default to first item
        self.navigator.setCurrentItem(self.navigator.topLevelItem(0))

        """Add  to menubar"""

        @dataclass
        class MenuItem:
            name: str
            func: Callable
            shortcut: str = ""

        items = {
            "Edit": [
                MenuItem(
                    name="Find", func=self.find_bar.show_find_bar, shortcut="Ctrl+F"
                ),
                # MenuItem(name="Copy", func=self.copy, shortcut="Ctrl+C"),
                # MenuItem(
                #     name="Copy With Headers",
                #     func=self.copy_with_headers,
                #     shortcut="Ctrl+Shift+C",
                # ),
                # MenuItem(name="Paste", func=self.paste, shortcut="Ctrl+V"),
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
                {
                    "Context Menus": [
                        MenuItem(
                            name="Add PandasGUI To Context Menu",
                            func=self.add_to_context_menu,
                        ),
                        MenuItem(
                            name="Remove PandasGUI From Context Menu",
                            func=self.remove_from_context_menu,
                        ),
                        MenuItem(
                            name="Add JupyterLab To Context Menu",
                            func=self.add_jupyter_to_context_menu,
                        ),
                        MenuItem(
                            name="Remove JupyterLab From Context Menu",
                            func=self.remove_jupyter_from_context_menu,
                        ),
                    ]
                },
            ],
            "Debug": [
                MenuItem(name="About", func=self.about),
                MenuItem(name="Browse Sample Datasets", func=self.show_sample_datasets),
                MenuItem(name="View PandasGuiStore", func=self.view_store),
                MenuItem(name="View DataFrame History", func=self.view_history),
            ],
        }

        def add_menus(dic, root):
            # Add menu items and actions to UI using the schema defined above
            for menu_name in dic.keys():
                menu = root.addMenu(menu_name)
                for x in dic[menu_name]:
                    if type(x) == dict:
                        add_menus(x, menu)
                    else:
                        action = QtWidgets.QAction(x.name, self)
                        action.setShortcut(x.shortcut)
                        action.triggered.connect(x.func)
                        menu.addAction(action)

        add_menus(items, self.menubar)

        """End PandasGUI init"""

    ################################################################################################
    """
    PandasGUI Methods
    """
    ################################################################################################
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

    # def copy(self):
    #     print("other copy")
    #     if self.store.selected_pgdf.dataframe_explorer.active_tab == "DataFrame":
    #         self.store.selected_pgdf.dataframe_explorer.dataframe_viewer.copy()
    #     elif self.store.selected_pgdf.dataframe_explorer.active_tab == "Statistics":
    #         self.store.selected_pgdf.dataframe_explorer.statistics_viewer.dataframe_viewer.copy()

    # def copy_with_headers(self):
    #     if self.store.selected_pgdf.dataframe_explorer.active_tab == "DataFrame":
    #         self.store.selected_pgdf.dataframe_viewer.copy(header=True)
    #     elif self.store.selected_pgdf.dataframe_explorer.active_tab == "Statistics":
    #         self.store.selected_pgdf.dataframe_explorer.statistics_viewer.dataframe_viewer.copy(
    #             header=True
    #         )

    # def paste(self):
    #     if self.store.selected_pgdf.dataframe_explorer.active_tab == "DataFrame":
    #         self.store.selected_pgdf.dataframe_explorer.dataframe_viewer.paste()

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

    # Return all DataFrames, or a subset specified by names.
    # Returns a dict of name:df or a single df if there's only 1
    def get_dataframes(self, names: Union[None, str, list] = None):
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

    # https://stackoverflow.com/a/29769228/3620725
    def add_to_context_menu(self):
        import winreg

        key = winreg.HKEY_CURRENT_USER
        command_value = rf'{sys.executable} -m pandasgui.run_with_args "%V"'
        icon_value = rf"{os.path.dirname(pandasgui.__file__)}\resources\images\icon.ico"

        handle = winreg.CreateKeyEx(
            key,
            "Software\Classes\*\shell\Open with PandasGUI\command",
            0,
            winreg.KEY_SET_VALUE,
        )
        winreg.SetValueEx(handle, "", 0, winreg.REG_SZ, command_value)
        handle = winreg.CreateKeyEx(
            key, "Software\Classes\*\shell\Open with PandasGUI", 0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(handle, "icon", 0, winreg.REG_SZ, icon_value)

    def remove_from_context_menu(self):
        import winreg

        key = winreg.HKEY_CURRENT_USER
        winreg.DeleteKey(key, "Software\Classes\*\shell\Open with PandasGUI\command")
        winreg.DeleteKey(key, "Software\Classes\*\shell\Open with PandasGUI")

    def add_jupyter_to_context_menu(self):
        import winreg

        key = winreg.HKEY_CURRENT_USER
        command_value = rf'cmd.exe /k jupyter lab --notebook-dir="%V"'
        icon_value = (
            rf"{os.path.dirname(pandasgui.__file__)}\resources\images\jupyter_icon.ico"
        )

        handle = winreg.CreateKeyEx(
            key,
            "Software\Classes\directory\Background\shell\Open with JupyterLab\command",
            0,
            winreg.KEY_SET_VALUE,
        )
        winreg.SetValueEx(handle, "", 0, winreg.REG_SZ, command_value)
        handle = winreg.CreateKeyEx(
            key,
            "Software\Classes\directory\Background\shell\Open with JupyterLab",
            0,
            winreg.KEY_SET_VALUE,
        )
        winreg.SetValueEx(handle, "icon", 0, winreg.REG_SZ, icon_value)

    def remove_jupyter_from_context_menu(self):
        import winreg

        key = winreg.HKEY_CURRENT_USER
        winreg.DeleteKey(
            key,
            "Software\Classes\directory\Background\shell\Open with JupyterLab\command",
        )
        winreg.DeleteKey(
            key, "Software\Classes\directory\Background\shell\Open with JupyterLab"
        )

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
        from pandasgui.datasets import LOCAL_DATASET_DIR
        import os

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

    ################################################################################################
    """
    Main Methods
    """
    ################################################################################################

    def keyPressEvent(self, event):
        """
        Hotkeys
        """
        QtWidgets.QWidget.keyPressEvent(self, event)
        mods = event.modifiers()
        if event.key() == Qt.Key_G and (mods & Qt.ControlModifier):
            # Switch to Analysis
            self.stackedWidget.setCurrentIndex(0)
        if event.key() == Qt.Key_T and (mods & Qt.ControlModifier):
            # Switch to Testing
            self.stackedWidget.setCurrentIndex(1)
        if event.key() == Qt.Key_D and (mods & Qt.ControlModifier):
            # Switch to Dataframe Viewer
            self.stackedWidget.setCurrentIndex(5)

    def set_df(self, df_title: str, mode: str):
        """
        Assigns dataframes to analysis and testing suite
        """
        if mode == "analysis":
            self.analysis_df = self.store.data[df_title]
            if self.analysis_viewer == None:
                self.analysis_viewer = DataFrameViewer(pgdf=self.analysis_df)
                self.analysis_dataframe_layout.replaceWidget(
                    self.add_analysis_dataframe,
                    self.analysis_viewer,
                )
                self.add_analysis_dataframe.deleteLater()

                # Add Header Roles View
                self.analysis_roles_view = HeaderRolesViewContainer(
                    parent=self.analysis_df.dataframe_explorer
                )
                self.analysis_column_viewer_layout.addWidget(self.analysis_roles_view)

            # Switch out models
            self.analysis_viewer.replace_models(pgdf=self.analysis_df)
            self.analysis_roles_view.replace_model(pgdf=self.analysis_df)
            self.populate_sidebar()
            self.populate_cell_selector()
            self.populate_canned()

        elif mode == "testing":
            self.testing_df = self.store.data[df_title]
            if self.testing_viewer == None:
                self.testing_viewer = DataFrameViewer(pgdf=self.testing_df)
                self.testing_dataframe_layout.replaceWidget(
                    self.add_testing_dataframe,
                    self.testing_viewer,
                )
                self.add_testing_dataframe.deleteLater()

                self.analysis_roles_view = HeaderRolesViewContainer(
                    parent=self.testing_df.dataframe_explorer
                )
                self.analysis_column_viewer_layout.addWidget(self.analysis_roles_view)

            self.testing_viewer.replace_models(pgdf=self.testing_df)
            self.testing_roles_view.replace_model(pgdf=self.testing_df)
            self.populate_sidebar_2()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qtstylish.dark())
    win = MainWindow()
    win.resize(1920, 180)
    win.show()
    sys.exit(app.exec_())
