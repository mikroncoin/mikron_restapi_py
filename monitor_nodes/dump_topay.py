import db

import time

now = int(time.time())
last_days = 7
start_time = now - last_days * 24 * 3600

to_pay = db.get_daily_filter_topay_time(start_time)
print('Found', len(to_pay), 'rewards to pay out', '(in last', last_days, 'days', now, start_time, '):')
for n in to_pay:
    print('Reward elig/sent: ', n['reward_elig'], n['reward_sent'], n)
