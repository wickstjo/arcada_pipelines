#########################################################################
### DOCKER ENVIRONMENTS

docker.cpu_env:
	clear && cd 00_docker_env && docker compose -f cpu_compose.yml up --force-recreate --renew-anon-volumes --remove-orphans

docker.gpu_env:
	clear && cd 00_docker_env && docker compose -f gpu_compose.yml up --force-recreate --renew-anon-volumes --remove-orphans

#########################################################################
### INSTALL PYTHON DEPENDENCIES

PYTHON_ROOT = 03_python
# VIRTUAL_ENV_NAME = py_env

install:
	cd $(PYTHON_ROOT) && pip install -r requirements.txt

# env.install:
# 	cd $(PYTHON_ROOT)
# 	python3 -m venv $(VIRTUAL_ENV_NAME)
# 	$(VIRTUAL_ENV_NAME)/bin/pip install -r $(PYTHON_ROOT)/requirements.txt

# end.activate:
# 	source $(PYTHON_ROOT)/$(VIRTUAL_ENV_NAME)/bin/activate

#########################################################################
### BACKEND API

BACKEND_DIR = 00_backend
BACKEND_PREFIX = clear && cd $(PYTHON_ROOT) && python3 -m $(BACKEND_DIR)

backend.start:
	$(BACKEND_PREFIX).main

backend.create:
	$(BACKEND_PREFIX).create

#########################################################################
### PIPELINE COMPONENTS

PIPELINE_DIR = 01_pipeline
PIPELINE_PREFIX = clear && cd $(PYTHON_ROOT) && python3 -m $(PIPELINE_DIR)

pipeline.historical_ingest:
	$(PIPELINE_PREFIX).00_historical_ingest

pipeline.gradual_ingest:
	$(PIPELINE_PREFIX).01_gradual_ingest

pipeline.data_refinery:
	$(PIPELINE_PREFIX).02_data_refinery

pipeline.model_dispatch:
	$(PIPELINE_PREFIX).03_model_dispatch

pipeline.decision_synthesis:
	$(PIPELINE_PREFIX).04_decision_synthesis

pipeline.drift_analysis:
	$(PIPELINE_PREFIX).05_drift_analysis

pipeline.full:
	./$(PYTHON_ROOT)/$(PIPELINE_DIR)/tmux.sh

#########################################################################
### GIT PUSH SHORTHAND

push:
	@echo "Commit message?"; \
	read msg; \
	git add -A; \
	git commit -m "$$msg"; \
	git push origin main