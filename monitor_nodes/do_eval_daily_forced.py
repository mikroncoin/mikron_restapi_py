import evaluate

# Aggregate daily, last 7 days
evaluate.regen_aggregated_daily(7, True)
evaluate.dump_aggregated_daily(7)
