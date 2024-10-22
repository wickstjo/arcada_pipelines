# ON THE MOST MACHINE -- CREATE & RUN CONTAINER

# UBUNTU BASE
# docker build -t ubuntu_testing .
# docker run -it ubuntu_testing

# ALPINE DIND BASE
docker run -it --privileged ubuntu_testing
docker run -it ubuntu_testing