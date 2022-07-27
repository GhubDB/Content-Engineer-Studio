from pathlib import Path

import pandas as pd
import xlwings as xw


class Excel:
    """
    Handles loading, reading and updating Excel files
    """

    def __init__(self):
        self.sheet = ""
        self.wb = ""

    def load(self, filename, sheet):
        """
        Loads Excel files
        """
        filename = Path(filename)
        self.wb = xw.Book(filename)
        self.sheet = self.wb.sheets[sheet]
        df = self.sheet.range("A1").options(pd.DataFrame, expand="table").value
        df = df.reset_index()
        return df

    def reload(self):
        """
        Updates the dataframe with current excel values
        """
        df = self.sheet.range("A1").options(pd.DataFrame, expand="table").value
        df = df.reset_index()
        return df

    def updateCells(self, text, column, row):
        """
        Inserts values into excel sheet
        """
        self.sheet.range(column, row).value = text

    def saveWB(self):
        """
        Saves specified wb
        """
        self.wb.save()

    def incomplete(self, df, start, end):
        """
        Returns bool array with None values as false
        """
        missing = df.iloc[:, start : end + 1]
        return missing.isna()

    def colorize(self, column, row):
        self.sheet.range(column, row).color = (255, 255, 0)  # Yellow

    def overwrite_warn(self, df, idx, **kwargs):
        """
        Checks if data is being overwritten
        """

    def quit(self, wb):
        """
        Cleans up and closes Excel session
        """
        self.sheet.autofit()
        self.saveWB()
        # Close excel if wb is the only open wb. Else close the instance.
        if len(wb.app.books) == 1:
            wb.app.quit()
        else:
            wb.close()

    def getOpenBooks(self):
        xw.books.active.name

