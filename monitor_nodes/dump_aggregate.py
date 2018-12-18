import dump

# Aggregate into 10-minute periods, last 7 days
dump.regen_and_dump_aggregated_period(7, 600)
