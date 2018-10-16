import math

def fromRawToMikron(raw):
    # do the 10^30 multiplication in two steps to avoid non-zero trailing digits due to rounding error
    try:
        rawFloat = 0
        if (len(raw) <= 10):
            # short string, convert in one
            rawFloat = float(raw)
            rawFloat = rawFloat / float(1e30)
        else:
            # long string, simple cut the last 10 digits
            raw = raw[:len(raw)-10]
            rawFloat = float(raw)
            rawFloat = rawFloat / float(1e20)
    except:
        return "ERROR: Numercial conversion"
    return rawFloat

def fromMikronToRaw(mikron):
    try:
        mikronFloat = float(mikron)
    except:
        return "ERROR: Numercial conversion"
    # do the 10^30 multiplication in two steps to avoid non-zero trailing digits due to rounding error
    raw = math.floor(mikronFloat * float(1e20))
    rawStr = str(int(raw))
    rawStr = rawStr + "0000000000"
    return rawStr

