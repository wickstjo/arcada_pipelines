#########################################################################
### DOCKER ENVIRONMENT

docker.start_env:
	clear && cd 01_docker_env && docker compose up --force-recreate --renew-anon-volumes --remove-orphans

#########################################################################
### BACKEND API

BACKEND_DIR = 02_backend_api
BACKEND_PREFIX = clear && cd $(BACKEND_DIR) && python3 

backend.install:
	pip install -r $(BACKEND_DIR)/requirements.txt

backend.start_api:
	$(BACKEND_PREFIX) main.py

backend.create:
	$(BACKEND_PREFIX) create.py

#########################################################################
### PIPELINE COMPONENTS

PIPELINE_DIR = 03_pipeline
PIPELINE_PREFIX = clear && cd $(PIPELINE_DIR) && python3

pipeline.install:
	pip install -r $(PIPELINE_DIR)/requirements.txt

pipeline.historical_ingest:
	$(PIPELINE_PREFIX) 00_historical_ingest.py

pipeline.gradual_ingest:
	$(PIPELINE_PREFIX) 01_gradual_ingest.py

pipeline.data_refinery:
	$(PIPELINE_PREFIX) 02_data_refinery.py

pipeline.model_dispatcher:
	$(PIPELINE_PREFIX) 03_model_dispatch.py

#########################################################################
#########################################################################