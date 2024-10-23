# BUILD THE CONTAINER
docker build -t cluster_node_img -f dind.Dockerfile .

# START THE CONTAINER
docker run -it --rm --privileged --name cluster_node cluster_node_img

# START THE REVERSE TUNNEL -- INSIDE OF CONTAINER
docker exec cluster_node /bin/bash /cluster/create_ssh_tunnel.sh