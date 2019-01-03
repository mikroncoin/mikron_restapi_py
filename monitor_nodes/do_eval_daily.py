import evaluate

# Aggregate daily, last 7 days
evaluate.regen_aggregated_daily(7, False)
evaluate.dump_aggregated_daily(7)
