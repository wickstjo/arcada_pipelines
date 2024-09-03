from typing import Dict, Any, Callable, TypeAlias

# TYPE ALIASES
KAFKA_DICT: TypeAlias = Dict[str, Any]
KAFKA_PUSH_FUNC: TypeAlias = Callable[[str, KAFKA_DICT], None]