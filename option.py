
def fun(first, second, third, **option):
    print(first)
    print(second)
    print(third)
    print(type(option))
    print(option)
    print(option.get("fourth"))
    print(option.get("fifth"))
    print(option.get("sixth"))
    print(option.get("blah"))

def tion(first, second, third, *option):
    print(first)
    print(second)
    print(third)
    print(type(option))
    print(option)

void = 'void'
fun (1,2,3, fourth=4, fifth=void, sixth=6)
tion (1,2,3, 4,5,6)


