from turtle import *

color('red', 'yellow')
begin_fill()
while True:
    forward(1)
    left(1)
    if abs(pos()) < 1:
        break
end_fill()
done()
