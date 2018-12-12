from bottle import post, request, response, get, route, static_file

serviceBaseUrl = 'http://server2.mikron.io:8080';

def replaceServiceUrl(file):
    return file.replace('{{SERVICE_URL_PLACEHOLDER}}', serviceBaseUrl)

@route('/explorer/', method='GET')
@route('/explorer', method='GET')
def get_file_index():
    #return static_file('index.html', root='explorer_web/')
    f = open('explorer_web/index.html', 'r').read()
    f = replaceServiceUrl(f)
    return f

@route('/explorer/account/<account>', method='GET')
def get_account(account):
    f = open('explorer_web/account.html', 'r').read()
    f = replaceServiceUrl(f)
    f = f.replace('{{ACCOUNT_PLACEHOLDER}}', account)
    return f

@route('/explorer/<filename>', method='GET')
def get_file(filename):
    return static_file(filename, root="explorer_web/")
