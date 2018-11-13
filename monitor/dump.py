import db

def dump():
    lines = db.get_all_lines()
    #print(str(len(lines)) + " lines")
    for l in lines:
        print(l['timestamp'], l['no_nodes'], l['no_blocks'], l['no_frontiers'], sep=', ')

dump()