NUM_GPUS=2
export SPARK_WORKER_OPTS="-Dspark.worker.resource.gpu.amount=$NUM_GPUS -Dspark.worker.resource.gpu.discoveryScript=/opt/bitnami/spark/conf/getGpusResources.sh"

export SPARK_WORKER_CORES=2
export SPARK_WORKER_MEMORY="2gb"