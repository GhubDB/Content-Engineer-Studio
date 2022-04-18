import typing

import mysql.connector

from ContentEngineerStudio.data.data_variables import Data

# db = mysql.connector.connect(
#     host=Data.DEV["host"], user=Data.DEV["user"], passwd=Data.DEV["password"]
# )

# cursor = db.cursor()

# cursor.execute("CREATE DATABASE bot_message_hashes")

class SQL:
    def __init__(self) -> None:
        self.db = self.connect()
        self.cursor = self.db.cursor()

    def connect(self):
        return mysql.connector.connect(
    host=Data.DEV["host"], user=Data.DEV["user"], passwd=Data.DEV["password"]
)

sql = SQL()
print(sql)

class HashedBotMessages:
    pass
