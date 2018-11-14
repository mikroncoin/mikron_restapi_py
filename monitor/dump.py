import db
import datetime

def dump():
    lines = db.get_all_lines()
    #print(str(len(lines)) + " lines")
    for l in lines:
        ts = int(l['time_sec'])
        # derive timestamp in other formats
        sec_ordinal2 = ts - 1535760000          # Sept 1 2018
        date_time = datetime.datetime.utcfromtimestamp(ts)
        date_date = date_time.date()
        day_ordinal = date_date.toordinal() - 736938     # Sept 1 2018
        date_string = date_date.isoformat()
        hour_string = date_time.time().isoformat()
        print(ts, sec_ordinal2, day_ordinal, "'" + date_string + "'", "'" + hour_string + "'", \
                l['no_nodes'], l['no_blocks'], l['no_frontiers'], sep=', ')

dump()
