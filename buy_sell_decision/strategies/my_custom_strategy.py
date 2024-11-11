from strategies.base_strategy import base_strategy

class my_custom_strategy(base_strategy):
    def __init__(self, starting_capital: int, starting_stocks: int):

        # WHAT MAKES THIS STRATEGY UNIQUE?
        strategy_name: str = 'my_custom_strategy_v1'
        batch_window: int = 3

        # FINALLY, CALL THE PARENT CONSTRUCTOR
        super().__init__(starting_capital, starting_stocks, batch_window, strategy_name)

    # DEFINE THE STRATEGY SPECIFIC BUY CONDITION
    # RETURNS TRUE/FALSE, AND A REASON FOR MAKING IT -- FOR DEBUGGING PURPOSES
    def buy(self, latest_values: list[float], predicted_values: list[float]):
        return True, 'some valid reason that assists debugging'

    # DEFINE THE STRATEGY SPECIFIC SELL CONDITION
    # RETURNS TRUE/FALSE, AND A REASON FOR MAKING IT -- FOR DEBUGGING PURPOSES
    def sell(self, latest_values: list[float], predicted_values: list[float]):
        return False, None