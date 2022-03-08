class UtilityFunctions:
    @staticmethod
    def column_generator():
        n = 1
        while True:
            yield "Column_" + str(n)
            n += 1
