from common.testing import unittest_base
from actions.trading_strategies.strategies.mock_strategy import mock_strategy
import random

class validation_tests(unittest_base):
    def test_strategy_00_validate_inputs(self):
        self.validate_schema(self.input_params, {
            'strategy_name': str,
            'batch_size': int,
            'transaction_fee': int,
            'init': {
                'capital': int,
                'stocks': int,
            }
        })

    ################################################################################################
    ################################################################################################

    def create_mock_strategy(self, prefilled=False, init_capital=None, init_stocks=None):

        # DEFAULT TO YAML CONFIG PARAMS
        default_config = self.input_params

        # OVERRIDE CAPITAL/STOCK VALUES FOR TESTING
        if init_capital != None: default_config['init']['capital'] = init_capital
        if init_stocks != None: default_config['init']['stocks'] = init_stocks

        # CREATE THE STRATEGY
        strategy = mock_strategy(default_config)

        # FILL THE BATCH WINDOW WHEN REQUESTED
        # SO THE NEXT INVOCATION PRODUCES A REAL DECISION
        if prefilled:
            [strategy.make_decision(1, 2) for _ in range(strategy.state.batch_size - 1)]

        return strategy

    ################################################################################################
    ################################################################################################

    def test_strategy_01_default_values(self):
        strategy = self.create_mock_strategy(prefilled=True)

        self.assertTrue(len(strategy.state.strategy_name) > 0, msg='GIVE YOUR STRATEGY A NAME')
        self.assertTrue(strategy.state.batch_size > 0, msg='BATCH SIZE MUST BE LARGER THAN 0')

        # PREVENT CAPITAL OR STOCKS COUNTS TO START FROM THE NEGATIVE
        self.assertTrue(strategy.state.num_capital >= 0, msg='CAPITAL CANNOT START FROM NEGATIVE')
        self.assertTrue(strategy.state.num_stock >= 0, msg='STOCK COUNT CANNOT START FROM NEGATIVE')

        # PREVENT BOTH CAPITAL AND STOCK COUNT TO BE ZERO
        self.assertTrue(strategy.state.num_stock > 0 or strategy.state.num_capital > 0, msg='BOTH CAPITAL AND STOCK COUNT CANNOT START FROM ZERO')

        # MAKE SURE THE TRADE PENALTY IS POSITIVE
        self.assertTrue(strategy.state.transaction_fee >= 0, msg='TRANSACTION FEE CANNOT BE NEGATIVE')

    ################################################################################################
    ################################################################################################

    def test_strategy_02_batch_windows_logic(self):
        strategy = self.create_mock_strategy(prefilled=True, init_capital=100)

        # MAKE SURE ALL THE DECISIONS PRE-BATCH WINDOW ARE HOLDS
        for item in strategy.state.decision_log:
            self.assertEqual(item['decision'], 'hold')

        # THEN RUN ONE OF EACH DECISION
        buy_decision = strategy.make_decision(1, 2)['decision']
        sell_decision = strategy.make_decision(2, 1)['decision']
        hold_decision = strategy.make_decision(1, 1)['decision']

        # VERIFY THE OTHERS
        self.assertEqual(buy_decision, 'buy')
        self.assertEqual(sell_decision, 'sell')
        self.assertEqual(hold_decision, 'hold')

        # FINALLY, MAKE SURE THE BATCH WINDOWS HAVE BEEN TRUNCATED CORRECTLY
        self.assertEqual(len(strategy.state.model_predictions), strategy.state.batch_size)
        self.assertEqual(len(strategy.state.real_values), strategy.state.batch_size)

    ################################################################################################
    ################################################################################################

    def test_strategy_03_buying_state_change(self):
        strategy = self.create_mock_strategy(prefilled=True, init_capital=11)

        # SAVE THE INITIAL VALUES
        pre_capital = strategy.state.num_capital
        pre_stocks = strategy.state.num_stock

        # MAKE & VERIFY BUY DECISION
        rng_price = random.randrange(2, 10)
        output = strategy.make_decision(rng_price, rng_price+1)
        self.assertEqual(output['decision'], 'buy')

        # FIND THE DELTAS OF THE NEW VALUES
        capital_delta = strategy.state.num_capital - pre_capital
        stocks_delta = strategy.state.num_stock - pre_stocks

        # MAKE SURE THEY'RE CORRECT
        self.assertEqual(capital_delta, -(rng_price + strategy.state.transaction_fee))
        self.assertEqual(stocks_delta, 1)

    ################################################################################################
    ################################################################################################

    def test_strategy_04_buying_without_capital(self):
        strategy = self.create_mock_strategy(prefilled=True, init_capital=0)

        output = strategy.make_decision(1, 2)
        self.assertEqual(output['decision'], 'hold')

    ################################################################################################
    ################################################################################################

    def test_strategy_05_selling_state_change(self):
        strategy = self.create_mock_strategy(prefilled=True, init_stocks=1)

        # SAVE THE INITIAL VALUES
        pre_capital = strategy.state.num_capital
        pre_stocks = strategy.state.num_stock

        # MAKE & VERIFY SELL DECISION
        rng_price = random.randrange(2, 10)
        output = strategy.make_decision(rng_price, rng_price-1)
        self.assertEqual(output['decision'], 'sell')

        # FIND THE DELTAS OF THE NEW VALUES
        capital_delta = strategy.state.num_capital - pre_capital
        stocks_delta = strategy.state.num_stock - pre_stocks

        # MAKE SURE THEY'RE CORRECT
        self.assertEqual(capital_delta, (rng_price - strategy.state.transaction_fee))
        self.assertEqual(stocks_delta, -1)

    ################################################################################################
    ################################################################################################

    def test_strategy_06_selling_without_stocks(self):
        strategy = self.create_mock_strategy(prefilled=True, init_stocks=0)

        output = strategy.make_decision(2, 1)
        self.assertEqual(output['decision'], 'hold')

    ################################################################################################
    ################################################################################################

    def test_strategy_07_holding_state_change(self):
        strategy = self.create_mock_strategy(prefilled=True)

        # SAVE THE INITIAL VALUES
        pre_capital = strategy.state.num_capital
        pre_stocks = strategy.state.num_stock

        # MAKE & VERIFY HOLD DECISION
        output = strategy.make_decision(420, 420)
        self.assertEqual(output['decision'], 'hold')

        # FIND THE DELTAS OF THE NEW VALUES
        capital_delta = strategy.state.num_capital - pre_capital
        stocks_delta = strategy.state.num_stock - pre_stocks

        # MAKE SURE THEY'RE CORRECT
        self.assertEqual(capital_delta, 0)
        self.assertEqual(stocks_delta, 0)

    ################################################################################################
    ################################################################################################

    def test_strategy_08_outputs_match_log(self):
        strategy = self.create_mock_strategy()
        outputs = []

        # MAKE 100 RANDOM DECISION
        for _ in range(100):
            first, second = random.randrange(3), random.randrange(3)
            output = strategy.make_decision(first, second)
            outputs.append(output)

        # MAKE SURE OUTPUTS & STRATEGY LOG MATCH
        self.assertEqual(outputs, strategy.state.decision_log)