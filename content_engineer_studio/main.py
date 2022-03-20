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

        # Methods to be executed on startup
        self.populate_flows(example_flows)
        self.populate_actions(example_actions)

        """Sets sidebar to first item selected on startup"""
        # index = self.sidebar.model().index(0, 0)
        # self.sidebar.selectionModel().select(
        #     index, QtCore.QItemSelectionModel.Select | QtCore.QItemSelectionModel.Current)

        self.populate_status_bar(2, 0, 2)

        # Tests
        # print(xw.books.active.name)

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

            # self.analysis_excel.updateCells(customer, self.row + 2, 5)
            # self.analysis_excel.updateCells(bot, self.row + 2, 6)

        # Saving analysis contents
        # self.analysis_excel.updateCells(
        #     self.df.iloc[
        #         self.row : self.row + 1, self.cell_selector_start : self.header_len
        #     ].values,
        #     self.row + 2,
        #     self.cell_selector_start + 1,
        # )

        # Saves the excel file
        # self.analysis_excel.saveWB()

    def eventFilter(self, source: QtCore.QObject, event: QtCore.QEvent):
        """
        Filters Events and calls the respective functions
        """
        # Resizing chat message textedits
        if event.type() == event.Resize:
            page = self.stackedWidget.currentIndex()
            if page == 0:
                QTimer.singleShot(0, self.chat.resizeRowsToContents)
            elif page == 1:
                QTimer.singleShot(0, self.chat_2.resizeRowsToContents)

        # Navigate back to working view
        if source.objectName() == "search_box_3":
            if event.type() == 82:
                index = self.search_box_3.selectionModel().currentIndex()
                value = index.sibling(index.row(), index.column()).data()
                self.search_column_select_3.setCurrentIndex(index.column())
                self.searchbar.setText(
                    value
                ) if self.current_work_area == 0 else self.searchbar_2.setText(value)
                self.stackedWidget.setCurrentIndex(self.current_work_area)
                self.populate_search_box()
                self.search_box.setMinimumHeight(100)
                self.search_box_2.setMinimumHeight(100)
        return super().eventFilter(source, event)

    def getChatlog(self, output):
        """
        Accesses URL and downloads chat log
        """
        if not self.browsers[0].getURL(url=self.df.iloc[self.row, 3]):
            self.browsers[0].setUp(url=self.df.iloc[self.row, 3])
        chat_text = self.browsers[self.current_browser].getCleverbotStatic()
        output.emit(chat_text)

    def populate_chat(self, chat: list[list[str]]):
        self.chat.setColumnCount(1)
        self.chat.setRowCount(len(chat))
        for (
            idx,
            sender,
        ) in enumerate(chat):
            if sender[0] == "bot":
                combo = TextEdit(
                    self, objectName=f"bot_{idx}", participant="bot", index=idx
                )
            else:
                combo = TextEdit(
                    self,
                    objectName=f"customer_{idx}",
                    participant="customer",
                    index=idx,
                )
            self.chat.setCellWidget(idx, 0, combo)

            # Add auto highlighting
            if sender[0] == "customer":
                self.highlighters[idx] = Highlighter(
                    document=combo.document(), name=combo
                )

            combo.setText(sender[1])
            combo.setContextMenuPolicy(Qt.PreventContextMenu)
            combo.installEventFilter(self)

            # Bot
            if sender[0] == "bot":
                combo.setStyleSheet(Stylesheets.bot)
                # combo.setAlignment(Qt.AlignRight)

            # customer
            else:
                combo.setStyleSheet(Stylesheets.customer)

            combo.textChanged.connect(
                lambda idx=idx: self.chat.resizeRowToContents(idx)
            )
            combo.cursorPositionChanged.connect(self.highlight_selection)
        self.chat.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.anynomyzify()

    def clearChat(self):
        # self.chat.clear()
        self.chat.setRowCount(0)

    def highlight_selection(self):
        """
        Highlights and unhighlights user selected text
        """
        sender = self.sender()
        cursor = sender.textCursor()
        current_color = cursor.charFormat().background().color().rgb()
        format = QTextCharFormat()
        if cursor.hasSelection() and current_color != 4282679021:
            format.setBackground(QColor(68, 126, 237))
        else:
            format.clearBackground()
        cursor.setCharFormat(format)

    def anynomyzify(self):
        """
        Receives starting and ending positions
        of words to select from the Highlighter subclass and selects them
        """
        for name, start, end in self.auto_anonymized:
            cursor = name.textCursor()
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.KeepAnchor)
            name.setTextCursor(cursor)
            # cursor.clearSelection()
        self.auto_anonymized = []

    def populate_cell_selector(self):
        """
        Set model for combobox that displays "Editable" rows
        """
        # for _ in range(10):
        #     self.cell_selector.addItem("Banana")
        # return
        self.analysis_df.model["analysis_selector_proxy_model"] = AnalysisSelectorModel(
            parent=self, df=self.analysis_df.df_unfiltered
        )

        self.cell_selector.setModel(
            self.analysis_df.model["analysis_selector_proxy_model"]
        )

    def populate_analysis(self):
        self.analysis.setPlainText(
            self.analysis_df.df_unfiltered.loc[
                self.row, (self.cell_selector.currentText(), "Editable")
            ]
        )

    def save_analysis(self):
        """
        Saves current analysis text to dataframe
        """

        # self.analysis_df.df_unfiltered.loc[
        #     self.row, (self.cell_selector.currentText(), "Editable")
        # ] = self.analysis.toPlainText()

        # self.analysis_df.edit_data(
        #     self.row,
        #     (self.cell_selector.currentText(), "Editable"),
        #     self.analysis.toPlainText(),
        # )
        self.analysis_df.edit_data(
            self.row,
            (self.cell_selector.currentText(), "Editable"),
            self.analysis.toPlainText(),
        )

    def populate_search_column_select(self):
        """
        Set model for FAQ search selector
        """
        model = QStandardItemModel(len(self.faq_df.columns), 0)
        for idx, item in enumerate(list(self.faq_df.columns.values)):
            item = QStandardItem(item)
            model.setItem(idx, 0, item)

        # For searching all columns
        item = QStandardItem("Search in all columns")
        model.setItem(len(self.faq_df.columns), 0, item)
        self.search_column_select.setModel(model)
        self.search_column_select_2.setModel(model)
        self.search_column_select_3.setModel(model)

    def populate_search_box(self):
        """
        Populates the search box with values from FAQ excel sheet
        """
        # Synchronize selectors
        page = self.stackedWidget.currentIndex()
        if page == 0:
            index = self.search_column_select.currentIndex()
            self.search_column_select_2.setCurrentIndex(index)
            self.search_column_select_3.setCurrentIndex(index)
        elif page == 1:
            index = self.search_column_select_2.currentIndex()
            self.search_column_select.setCurrentIndex(index)
            self.search_column_select_3.setCurrentIndex(index)
        elif page == 3:
            index = self.search_column_select_3.currentIndex()
            self.search_column_select.setCurrentIndex(index)
            self.search_column_select_2.setCurrentIndex(index)

        # Set table column to filter by
        try:
            if index == len(self.faq_df.columns):
                # Set to filter by all columns
                self.faq_auto_search_model.setFilterKeyColumn(-1)
            else:
                self.faq_auto_search_model.setFilterKeyColumn(index)
        except UnboundLocalError as e:
            pass

        # Show/hide columns according to current selection
        if (page == 0 or page == 1) and index != len(self.faq_df.columns):
            for i in range(0, len(self.faq_df.index)):
                if i != index:
                    self.search_box.hideColumn(
                        i
                    ) if page == 0 else self.search_box_2.hideColumn(i)
                else:
                    self.search_box.showColumn(
                        i
                    ) if page == 0 else self.search_box_2.showColumn(i)

    def populate_canned(self):
        """
        Radiobuttons
        """

        self.analysis_df.model["analysis_canned_model"] = CannedSelectionModel(
            parent=self, pgdf=self.analysis_df, mode="analysis"
        )
        self.canned.setModel(self.analysis_df.model["analysis_canned_model"])
        self.canned.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.canned.horizontalHeader().resizeSection(1, 50)
        self.canned.horizontalHeader().resizeSection(2, 70)
        self.canned.horizontalHeader().resizeSection(3, 100)
        return
        self.canned.setColumnCount(len(canned_questions) + 1)
        self.canned.setRowCount(len(canned_questions))
        for idx, row in enumerate(canned_questions):
            self.canned.setItem(idx, 0, QTableWidgetItem(row))
            rb_group = QButtonGroup(self, objectName=f"rb_group_{idx}")
            oname = f"rb_group_{idx}"
            rb_group.idReleased.connect(self.canned_selection)
            rb_group.setExclusive(True)
            for i, choice in enumerate(multiple_choice):
                combo = QRadioButton(self)
                combo.setText(choice)
                # combo.setId(i)
                if self.row in self.canned_states:
                    if oname in self.canned_states[self.row]:
                        if self.canned_states[self.row][oname] == choice:
                            combo.setChecked(True)
                rb_group.addButton(combo)
                self.canned.setCellWidget(idx, i + 1, combo)
        self.canned.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        # self.canned.resizeColumnsToContents()
        self.canned.horizontalHeader().resizeSection(1, 50)
        self.canned.horizontalHeader().resizeSection(2, 55)
        self.canned.horizontalHeader().resizeSection(3, 85)
        # self.canned.horizontalHeader().resizeSection(4, 70)

        # self.canned.setColumnWidth(0, 320)

    def canned_selection(self):
        """
        Keeps track of selected radiobuttons for each row of the excel file
        """
        btn = self.sender()
        if self.row not in self.canned_states:
            self.canned_states[self.row] = {
                btn.objectName(): btn.checkedButton().text()
            }
        else:
            self.canned_states[self.row][btn.objectName()] = btn.checkedButton().text()

    def populate_sidebar(self):

        sidebar_proxy_model = SideBarProxyModel(parent=self)
        sidebar_proxy_model.setSourceModel(
            self.analysis_df.model["header_model_vertical"]
        )
        self.sidebar.setModel(sidebar_proxy_model)
        self.sidebar.selectionModel().selectionChanged.connect(self.row_selector)

        # self.sidebar.resizeColumnsToContents()
        # self.sidebar.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def populate_status_bar(self, row: int, start: int, end: int):
        self.status_bar.setText(
            self.df.iloc[row : row + 1, start : end + 1].to_string(
                header=False, index=False
            )
        )

    def populate_flows(self, flows):
        self.flows.setColumnCount(1)
        self.flows.setRowCount(len(flows))
        for idx, row in enumerate(flows):
            self.flows.setItem(idx, 0, QTableWidgetItem(row))
        self.flows.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def populate_actions(self, actions):
        self.actions.setColumnCount(1)
        self.actions.setRowCount(len(actions))
        for idx, row in enumerate(actions):
            self.actions.setItem(idx, 0, QTableWidgetItem(row))
        self.actions.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.actions.resizeColumnsToContents()

    ################################################################################
    """
    Buttons
    """
    ################################################################################

    def btn_up(self):
        if self.row > 0:
            index = self.sidebar.model().index(self.row - 1, 0)
            self.sidebar.selectionModel().select(
                index,
                QtCore.QItemSelectionModel.Select | QtCore.QItemSelectionModel.Current,
            )

    def btn_down(self):
        if self.row < self.index_len:
            index = self.sidebar.model().index(self.row + 1, 0)
            self.sidebar.selectionModel().select(
                index,
                QtCore.QItemSelectionModel.Select | QtCore.QItemSelectionModel.Current,
            )

    def btn_save(self):
        self.saveOnRowChange()

    def btn_colorize(self):
        self.analysis_excel.colorize(
            self.row + 2,
            self.cell_selector.currentIndex() + self.cell_selector_start + 1,
        )

    def switchToAnalysis(self):
        self.is_webscraping = False
        self.stackedWidget.setCurrentWidget(self.analysis_suite)
        self.populate_search_box()

    def switchToTesting(self):
        self.stackedWidget.setCurrentWidget(self.testing_suite)
        self.populate_search_box()

    def exportToTesting(self):
        customer = self.getChatText(export=True)
        if customer:
            for message in customer:
                # print(message)
                item = QtGui.QStandardItem(message)
                self.auto_queue_model.appendRow(item)
        self.stackedWidget.setCurrentWidget(self.testing_suite)
        self.populate_search_box()

    def workingView(self, idx):
        if idx == 0 | idx == 1:
            self.current_work_area = idx

    def btn_test(self):
        index = self.history_model.index(3, 0)
        # print(index)
        print(self.history_model.itemData(index))

    #####################################################################
    """
    Test Suite
    """
    #####################################################################

    def row_selector_2(self, selected: QtCore.QObject):
        """
        Master Controller. Keeps the current row number updated
        """
        # Save and clean up before next row is loaded
        self.saveOnRowChange_2()
        self.chat_2.setRowCount(0)

        # Updates the self.row property
        idx = selected.indexes()
        if len(idx) > 0 and idx != self.row:
            self.row = idx[0].row()

        # Reloading excel sheet for test purposes
        self.df_2 = self.testing_excel.reload()
        self.header_len_2 = len(self.df_2.columns)
        self.index_len_2 = len(self.df_2.index)
        self.completed_2 = self.testing_excel.incomplete(
            self.df_2, self.cell_selector_start_2, len(self.df_2.columns)
        )
        self.populate_sidebar_2()

        # Autoscrolling to the selection on the sidebar
        self.sidebar_2.scrollToItem(self.sidebar.item(self.row, 0))

    def saveOnRowChange_2(self):
        """
        Saves current states to Excel
        """
        # Saving correct FAQ
        index = self.search_box_2.selectionModel().currentIndex()
        value = index.sibling(index.row(), index.column()).data()
        if value:
            self.testing_excel.updateCells(value, self.row + 2, 2)

        # Saving canned_2 states
        # print(self.canned_states_2)

        # Saving chat messages
        if self.chat_2.rowCount() > 0:
            customer, bot = self.getChatText_2()
            self.testing_excel.updateCells(customer, self.row + 2, 3)
            self.testing_excel.updateCells(bot, self.row + 2, 4)

        # Saving analysis contents
        self.testing_excel.updateCells(
            self.df_2.iloc[
                self.row : self.row + 1,
                self.cell_selector_start_2 : self.header_len_2,
            ].values,
            self.row + 2,
            self.cell_selector_start_2 + 1,
        )

        # Saves the excel file
        self.testing_excel.saveWB()

    def save_analysis_2(self):
        """
        Saves current analysis text to dataframe
        """
        self.testing_df.df_unfiltered.loc[self.row][
            self.cell_selector_2.currentText()
        ] = self.analysis_2.toPlainText()

    def setUpNewDialog(self, browser_num=None):
        """
        Sets up (singular) new chat session
        """
        self.browsers[self.current_browser].setUp(url=self.livechat_url)
        self.browsers[self.current_browser].clickCleverbotAgree()
        # clear chat
        self.dialog_num += 1
        self.chat_2.clear()
        self.chat_2.setRowCount(0)
        self.sent_messages = []
        return

    def setUpNewAutoDialog(self, i: int) -> None:
        """
        Prebuffers browser windows and asks auto_queue questions
        """
        # self.browsers[i].tearDown()
        if self.browsers[i].setUp(url=self.livechat_url):
            self.browsers[i].clickCleverbotAgree()
            self.browsers[i].prebufferAutoTab(self.questions)
        return

    def initializeWebscraping(self):
        """
        Start new webscraping thread
        """
        # Check if there is a running webscraping thread
        if not self.is_webscraping:
            self.is_webscraping = True
            # Pass the function to execute
            live_webscraper = Worker(self.chatWebscrapingLoop, "activate_output")
            # Catch signal of new chat messages
            live_webscraper.signals.output.connect(self.populate_chat_2)
            # Execute
            self.threadpool.start(live_webscraper)

    def chatWebscrapingLoop(self, output: QtCore.pyqtSignal):
        """
        Continuously fetches new messages from the chat page
        """
        while self.is_webscraping:
            try:
                chats = self.browsers[self.current_browser].getCleverbotLive()
                if chats:
                    output.emit(chats)
                time.sleep(5)
            except:
                time.sleep(5)
                continue

    def populate_chat_2(self, chat: list[list[str]]):
        output = []
        # Add new messages that are not empty strings to output and reset table
        [
            output.append(message)
            for message in chat
            if message not in self.sent_messages and "" not in message
        ]
        self.chat_2.setColumnCount(1)
        length = len(self.sent_messages)
        self.chat_2.setRowCount(length + len(output))
        for (
            idx,
            sender,
        ) in enumerate(output, start=length):
            if sender[0] == "bot":
                combo = TextEdit(
                    self, objectName=f"bot_{idx}", participant="bot", index=idx
                )
            else:
                combo = TextEdit(
                    self,
                    objectName=f"customer_{idx}",
                    participant="customer",
                    index=idx,
                )
            self.chat_2.setCellWidget(idx, 0, combo)
            combo.setText(sender[1])
            combo.setContextMenuPolicy(Qt.PreventContextMenu)
            combo.installEventFilter(self)
            # Bot
            if sender[0] == "bot":
                combo.setStyleSheet(Stylesheets.bot)
            # customer
            else:
                combo.setStyleSheet(Stylesheets.customer)
            # Add auto resizing of editor and highlighting
            combo.textChanged.connect(
                lambda idx=idx: self.chat_2.resizeRowToContents(idx)
            )
            combo.cursorPositionChanged.connect(self.highlight_selection_2)
        [self.sent_messages.append(message) for message in output]
        self.chat_2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def getChatText_2(self, export: Optional[bool] = False):
        """
        Pulls and anonymizes user selected messages from the chat tablewidget.
        """
        bot = []
        customer = []
        # Iterate over editors in self.chat TableWidget
        for idx in range(0, self.chat_2.rowCount()):
            editor = self.chat_2.cellWidget(idx, 0)
            if editor.selected:
                message_html = BeautifulSoup(
                    self.chat_2.cellWidget(int(idx), 0).toHtml(), "html.parser"
                )
                # Find all span tags and replace the text with ***
                tags = message_html.find_all("span")
                for tag in tags:
                    tag.string = "***"
                if editor.participant == "bot":
                    bot.append(message_html.get_text().strip())
                else:
                    customer.append(message_html.get_text().strip())
            if export:
                return customer
        return "\n".join(customer), "\n".join(bot)

    def highlight_selection_2(self):
        """
        Highlights and unhighlights user selected text
        """
        sender = self.sender()
        cursor = sender.textCursor()
        current_color = cursor.charFormat().background().color().rgb()
        format = QTextCharFormat()
        if cursor.hasSelection() and current_color != 4282679021:
            format.setBackground(QColor(68, 126, 237))
        else:
            format.clearBackground()
        cursor.setCharFormat(format)

    def populate_cell_selector_2(self, start, end):
        for item in list(self.df_2.columns.values)[start:end]:
            self.cell_selector_2.addItem(item)

    # def populate_analysis_2(self):
    #     self.analysis_2.setPlainText(
    #         self.store.data[self.testing_df].df.loc[self.row][
    #             self.cell_selector_2.currentIndex() + self.cell_selector_start_2
    #         ]
    #     )

    def populate_canned_2(self):
        # Radiobuttons
        self.canned_2.setColumnCount(len(canned_questions) + 1)
        self.canned_2.setRowCount(len(canned_questions))
        for idx, row in enumerate(canned_questions):
            self.canned_2.setItem(idx, 0, QTableWidgetItem(row))
            rb_group = QButtonGroup(self, objectName=f"rb_group_2_{idx}")
            oname = f"rb_group_2_{idx}"
            rb_group.idReleased.connect(self.canned_selection_2)
            rb_group.setExclusive(True)
            for i, choice in enumerate(multiple_choice):
                combo = QRadioButton(self)
                combo.setText(choice)
                # combo.setId(i)
                if self.row in self.canned_states_2:
                    if oname in self.canned_states_2[self.row]:
                        if self.canned_states_2[self.row][oname] == choice:
                            combo.setChecked(True)
                rb_group.addButton(combo)
                self.canned_2.setCellWidget(idx, i + 1, combo)
        self.canned_2.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        # self.canned.resizeColumnsToContents()
        self.canned_2.horizontalHeader().resizeSection(1, 50)
        self.canned_2.horizontalHeader().resizeSection(2, 55)
        self.canned_2.horizontalHeader().resizeSection(3, 85)
        # self.canned.horizontalHeader().resizeSection(4, 70)

        # self.canned.setColumnWidth(0, 320)

    def canned_selection_2(self):
        """
        Keeps track of selected radiobuttons for each row of the excel file
        """
        btn = self.sender()
        if self.row not in self.canned_states_2:
            self.canned_states_2[self.row] = {
                btn.objectName(): btn.checkedButton().text()
            }
        else:
            self.canned_states_2[self.row][
                btn.objectName()
            ] = btn.checkedButton().text()

    def getCanned_2(self):
        pass

    def populate_sidebar_2(self):
        self.sidebar_2.setColumnCount(1)
        self.sidebar_2.setRowCount(self.index_len)
        [
            self.sidebar_2.setItem(idx, 0, QTableWidgetItem(str(idx + 2)))
            for idx in range(0, self.index_len_2)
        ]
        [
            self.sidebar_2.item(idx, 0).setBackground(QtGui.QColor(120, 120, 120))
            for idx, row in self.completed_2.iterrows()
            if row.all()
        ]
        self.sidebar_2.resizeColumnsToContents()
        self.sidebar_2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def populateHistory(self, input):
        item = QtGui.QStandardItem(input)
        if self.dialog_num % 2 == 0:
            item.setBackground(QColor(70, 81, 70))
        else:
            item.setBackground(QColor(74, 69, 78))
        self.history_model.appendRow(item)

    #################################################################
    # Buttons_2
    #################################################################

    def send_btn(self):
        """
        Sends chat messages
        """
        input = self.chat_input.text()
        if input:
            self.browsers[self.current_browser].setCleverbotLive(input)
            self.populateHistory(input)
            self.chat_input.clear()

    def new_dialog_btn(self):
        """
        Sets up webscraper, clears dialog and opens new dialog
        """
        if self.auto_2.checkState():
            current = self.current_browser
            if self.current_browser >= self.buffer_len:
                self.current_browser = 0
            else:
                self.current_browser = self.current_browser + 1
            if self.browsers[self.current_browser] is None:
                self.browsers[self.current_browser] = Browser()
            self.browsers[self.current_browser].bringToFront()
            # Start prebuffering previous window
            setup = Worker(lambda: self.setUpNewAutoDialog(current))
            if not self.is_webscraping:
                setup.signals.finished.connect(self.initializeWebscraping)
            self.threadpool.start(setup)
            # clear chat
            self.chat_2.clear()
            self.chat_2.setRowCount(0)
            self.sent_messages = []
        else:
            # Start Thread for webdriver setup
            setup = Worker(self.setUpNewDialog)
            # Once setup is complete, start webscraping the chat log
            if not self.is_webscraping:
                setup.signals.finished.connect(self.initializeWebscraping)
            self.threadpool.start(setup)

    def auto_2_btn(self, signal):
        """
        Turns on auto prebuffering of tabs
        """
        # If auto is on
        if signal == 2:
            self.questions = []

            try:
                # Get current questions in auto_queue
                for i in range(0, self.auto_queue_model.rowCount()):
                    index = self.auto_queue_model.index(i, 0)
                    self.questions.append(
                        index.sibling(index.row(), index.column()).data()
                    )
            except:
                traceback.print_exc()
                return

            if self.questions != []:

                # Set up self.buffer_len new browser windows and ask the questions in the auto_queue
                for i in range(0, self.buffer_len):
                    setup = Worker(lambda: self.setUpNewAutoDialog(i))
                    if not self.is_webscraping and i == 0:
                        setup.signals.finished.connect(self.initializeWebscraping)
                    self.threadpool.start(setup)
                    print(f"setting up {i}")
            print("setup done")

        if signal == 0:
            # If auto is disabled, close browser windows
            self.is_webscraping = False
            for i in range(0, self.buffer_len):
                setup = Worker(lambda: self.browsers[i].tearDown())
                self.threadpool.start(setup)

    def next_btn(self):
        """
        Loads the next message in the auto_queue into the input box
        """
        # Get value of the currently selected item in the auto_queue
        index = self.auto_queue.selectionModel().currentIndex()
        value = index.sibling(index.row(), index.column()).data()
        self.chat_input.setText(value)

        # Jumping to next row in line
        self.auto_queue.selectionModel().select(index, QItemSelectionModel.Deselect)
        index = index.row() + 1
        self.auto_queue.selectRow(index)

        # Jump back to the beginning
        if self.auto_queue.selectedIndexes() == []:
            self.auto_queue.selectRow(0)

    def btn_left_2(self):
        if self.cell_selector_2.currentIndex() > 0:
            self.cell_selector_2.setCurrentIndex(
                self.cell_selector_2.currentIndex() - 1
            )

    def btn_right_2(self):
        if (
            not self.cell_selector_2.currentIndex()
            < self.header_len_2 - self.cell_selector_start_2 - 1
        ):
            self.cell_selector_2.setCurrentIndex(
                self.cell_selector_2.currentIndex() + 2
            )
        self.cell_selector_2.setCurrentIndex(self.cell_selector_2.currentIndex() + 1)

    def btn_up_2(self):
        if self.row > 0:
            index = self.sidebar_2.model().index(self.row - 1, 0)
            self.sidebar_2.selectionModel().select(
                index,
                QtCore.QItemSelectionModel.Select | QtCore.QItemSelectionModel.Current,
            )

    def btn_down_2(self):
        if self.row < self.index_len_2:
            index = self.sidebar_2.model().index(self.row + 1, 0)
            self.sidebar_2.selectionModel().select(
                index,
                QtCore.QItemSelectionModel.Select | QtCore.QItemSelectionModel.Current,
            )

    def btn_save_2(self):
        self.saveOnRowChange_2()

    def btn_colorize_2(self):
        """
        Applies highlight color to specified cells
        """
        self.testing_excel.colorize(
            self.row + 2,
            self.cell_selector_2.currentIndex() + self.cell_selector_start_2 + 1,
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qtstylish.dark())
    win = MainWindow()
    win.resize(1920, 180)
    win.show()
    sys.exit(app.exec_())
