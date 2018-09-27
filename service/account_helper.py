import math

def fromRawToMikron(raw):
    try:
        rawFloat = float(raw)
    except:
        return "ERROR: Numercial conversion"
    return rawFloat / float(1e30)

def fromMikronToRaw(mikron):
    try:
        mikronFloat = float(mikron)
    except:
        return "ERROR: Numercial conversion"
    # do the 10^30 multiplication in two steps to avoid non-zero trailing digits due to rounding error
    raw = math.floor(mikronFloat * float(1e20))
    raw = raw * 10000000000
    return raw

