# Use the official Docker-in-Docker image as the base
FROM docker:27.3.1-dind

# Install necessary packages
RUN apk add --no-cache git go make curl bash build-base libseccomp-dev musl-dev linux-headers

# RUN dockerd &

# # Set Go environment variables
# ENV GO111MODULE=on
# ENV GOPATH=/go
# ENV GOBIN=$GOPATH/bin
# ENV PATH=$PATH:$GOBIN

# # Install cri-dockerd
# RUN git clone https://github.com/Mirantis/cri-dockerd.git $GOPATH/src/github.com/Mirantis/cri-dockerd
# RUN cd $GOPATH/src/github.com/Mirantis/cri-dockerd
# RUN git checkout v0.3.1
# RUN make
# RUN cp bin/cri-dockerd /usr/local/bin/
# RUN cp -r cri-docker.service /etc/systemd/system/
# RUN mkdir -p /etc/cri-dockerd

# Start the Docker daemon
CMD ["dockerd"]
