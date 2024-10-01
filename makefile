#########################################################################
### DOCKER ENVIRONMENT

docker.start_env:
	clear && cd 01_docker_env && docker compose up --force-recreate --renew-anon-volumes --remove-orphans

#########################################################################
### BACKEND API

BACKEND_PREFIX = clear && cd 02_backend_api && python3 

backend.start_api:
	$(BACKEND_PREFIX) main.py

backend.init:
	$(BACKEND_PREFIX) init.py

#########################################################################
### PIPELINE COMPONENTS

PIPELINE_PREFIX = clear && cd 03_pipeline && python3

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