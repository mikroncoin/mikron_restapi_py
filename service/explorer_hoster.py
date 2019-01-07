from bottle import post, request, response, get, route, static_file, redirect

serviceBaseUrl = 'http://server2.mikron.io:8080';

@route('/explorer/', method='GET')
@route('/explorer', method='GET')
def get_file_index():
    return static_file('index.html', root='explorer_web/')

@route('/explorer/account', method='GET')
def get_account():
    return static_file('account.html', root='explorer_web/')

@route('/explorer/account/<account>', method='GET')
def get_account(account):
    newurl = '/explorer/account?a=' + account;
    return redirect(newurl)

@route('/explorer/block', method='GET')
def get_block():
    return static_file('block.html', root='explorer_web/')

@route('/explorer/block/<block_hash>', method='GET')
def get_block(block_hash):
    newurl = '/explorer/block?bh=' + block_hash;
    return redirect(newurl)

@route('/explorer/<filename>', method='GET')
def get_file(filename):
    return static_file(filename, root="explorer_web/")
