# Use the Docker-in-Docker image
FROM docker:27.3.1-dind

# Set environment variables
ENV KUBE_VERSION=v1.27.3
ENV CRICTL_VERSION=v1.26.0

# Install required packages
RUN apk add --no-cache \curl \
    bash \
    iproute2 \
    iptables \
    socat \
    conntrack-tools \
    ca-certificates

# Install kubelet, kubectl, and kubeadm
RUN curl -LO "https://storage.googleapis.com/kubernetes-release/release/${KUBE_VERSION}/bin/linux/amd64/kubelet" && \
    chmod +x kubelet && \
    mv kubelet /usr/bin/ && \
    curl -LO "https://storage.googleapis.com/kubernetes-release/release/${KUBE_VERSION}/bin/linux/amd64/kubectl" && \
    chmod +x kubectl && \
    mv kubectl /usr/bin/ && \
    curl -LO "https://storage.googleapis.com/kubernetes-release/release/${KUBE_VERSION}/bin/linux/amd64/kubeadm" && \
    chmod +x kubeadm && \
    mv kubeadm /usr/bin/

# Install crictl
RUN curl -LO "https://github.com/kubernetes-sigs/cri-tools/releases/download/${CRICTL_VERSION}/crictl-${CRICTL_VERSION}-linux-amd64.tar.gz" && \
    tar -C /usr/local/bin -xzf "crictl-${CRICTL_VERSION}-linux-amd64.tar.gz" && \
    rm "crictl-${CRICTL_VERSION}-linux-amd64.tar.gz"

# Create crictl configuration
RUN mkdir -p /etc/crictl.yaml && \
    echo "runtime-endpoint: unix:///var/run/dockershim.sock" > /etc/crictl.yaml

# Set sysctl parameters for Kubernetes networking
RUN echo "net.bridge.bridge-nf-call-iptables=1" >> /etc/sysctl.conf && \
    echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf

# Entry point to keep the container running
CMD ["dockerd-entrypoint.sh"]

# docker run -it --privileged ubuntu_testing