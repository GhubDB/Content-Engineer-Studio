import pandas as pd

d = {
    "col1": [1, 2, 3, 4],
    "col2": [1, 2, 3, 4],
    "col3": [1, 2, 3, 4],
    "col4": [1, 2, 3, 4],
    "col5": [1, 2, 3, 4],
}
df = pd.DataFrame(data=d)
df.columns = pd.MultiIndex.from_product([df.columns, ["identical"]])
print(list(df.columns.get_level_values(1)))
print(df)
