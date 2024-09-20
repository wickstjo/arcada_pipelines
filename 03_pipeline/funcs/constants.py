from dataclasses import dataclass

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

# IMPORTANT DIRECTORIES
@dataclass(frozen=True)
class dirs:
    MODEL_REPO: str = 'model_repo'
    YAML_CONFIGS: str = '00_configs'

###################################################################################################
###################################################################################################