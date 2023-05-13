def rtd(re, rl, rref = 1000, tcf = 0.00385, tref = 0):
    t = tref + ((((re-rl)/rref) - 1) / tcf)
    return t
    