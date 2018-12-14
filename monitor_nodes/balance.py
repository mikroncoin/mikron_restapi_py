import requests

import logging
import random

account_balance_cache = {}

def get_logger():
    """ Get named logger """
    return logging.getLogger(__name__)

def get_account_balance(session, base_url, account):
    try:
        url = base_url + '/account/balance/' + account
        print('Getting balance for', account, url)
        response = session.get(url)
        if response.status_code == 200:
            return (0, float(response.text))
        return (1, 0)
    except:
        return (2, 0)
    return (3, 0)

def get_account_balance_cached(timestamp, session, base_url, account):
    balance_cached = 0
    if account in account_balance_cache:
        cache = account_balance_cache[account]
        if ('balance' in cache) and ('valid_until' in cache):
            balance_cached = cache['balance']
            if cache['valid_until'] >= timestamp:
                #print('Balance found in cache', 'bal', balance, 'acc', account)
                return balance_cached
            else:
                # found in cache, but outdated
                balance_cached = cache['balance']
    # not found in cache
    (ret_code, balance) = get_account_balance(session, base_url, account)
    if ret_code == 0:
        # cache it
        validity = timestamp + random.randint(50, 60) * 60
        cache = {
            'balance': balance,
            'valid_until': validity,
        }
        account_balance_cache[account] = cache
        if balance != balance_cached:
            get_logger().info('Balance added to cache, ' + str(balance) + " " + str(account))
    return balance
