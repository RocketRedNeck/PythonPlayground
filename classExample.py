
# ***************************************
class Base:
    def __init__(self,N):
        self.N = N
        self.data = N*[0]

    def __str__(self):
        return f'{self.data[:]}'
    
    def fill(self,x):
        self.data = self.N * [x]

# ***************************************
class Derived(Base):
    def __init__(self,N):
        super().__init__(N)

    def fill(self,x):       # Override the function name
        super().fill(x*2)   # But still use the base function explicitly for behavior

class Derived2(Base):
    def __init__(self,N):
        super().__init__(N)

    def fill2(self,x):      # Creates a new function name
        self.fill(x*2)      # But uses base class function implicitly

# ***************************************

y = Base(10)

x = Derived(10)
print(y)
print(x)

y.fill(3)
x.fill(3)
print(y)
print(x)

y.fill(3)
x.fill(3)
print(y)
print(x)

print(f'isinstance(3,int) = {isinstance(3,int)}')
print(f'isinstance(3,float) = {isinstance(3,float)}')
print(f'isinstance(3.14,int) = {isinstance(3.14,int)}')
print(f'isinstance(3.14,float) = {isinstance(3.14,float)}')
