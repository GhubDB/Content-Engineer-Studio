def find_uniq(arr):
    x, y = set(arr)
    if x in arr[0:2]:
        n = y
    else: 
        n = x

    return n   # n: unique number in the array

arr = [1, 1, 1, 1, 0, 1, 1]
print(find_uniq(arr))