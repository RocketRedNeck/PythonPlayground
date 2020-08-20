
from tee import start_simple_logging
start_simple_logging(__file__)

from somemodule import SomeClass

print ("With starting...")
with SomeClass(3.14) as thing:
    for i in range(10):
        if i == 4:
            thing.doBad()
        else:
            thing.doGood()

print(f'Exited "Normally" - This line never runs')