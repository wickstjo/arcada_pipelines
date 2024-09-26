from dataclasses import dataclass
import funcs.misc as misc

###################################################################################################
###################################################################################################

# KAFKA MQ TOPICS
@dataclass(frozen=True)
class kafka:
    DATA_REFINERY: str = 'data_refinery'
    MODEL_TRAINING: str = 'model_training'
    MODEL_INFERENCE: str = 'model_inference'
    MODEL_ANALYSIS: str = 'model_analysis'
    DECISION_SYNTHESIS: str = 'decision_synthesis'

###################################################################################################
###################################################################################################

# CASSANDRA DB TABLES
@dataclass(frozen=True)
class cassandra:
    STOCKS_TABLE: str = 'john.refined_stock_data'
    MODELS_TABLE: str = 'john.model_history'

###################################################################################################
###################################################################################################

# REDIS CACHE KEYSPACES
@dataclass(frozen=True)
class redis:
    MODEL_PIPELINES: str = 'model_pipelines'
    
###################################################################################################
###################################################################################################

# IMPORTANT DIRECTORIES
@dataclass(frozen=True)
class dirs:
    MODEL_REPO: str = 'model_repo'
    YAML_CONFIGS: str = '00_configs'

###################################################################################################
###################################################################################################

def global_config():
    data_dict: dict = misc.load_yaml('../00_configs/global_config.yaml')
    return misc.TO_NAMESPACE(data_dict)

###################################################################################################
###################################################################################################