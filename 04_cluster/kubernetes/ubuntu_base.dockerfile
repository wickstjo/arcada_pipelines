FROM ubuntu:24.04

# MAKE INSTALL NON-INTERACTIVE
ENV DEBIAN_FRONTEND=noninteractive

#########################################################################################
#########################################################################################

# UPGRADE APT
RUN apt-get update && apt-get upgrade

# INSTALL BASIC PACKAGES
RUN apt-get install -y openssh-server openssh-client
RUN apt-get install -y nano git wget curl make net-tools make apt-utils

RUN mkdir CLUSTER
WORKDIR /CLUSTER

#########################################################################################
#########################################################################################

# INSTALL DOCKER COMPONENTS
# REMEMBER: WE HAVE MOUNTED THE HOST SYSTEMS' DOCKER CRI
RUN curl -fsSL https://get.docker.com -o get-docker.sh
RUN chmod +x get-docker.sh && sh get-docker.sh

# MAKE SURE DOCKER WORKS
# RUN docker version
# RUN docker run hello-world

#########################################################################################
#########################################################################################

# # DOWNLOAD & INSTALL GO-LANG
# RUN wget https://go.dev/dl/go1.21.3.linux-amd64.tar.gz
# RUN tar -C /usr/local -xzf go1.21.3.linux-amd64.tar.gz

# # RUN export PATH=$PATH:/usr/local/go/bin
# RUN echo "export PATH=$PATH:/usr/local/go/bin" | cat >> ~/.bashrc
# ENV PATH="/usr/local/go/bin:${PATH}"
# RUN go version

#########################################################################################
#########################################################################################

# DOWNLOAD & INSTALL DOCKER CRI
# NECESSARY FOR KUBERNETES TO USE DOCKER
# MAKE SURE YOU HAVE 'MAKE' INSTALLED -- RUN apt install make
# RUN git clone https://github.com/Mirantis/cri-dockerd.git
# RUN cd cri-dockerd
# RUN make cri-dockerd
# RUN mkdir -p /usr/local/bin
# RUN install -o root -g root -m 0755 cri-dockerd /usr/local/bin/cri-dockerd
# RUN install packaging/systemd/* /etc/systemd/system
# RUN sed -i -e 's,/usr/bin/cri-dockerd,/usr/local/bin/cri-dockerd,' /etc/systemd/system/cri-docker.service
# RUN systemctl daemon-reload
# RUN systemctl enable --now cri-docker.socket

#########################################################################################
#########################################################################################

# ADD KUBE COMPONENT CERTS
RUN apt-get update
RUN apt-get install -y apt-transport-https ca-certificates curl gpg
RUN curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.28/deb/Release.key | gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg

# This overwrites any existing configuration in /etc/apt/sources.list.d/kubernetes.list
RUN echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.28/deb/ /' | tee /etc/apt/sources.list.d/kubernetes.list

# INSTALL KUBE & FREEZE ITS VERSION
RUN apt-get update
RUN apt-get install -y kubelet kubeadm kubectl
RUN apt-mark hold kubelet kubeadm kubectl

# CHECK THAT EVERYTHING IS OK
RUN kubelet --version
RUN kubeadm version

#########################################################################################
#########################################################################################

# TURN OF SWAP & FIREWALLS
# RUN swapoff -a
# systemctl stop firewalld
# RUN systemctl disable firewalld

# DEBUG: INVERSE THE PREVIOUS ACTIONS
# RUN swapon -a
# systemctl start firewalld
# RUN systemctl enable firewalld


kubeadm init --cri-socket=unix:///var/run/cri-dockerd.sock --pod-network-cidr=10.0.0.0/8

# INITIALIZE THE CLUSTERS CONTROL PLANE (MASTER NODE)
# RUN kubeadm init \
#   --cri-socket=unix:///var/run/cri-dockerd.sock \
#   --pod-network-cidr=10.0.0.0/8

# # MAKE THE NODE AVAILABLE
# RUN mkdir -p $HOME/.kube
# RUN cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
# RUN chown $(id -u):$(id -g) $HOME/.kube/config

# # INSTALL POD NETWORK ADDON
# # calico-kube-controllers IS GENERALLY THE LAST POD TO FINISH
# RUN curl https://raw.githubusercontent.com/projectcalico/calico/v3.26.3/manifests/calico.yaml -O
# RUN kubectl apply -f calico.yaml
# RUN kubectl get pods -A --watch

# # FINALLY, PRINT CLUSTER JOIN STRING
# RUN clear && kubectl get pods -A
# RUN kubeadm token create --print-join-command

#########################################################################################
#########################################################################################

# BOOT UP BASH
CMD ["/bin/bash"]
