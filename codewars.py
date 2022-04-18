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
# container = QtGui.MainWindow()
# edit = TextEdit(objectName="test_textedit", participant="bot", index=0)
# container.addWidget(edit)
# container.show()

# roman = "MMVIII"


# def solution(roman):
#     numerals = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}

#     numbers = [numerals[char] for char in roman]

#     def calculate(numbers, start, len, total):
#         if start + 1 == len:
#             return total + numbers[start]
#         if numbers[start] >= numbers[start + 1]:
#             total += numbers[start]
#         else:
#             total -= numbers[start]
#         return calculate(numbers, start + 1, len, total)

#     return calculate(numbers, 0, len(numbers), 0)


# print(solution(roman))


# n = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]

# def create_phone_number(n):
#     n = [str(x) for x in n]
#     n[0] = "(" + n[0]
#     n[2] = n[2] + ") "
#     n[5] = n[5] + "-"
#     return "".join(n)

# print(create_phone_number(n))


# def find_outlier(integers):
#     def even(n):
#         return True if n % 2 == 0 else False

#     if even(integers[0] + integers[1]):
#         is_even = even(integers[0])
#     else:
#         return integers[1] if even(integers[0]) == even(integers[2]) else integers[0]

#     return [x for x in integers if even(x) != is_even][0]

#################

# def tower_builder(n_floors):
#     return [
#         (i * " ") + ((((n_floors * 2) - 1) - (i * 2)) * "*") + (i * " ")
#         for i in range(n_floors)
#     ][::-1]


# print(tower_builder(6))

#################

# people = "hel  lo"

# def wave(people):
#     return [
#         people[:i] + people[i].upper() + people[i + 1 :]
#         for i in range(len(people))
#         if people[i] != " "
#     ]


# print(wave(people))

# seconds = 3600


# def format_duration(seconds):
#     if seconds <= 0:
#         return "now"

#     time = [["year", 31536000], ["day", 86400], ["hour", 3600], ["minute", 60]]
#     lst = []
#     output = []
#     s = "s"

#     for unit in time:
#         if seconds / unit[1] >= 1:
#             n = seconds // unit[1]
#             lst.append([n, unit[0]])
#             seconds = seconds % unit[1]

#     if seconds > 0:
#         lst.append([seconds, "second"])

#     length = len(lst)

#     for i, unit in enumerate(lst):
#         output.append(f"{unit[0]} {unit[1] if unit[0] == 1 else unit[1] + s}")
#         if i == length - 2 and length > 1:
#             output.append(" and ")

#         if i < length - 2 and length > 2:
#             output.append(", ")

#     return "".join(output)


# print(format_duration(seconds))

# string = ")("


# def valid_parentheses(string):
#     # if not string or ("(" and ")") not in string:
#     #     return False

#     # if sum(x == "(" for x in string) != sum(x == ")" for x in string):
#     #     return False

#     opened = 1
#     for char in string:
#         if char not in ["(", ")"]:
#             continue
#         if char == "(":
#             opened += 1
#         if char == ")":
#             opened -= 1
#         if opened < 1:
#             return False

#     return True


# print(valid_parentheses(string))


# intervals = [[1, 5], [10, 20], [1, 6], [16, 19], [5, 11], [1, 5], [2, 453]]


# def sum_of_intervals(intervals):
#     intervals = sorted([list(sublist) for sublist in intervals])
#     i = 0
#     while True:
#         if i == len(intervals) - 1:
#             break
#         if intervals[i][1] >= intervals[i + 1][0]:
#             if intervals[i][1] <= intervals[i + 1][1]:
#                 intervals[i][1] = intervals[i + 1][1]
#             intervals.pop(i + 1)
#             continue
#         i += 1

#     return sum([item[0] - item[1] for item in intervals]) * -1


# print(sum_of_intervals(intervals))
u = [1, 3, 4, 7, 9, 10, 13, 15, 19, 21, 22, 27, ...]


def dbl_linear(u):
    for i, j in enumerate(u):
        print(i, j)


dbl_linear(u)
