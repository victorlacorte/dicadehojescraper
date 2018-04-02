from bisect import bisect_left


# https://docs.python.org/3.6/library/bisect.html
def index(a, x):
    'Locate the leftmost value exactly equal to x'
    i = bisect_left(a, x)
    if i != len(a) and a[i] == x:
        return i
    raise ValueError
