import pandas as pd
import xlwings as xw
import datetime as dt

from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Excel:
    '''
    Handles loading, reading and updating Excel files
    '''
    def __init__(self):
        self.sheet = ''

    def load(self, filename, sheet):
        '''
        Loads Excel files
        '''
        filename = Path(filename)
        # with xw.App() as app:
        #     wb = app.books[filename]
        wb = xw.Book(filename)
        self.sheet = wb.sheets[sheet]
        df = self.sheet.range('A1').options(pd.DataFrame, expand='table').value
        df = df.reset_index()
        return df, wb

    def reload(self):
        '''
        Updates the dataframe with current excel values
        '''
        df = self.sheet.range('A1').options(pd.DataFrame, expand='table').value
        df = df.reset_index()


    def updateCells(self, input, header, row):
        '''
        Inserts values into excel sheet
        '''
        self.sheet.range(header, row).value = input
    
    def saveWB(self, wb):
        '''
        Saves specified wb
        '''
        wb.save()

    def incomplete(self, df, start, end):
        '''
        Adds header bool_check to df and assigns 1 to rows that have incomplete values under this header
        '''
        missing = df.iloc[: , start:end + 1]
        
        # df.loc[(df['Transcript Link'].isnull()) | (df['Kundenanliegen'].isnull()) | (df['Kundenanliegen'].isnull()) | (df['Kundenanliegen'].isnull()), "bool_check"]=True
        return missing.isna()

    def overwrite_warn(self, df, idx, **kwargs):
        '''
        Checks if data is being overwritten 
        '''

    def quit(self, wb):
        '''
        Cleans up and closes Excel session
        '''
        self.sheet.autofit()
        self.saveWB(wb)
        # Close excel if wb is the only open wb. Else close the instance.
        if len(wb.app.books) == 1:
            wb.app.quit()
        else:
            wb.close()

# df.loc[(df['Price'].isnull()) | (df['Location'].isnull()),"bool_check"]=True

# print(df)


'''pandas tests
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

'''
#################
# WEBSCRAPING
#################
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# driver.get('')

# login = driver.find_element(By.ID, 'old-username')
# login.send_keys('')

# login = driver.find_element(By.ID, 'old-password')
# login.send_keys('')
# login.send_keys('\n')

# driver.get('')


# favourites = WebDriverWait(driver, 10).until(
#     EC.presence_of_element_located((By.CLASS_NAME, "card-list__items"))
# )

# releases = favourites.find_elements_by_class_name('user-card ')
# cells = []
# for idx, release in enumerate(releases):
#     name = release.find_element(By.CLASS_NAME, 'user-card__name')
#     updated = release.find_element(By.CLASS_NAME, 'user-card__updated')
#     cells.append(name.text)
#     cells.append(str(updated.text))

# print(cells)
# sheet.range('A1').value = cells
