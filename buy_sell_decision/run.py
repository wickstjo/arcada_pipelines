from strategies.my_custom_strategy import my_custom_strategy

# CREATE STRATEGY
strat = my_custom_strategy(1000, 0)

# FEED REAL & PREDICTED VALUE TO STRATEGY
strat.make_decision(1, 11)
strat.make_decision(2, 12)
strat.make_decision(3, 13)
strat.make_decision(4, 14)
strat.make_decision(5, 15)
strat.make_decision(6, 16)
strat.make_decision(7, 17)
strat.make_decision(8, 18)
strat.make_decision(9, 19)

# FINALLY, GENERATE A LOGFILE
strat.create_log()