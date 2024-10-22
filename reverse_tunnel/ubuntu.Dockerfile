FROM ubuntu:24.04

# MAKE INSTALL NON-INTERACTIVE
ENV DEBIAN_FRONTEND=noninteractive

#########################################################################################

# UPGRADE APT
RUN apt-get update -y && apt-get upgrade -y

# INSTALL BASIC PACKAGES
RUN apt-get install -y openssh-server openssh-client
RUN apt-get install -y nano git wget curl make net-tools make apt-utils

# SETUP SSH LOGIN CREDENTIALS
RUN mkdir /var/run/sshd
RUN echo 'root:pass' | chpasswd

# ALLOW ROOT ACCESS VIA SSH
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

# START THE SSH SERVICE & EXPOSE ITS PORT
# RUN service ssh start
EXPOSE 22

#########################################################################################

RUN mkdir CLUSTER
WORKDIR /CLUSTER

# CMD ["/usr/sbin/sshd", "-D"]
CMD ["/bin/bash"]


# docker build -t ubuntu_testing .
# docker run -it ubuntu_testing

