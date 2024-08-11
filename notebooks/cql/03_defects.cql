CREATE TABLE IF NOT EXISTS surface_data.defects (
    timestamp text,
    tensor_hash text,
    cable_sector text,
    tile_max double,
    tile_min double,
    tile_delta double,
    tile_mean double,
    n_defects int,
    PRIMARY KEY(timestamp, cable_sector, tensor_hash)
);