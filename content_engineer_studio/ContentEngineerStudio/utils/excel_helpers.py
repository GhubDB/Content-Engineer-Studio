import pandas as pd
import xlwings as xw

from pathlib import Path


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
        # with xw.App() as app:
        #     wb = app.books[filename]
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
        # df.loc[(df['Transcript Link'].isnull()) | (df['Kundenanliegen'].isnull()) | (df['Kundenanliegen'].isnull()) | (df['Kundenanliegen'].isnull()), "bool_check"]=True
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


# df.loc[(df['Price'].isnull()) | (df['Location'].isnull()),"bool_check"]=True

# print(df)


"""pandas tests
df = sheet.range('A2').options(pd.DataFrame, expand='table').value

#################
Pandas Examples
#################

/Assign 1 to the new header "bool_check" where Updated isnull and/or Mechanimus isnull
df.loc[(df['Updated'].isnull()) & (df['Mecanimus'].isnull()),"bool_check"]=1

/Use this to find rows that contain specific values ~ means not use 'fire|grass' for either/or
df.loc[df['Header'].str.contains('searchterm')]

/Assign Value1 and Value2 respectively to Header2 and Header3 where Header is over 500
df.loc[df['Header']] > 500, ['Header2', 'Header3']] = ['Value1', 'Value2']

/Use this to isolate rows where the header matches the value
print(df.loc[df['Location'] =="East"])

/Sort df
df.sort_values('Header', ascending=False)

/Get overview with this
df.describe()

/ Use empty to specify value to assign to empty cells
# df = sheet.range('A2').options(pd.DataFrame, expand='table', empty='NA').value

"""
