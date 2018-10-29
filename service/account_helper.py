import math

def fromRawToMikron(raw):
    # do the 10^30 multiplication in two steps to avoid non-zero trailing digits due to rounding error
    try:
        rawFloat = 0
        rawFloat = float(raw)
        rawFloat = rawFloat / float(1e10)
    except:
        return "ERROR: Numercial conversion"
    return rawFloat

def fromMikronToRaw(mikron):
    try:
        mikronFloat = float(mikron)
    except:
        return "ERROR: Numercial conversion"
    raw = math.floor(mikronFloat * float(1e10))
    rawStr = str(int(raw))
    return rawStr

