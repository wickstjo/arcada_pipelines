LD_PRELOAD=/opt/bitnami/common/lib/libnss_wrapper.so
SPARK_WORKER_OPTS=”-Dspark.worker.resource.gpu.amount=2 -Dspark.worker.resource.gpu.discoveryScript=/opt/bitnami/spark/getGpusResources.sh”