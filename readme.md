Foo

- Multi-threaded feeding script for timeseries input.
    - Kafka topic for raw data.

---

- Capture raw data with Flink pipeline from kafka.
    - Perform feature engineering.
    - Send raw & features to storage.

---

- Every n-rows, train new model on newest collected data.
    - Add it to the model registry.
    - Make it available to frontend users.

