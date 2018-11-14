import db
import datetime
import sys

class datapoint:
    count = 0
    sum = 0
    first = 0
    last = 0
    min = sys.maxsize
    max = 0
    def add(self, v):
        self.sum = self.sum + v
        if self.count == 0:
            self.first = v
        self.last = v
        if self.min > v:
            self.min = v
        if self.max < v:
            self.max = v
        self.count = self.count + 1
    def avg(self):
        if self.count == 0:
            return 0
        return float(self.sum) / float(self.count)

def dump():
    lines = db.get_all_lines_unordered()
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

def dump_compressed(timestep):
    lines = db.get_all_lines_ordered()
    count = 0
    starttime = 0
    dp1 = datapoint()
    dp2 = datapoint()
    dp3 = datapoint()
    for l in lines:
        ts = int(l['time_sec'])
        if count == 0:
            starttime = int(ts / timestep) * timestep
            endtime = starttime + timestep
        #print(ts, starttime, endtime, ts < endtime)
        if ts < endtime:
            dp1.add(l['no_nodes'])
            dp2.add(l['no_blocks'])
            dp3.add(l['no_frontiers'])
            #print(dp1.count, dp1.avg())
        else:
            # new period
            #print("new period", ts, dp1.count)
            if dp1.count > 0 or dp2.count > 0 or dp3.count > 0:
                #print(dp1.count)
                # derive timestamp in other formats
                sec_ordinal2 = endtime - 1535760000          # Sept 1 2018
                date_time = datetime.datetime.utcfromtimestamp(endtime)
                date_date = date_time.date()
                day_ordinal = date_date.toordinal() - 736938     # Sept 1 2018
                date_string = date_date.isoformat()
                hour_string = date_time.time().isoformat()
                print(endtime, sec_ordinal2, timestep, day_ordinal, "'" + date_string + "'", "'" + hour_string + "'", \
                    dp1.first, dp1.last, dp1.avg(), dp1.min, dp1.max, \
                    dp2.first, dp2.last, dp2.avg(), dp2.min, dp2.max, \
                    dp3.first, dp3.last, dp3.avg(), dp3.min, dp3.max, \
                    sep=', ')
            dp1 = datapoint()
            dp2 = datapoint()
            dp3 = datapoint()
            starttime = endtime
            endtime = starttime + timestep
            while (endtime <= ts):
                starttime = endtime
                endtime = starttime + timestep
            if ts < endtime:
                dp1.add(l['no_nodes'])
                dp2.add(l['no_blocks'])
                dp3.add(l['no_frontiers'])
        count = count + 1
    if dp1.count > 0 or dp2.count > 0 or dp3.count > 0:
        # derive timestamp in other formats
        sec_ordinal2 = endtime - 1535760000          # Sept 1 2018
        date_time = datetime.datetime.utcfromtimestamp(endtime)
        date_date = date_time.date()
        day_ordinal = date_date.toordinal() - 736938     # Sept 1 2018
        date_string = date_date.isoformat()
        hour_string = date_time.time().isoformat()
        print(endtime, sec_ordinal2, timestep, day_ordinal, "'" + date_string + "'", "'" + hour_string + "'", \
                dp1.first, dp1.last, dp1.avg(), dp1.min, dp1.max, \
                dp2.first, dp2.last, dp2.avg(), dp2.min, dp2.max, \
                dp3.first, dp3.last, dp3.avg(), dp3.min, dp3.max, \
                sep=', ')
