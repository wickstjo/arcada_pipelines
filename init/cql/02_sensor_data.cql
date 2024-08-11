CREATE TABLE IF NOT EXISTS surface_data.sensor_1A (
    timestamp text,
    serial_number text,
    vector list<double>,
    PRIMARY KEY(timestamp, serial_number)
);