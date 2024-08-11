CREATE KEYSPACE IF NOT EXISTS surface_data WITH replication = {
    'class': 'SimpleStrategy', 
    'replication_factor': 3
};