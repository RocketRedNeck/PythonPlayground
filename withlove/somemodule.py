
class SomeClass:
    def __init__(self, initialvalue):
        self.x = initialvalue

    def __enter__(self):
        print(f'__enter__ called')
        print(f'Do setup here')
        return self

    def __exit__(self, type, value, traceback):
        print(f'__exit__ called')
        print(f'Do tear down here (i.e., close things up, etc)')

    def doGood(self):
        print(f'x = {self.x}')
        return 1.0/self.x

    def doBad(self):
        self.x = 0
        return self.doGood()

