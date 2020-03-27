
def add(a, b):
    a += b
    return a

def sub(a, b):
    a -= b
    return a

def mul(a, b):
    a *= b
    return a

def div(a, b):
    a /= b
    return a

def mod(a, b):
    a %= b
    return a

def inc(a):
    a +=1
    return a

def dec(a):
    a -= 1
    return a

def _cmp(a, b):
    if a == b:
        return 0b00000001
    elif a < b:
        return 0b00000100
    else:
        return 0b00000010

def _and(a, b):
    a &= b
    return a

def _not(a, b):
    a = ~b
    return a

def _or(a, b):
    a |= b
    return a

def xor(a, b):
    a ^= b
    return a

def shl(a, b):
    a <<= b
    return a

def shr(a, b):
    a >>= b
    return a
    