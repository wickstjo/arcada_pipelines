from typing import Dict, Any, Callable, TypeAlias
from types import SimpleNamespace

########################################################################################################
########################################################################################################

### TODO: MAKE THESE BETTER
KAFKA_DICT: TypeAlias = Dict[str, Any]
KAFKA_PUSH_FUNC: TypeAlias = Callable[[str, KAFKA_DICT], None]
CASSANDRA_INSTANCE: TypeAlias = Callable

########################################################################################################
########################################################################################################

# CONVERT DICT TO CLASS NAMESPACE
def TO_NAMESPACE(d):
    if isinstance(d, dict):
        # Recursively convert the dictionary to a namespace
        for key, value in d.items():
            if isinstance(value, dict):
                d[key] = TO_NAMESPACE(value)
            elif isinstance(value, list):
                # Process each item in the list
                d[key] = [TO_NAMESPACE(item) if isinstance(item, dict) else item for item in value]
        return SimpleNamespace(**d)
    elif isinstance(d, list):
        # Process a list if the outermost structure is a list
        return [TO_NAMESPACE(item) if isinstance(item, dict) else item for item in d]
    else:
        # If d is neither a dict nor a list, return it as is
        return d