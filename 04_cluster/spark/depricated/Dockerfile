# Use the official NVIDIA CUDA base image
FROM nvidia/cuda:11.8.0-runtime-ubuntu20.04

# Set environment variables for Spark
ENV SPARK_VERSION=3.5.3
# ENV HADOOP_VERSION=3.5.3
ENV HADOOP_VERSION=3

# Install dependencies
RUN apt-get update && apt-get install -y \
    openjdk-11-jdk \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Download and install Spark
RUN wget https://downloads.apache.org/spark/spark-$SPARK_VERSION/spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION.tgz \
    && tar -xvzf spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION.tgz \
    && mv spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION /opt/spark \
    && rm spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION.tgz

# Set Spark home
ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:$SPARK_HOME/bin

# Set entrypoint
CMD ["spark-class"]