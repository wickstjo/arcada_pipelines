from base_strategy import base_strategy

class mock_strategy(base_strategy):
    def buy(self, real_values: list[dict], predicted_values: list[dict]):
        if real_values[-1] < predicted_values[-1]:
            return True, 1, 'NAIVE BUY CONDITION MET'

        return False, 0, ''

    def sell(self, real_values: list[dict], predicted_values: list[dict]):
        if real_values[-1] > predicted_values[-1]:
            return True, 1, 'NAIVE SELL CONDITION MET'

        return False, 0, ''