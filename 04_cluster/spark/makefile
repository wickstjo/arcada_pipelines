build_image:
	# docker build -t spark-gpu .
	docker build -t bitnami-spark-with-gpu .

worker:
	docker build -t bitnami-spark-with-gpu .
	docker run --gpus all --privileged bitnami-spark-with-gpu spark://193.167.37.47:7077

exec:
	docker exec -it gpu_worker /bin/bash

cpu_spark:
	clear && docker compose -f default_spark.yml up --force-recreate --renew-anon-volumes --remove-orphans

gpu_spark:
	clear && docker compose -f gpu_spark.yml up --force-recreate --renew-anon-volumes --remove-orphans
