import numpy as np
import pandas as pd
from ContentEngineerStudio.widgets.chat_widget import TextEdit
from PyQt5 import QtCore, QtGui, QtWidgets

# d = {
#     "col1": [1, 2, 3, 4],
#     "col2": [1, 2, 3, 4],
#     "col3": [1, 2, 3, 4],
#     "col4": [1, 2, 3, 4],
#     "col5": [1, 2, 3, 4],
# }
# df = pd.DataFrame(data=d)
# df.columns = pd.MultiIndex.from_product([df.columns, ["identical"]])
# print(list(df.columns.get_level_values(1)))
# print(df)

# tuples = [
#     ("cobra", "mark i"),
#     ("cobra", "mark ii"),
#     ("sidewinder", "mark i"),
#     ("test", "mark i"),
#     ("viper", "mark ii"),
#     ("viper", "mark iii"),
# ]

# index = pd.MultiIndex.from_tuples(tuples)

# values = [[12, 2], [0, 4], [10, 20], [1, 4], [7, 1], [16, 36]]

# df = pd.DataFrame(values, columns=["max_speed", "shield"], index=index)
# # print(df)

# print(df.loc[("sidewinder", "mark i"), "shield"])

# bla = "blabla"


# class thebla:
#     def __init__(self, bla) -> None:
#         self.bla = bla


# class bla2(thebla):
#     def __init__(self, bla):
#         super().__init__(bla)
#         print(self.bla)


# blablabla = bla2(bla)


# s = pd.DataFrame(
#     np.random.randint(low=0, high=10, size=(5, 5)), columns=["a", "b", "c", "d", "e"]
# )
# print(s)
container = QtGui.MainWindow()
edit = TextEdit(objectName="test_textedit", participant="bot", index=0)
container.addWidget(edit)
container.show()
