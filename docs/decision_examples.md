### MODEL TRAINING

- Train 3 regression models:
    - Using the same historical `AAPL` dataset.
    - With a differently shifted `close` column.

```yaml
# DATASET ROW
timestamp:          int
symbol:             text
open:               float
high:               float
low:                float
close:              float
adjusted_close:     float
volume:             int
```

- Model 1:
    - Shift `close` column by 5 units.
    - Represents the `immediate` future.
- Model 2:
    - Shift `close` column by 15 units.
    - Represents the `near` future.
- Model 3:
    - Shift `close` column by 30 units.
    - Represents the `distant` future.

### PREDICTION BATCH

- Feed fresh `AAPL` data to each model, side-by-side.
- For every fresh row, the `decision_synthesis` component receives:

```yaml
# PREDICTION BATCH
input_row:
    timestamp:          1727460997
    symbol:             AAPL
    open:               160.02000427246094
    high:               162.3000030517578
    low:                154.6999969482422
    close:              161.6199951171875
    adjusted_close:     159.1901397705078
    volume:             162294600

predictions:
    pipe_model_1:       153.64
    pipe_model_2:       159.96
    pipe_model_3:       168.12
```

### DECISION SYNTHESIS

- How many of the models are predicting a higher value?
    - What percentage of growth relative to the current value?
- What if the immediate future is lower, but distant future is higher?
    - What if it's significantly higher?
    - Is there an opportunity to sell now and buy back for more later?
- Based on how much `AAPL` stock we currently have:
    - Do we have an aversion to buying more?
    - Do we ever want to get rid of ALL stock?
- If we to decide to buy/sell, then how many stocks?
    - 1? 2? 100?
- Perhaps we want to maintain at a certain amount of capital?
- Does this decision require more context from the database?
    - Statistical averages.
    - Standard deviations.
    - etc.
- Could LLMs offer creative solutions for this?
    - Model outputs are quite easy to describe.
    - No model descriptions are necessary.