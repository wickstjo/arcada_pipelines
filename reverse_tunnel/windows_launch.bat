SET DOCKERFILE=dind.Dockerfile
SET DOCKER_IMAGE=cluster_node_img
SET CONTAINER_NAME=cluster_node

REM BUILD THE CONTAINER
docker build -t %DOCKER_IMAGE% -f %DOCKERFILE% .

REM START THE CONTAINER
docker run -d --rm --privileged --name %CONTAINER_NAME% %DOCKER_IMAGE%

REM START THE REVERSE TUNNEL -- INSIDE OF CONTAINER
docker exec %CONTAINER_NAME% /bin/bash /cluster/create_ssh_tunnel.sh