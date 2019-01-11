import evaluate

# Aggregate into 10-minute periods, last 7 days
evaluate.regen_aggregated_period(7, 600)
evaluate.dump_aggregated_period()
