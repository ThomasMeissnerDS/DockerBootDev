FROM debian:stable-slim

# COPY source destination --> this is the go binary of the server
COPY DockerBootDev /bin/DockerBootDev

ENV PORT=8991

CMD ["/bin/DockerBootDev"]