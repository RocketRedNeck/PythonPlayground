from getch import getch

while True:
    try:
        c = getch()
        x = bytes(c,'utf-8')
        if chr(3) == c:
            break
        print(c,flush=True, end='' if chr(13) != c else '\n')
    except Exception as e:
        print(f'{repr(e)} : Running in Thonny?')
