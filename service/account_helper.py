import node_rpc_helper

def getAccountBalance(accId):
    balance = node_rpc_helper.getAccountBalance(accId)
    balNum = 0
    try:
        balNum = float(balance)
    except ValueError:
        balNum = 'ERROR: ' + balance
    # Unit conversion
    balMik = balNum / 1e30
    #print("bal", balance, balNum, balMik)
    return balMik

