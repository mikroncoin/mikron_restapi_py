import dump

# Aggregate into 10-minute periods, last 7 days
#dump.regen_and_dump_aggregated_daily(7, 600)

# Aggregate daily, last 7 days
dump.regen_and_dump_aggregated_daily(7)
