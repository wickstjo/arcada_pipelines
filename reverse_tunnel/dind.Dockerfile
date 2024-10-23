FROM docker:27-dind-rootless

# REQUIRED FOR DOCKER APK & DOCKER MOUNTIN G
USER root

# UPDATE APK
RUN apk update && apk upgrade

# INSTALL APK DEPENDENCIES
RUN apk add --no-cache openssh-server openssh-client
RUN apk add --no-cache bash nano git wget curl make net-tools make screen sshpass

# SETUP SSH LOGIN CREDENTIALS
RUN mkdir /var/run/sshd
RUN echo 'root:pass123#' | chpasswd

# GENERATE SSH KEYGEN TO ENABLE SSH SERVICE
RUN ssh-keygen -A

# ALLOW ROOT ACCESS VIA SSH
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

# START THE SSH SERVICE & EXPOSE ITS PORT
# RUN service ssh start
EXPOSE 22

# COPY OVER FILES FOR REVERSE SSH TUNNEL
RUN mkdir /cluster
COPY password.txt /cluster/password.txt
COPY 01_create_ssh_tunnel.sh /cluster/create_ssh_tunnel.sh

CMD ["dockerd-entrypoint.sh"]