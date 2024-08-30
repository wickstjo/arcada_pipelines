import h5py, json, os
from misc import log

# CHECK WHETHER RESOURCE EXISTS
def resource_exists(path):
    if not os.path.exists(path):
        log(f"RESOURCE NOT FOUND ({path})")
        return False
    
    log(f"RESOURCE FOUND ({path})")
    return True

# READ & PARSE HDF5 DATASET
def load_dataset(yolo_args):
    container = []

    # MAKE SURE THE HDF5 DATASET EXISTS
    if not resource_exists(f'./datasets/{yolo_args.dataset}.hdf5'):
        log(f'THE DATASET ({yolo_args.dataset}) COULD NOT BE LOCATED, TERMINATING..')
        return False, []

    # EXTRACT DATASET COMPONENTS
    dataset = h5py.File(f'./datasets/{yolo_args.dataset}.hdf5', 'r')
    activity = dataset['is_enabled']
    sensors = dataset['sensors']
    metadata = json.loads(dataset['metadata'][()])
    n_frames = metadata["n_frames"]

    # COLLECT SENSOR COMPONENTS
    for nth_iter in range(yolo_args.repeat):
        sensor_names = list(dataset["sensors"].keys())
        sensor_data_iters = {key: iter(sensors[key]) for key in sensor_names}

        if yolo_args.max_frames > 0:
            n_frames = min(n_frames, yolo_args.max_frames)

        for frame in range(n_frames):
            frame_data = {}

            # FILL THE CURRENT FRAME
            for sensor_name, data_iter in sensor_data_iters.items():
                active = activity[sensor_name][frame]

                # Sensor has data for this frame only if it is marked as active
                if active:
                    sensor_data = next(data_iter)
                    frame_data[sensor_name] = sensor_data

                    container.append(sensor_data)

    dataset.close()
    return True, container