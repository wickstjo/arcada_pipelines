#######################################################################################
### INSTALL KUBERNETES & ITS DEPENDENCIES

# INSTALL EACH PART BACK TO BACK
install.full:
	make install.00_ubuntu_deps
	make install.01_docker
	make install.02_go
	make install.03_docker_cri
	make install.04_kubernetes

# INSTALL BASELINE UBUNTU DEPENDENCIES
install.00_ubuntu_deps:
	sudo apt-get install -y openssh-server openssh-client
	sudo apt-get install -y nano git wget curl make net-tools make golang-go

# INSTALL DOCKER
install.01_docker:
	curl -fsSL https://get.docker.com -o get-docker.sh
	sudo sh test-docker.sh

	sudo usermod -aG docker $(USER)
	newgrp docker

	sudo systemctl enable docker.service
	sudo systemctl enable containerd.service

	docker version
	docker run hello-world

# INSTALL GO-LANG
# IF THE GO REFERENCE FAILS, MANUALLY ENTER THE FOLLOWING: source ~/.bashrc
# IN A FRESH TERMINAL WINDOP
install.02_go:
	mkdir -p temp
	cd temp && wget https://go.dev/dl/go1.21.3.linux-amd64.tar.gz
	cd temp && sudo tar -C /usr/local -xzf go1.21.3.linux-amd64.tar.gz

	cd temp && export PATH=$$PATH:/usr/local/go/bin
	cd temp && echo "export PATH=$$PATH:/usr/local/go/bin" >> ~/.bashrc
	. ~/.bashrc
	. ~/.bashrc && go version
	sudo rm -rf temp

# INSTALL DOCKER_CRI (KUBE API)
install.03_docker_cri:
	mkdir -p temp
	cd temp && git clone https://github.com/Mirantis/cri-dockerd.git
	mkdir -p /usr/local/bin
	cd temp/cri-dockerd && make cri-dockerd

	cd temp/cri-dockerd && sudo install -o root -g root -m 0755 cri-dockerd /usr/local/bin/cri-dockerd
	cd temp/cri-dockerd && sudo install packaging/systemd/* /etc/systemd/system
	cd temp/cri-dockerd && sudo sed -i -e 's,/usr/bin/cri-dockerd,/usr/local/bin/cri-dockerd,' /etc/systemd/system/cri-docker.service

	sudo systemctl daemon-reload
	sudo systemctl enable --now cri-docker.socket
	cri-dockerd --version
	sudo rm -rf temp

# INSTALL KUBERNETES COMPONENTS
install.04_kubernetes:
	sudo apt-get update
	sudo apt-get install -y apt-transport-https ca-certificates curl gpg
	curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.28/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
	echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.28/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list

	sudo apt-get update
	sudo apt-get install -y kubelet kubeadm kubectl
	sudo apt-mark hold kubelet kubeadm kubectl

	kubelet --version
	kubeadm version

#######################################################################################
### CREATE CLUSTER NODES

# CREATE CLUSTER MASTER NODE
# MAKE SURE FIREWALL IS OFF -- systemctl stop firewalld, sudo systemctl disable firewalld
cluster.master:
	sudo swapoff -a
	sudo modprobe br_netfilter

	sudo kubeadm init \
		--cri-socket=unix:///var/run/cri-dockerd.sock \
		--pod-network-cidr=10.0.0.0/8 \
		--kubernetes-version v1.28.15

	mkdir -p $(HOME)/.kube
	sudo cp -f /etc/kubernetes/admin.conf $(HOME)/.kube/config
	sudo chown $(USER) $(HOME)/.kube/config

	mkdir -p temp
	cd temp && curl https://raw.githubusercontent.com/projectcalico/calico/v3.26.3/manifests/calico.yaml -O
	kubectl apply -f temp/calico.yaml
	sudo rm -rf temp

	kubectl get pods -A --watch

# FULLY RESET A NODE BEFORE RE JOIN/INSTALL
cluster.reset_node:
	sudo kubeadm reset --cri-socket=unix:///var/run/cri-dockerd.sock
	sudo rm -rf $(HOME).kube

# UPDATE THESE BASED ON YOUR LATEST JOIN STRING
# UPDATE THESE BASED ON YOUR LATEST JOIN STRING
# UPDATE THESE BASED ON YOUR LATEST JOIN STRING
MASTER_IP=193.167.37.127
KUBE_TOKEN=7h47wy.h3v290yywof6ir8c
KUBE_HASH=bee1773670f647eedf7ad4a1a4a55f0e1528c8281ffe39a1d83d5b3629fdeb23

# ADD WORKER NODE TO CLUSTER
# MAKE SURE FIREWALL IS OFF -- systemctl stop firewalld, sudo systemctl disable firewalld
cluster.worker:
	sudo swapoff -a
	sudo modprobe br_netfilter

	sudo kubeadm join $(MASTER_IP):6443 \
		--token $(KUBE_TOKEN) \
		--discovery-token-ca-cert-hash sha256:$(KUBE_HASH) \
		--cri-socket=unix:///var/run/cri-dockerd.sock

#######################################################################################
### KUBERNETES COMMAND SHORTCUTS

kube.join_string:
	kubeadm token create --print-join-command

kube.pods:
	clear && kubectl get pods -A --watch

kube.nodes:
	clear && kubectl get nodes --watch

kube.relabel:
	kubectl label nodes 3080-ubu kubernetes.io/role=worker
	kubectl label nodes 4090-ubu kubernetes.io/role=worker

kube.alloc:
	kubectl describe nodes | grep -A 5 "Allocatable"

kube.apply:
	kubectl apply -f $(f) && kubectl get pods -A -w