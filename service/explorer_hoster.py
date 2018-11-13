from bottle import post, request, response, get, route, static_file

@route('/explorer/', method='GET')
@route('/explorer', method='GET')
def get_file_index():
    return static_file("index.html", root="explorer_web/")

@route('/explorer/<filename>', method='GET')
def get_file(filename):
    return static_file(filename, root="explorer_web/")
