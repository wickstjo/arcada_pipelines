FROM docker:27-dind-rootless

# REQUIRED FOR DOCKER APK & DOCKER MOUNTIN G
USER root

# UPDATE APK
RUN apk update && apk upgrade

# INSTALL APK DEPENDENCIES
RUN apk add --no-cache openssh-server openssh-client
RUN apk add --no-cache bash nano git wget curl make net-tools make screen

# SETUP SSH LOGIN CREDENTIALS
RUN mkdir /var/run/sshd
RUN echo 'root:pass' | chpasswd

# GENERATE SSH KEYGEN TO ENABLE SSH SERVICE
RUN ssh-keygen -A

# ALLOW ROOT ACCESS VIA SSH
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

# EXPOSE SSH PORT
EXPOSE 22

# MOUNT HOST MACHINES' DOCKER
CMD ["dockerd-entrypoint.sh"]

