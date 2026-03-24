# Useful Docker commands

## General

* `docker pull`: Copy docker image as a copy to local
* `docker images`: List available images on the local machine
* `docker ps`: List running containers

## Run container

```
# this is just an example, don't run this
docker run -d -p hostport:containerport namespace/name:tag

# example
docker run -d -p 8965:80 docker/getting-started:latest

# run without any network access
docker run --network none
```

* -d: Run in detached mode (doesn't block your terminal)
* -p: Publish a container's port to the host (forwarding)
* hostport: The port on your local machine
* containerport: The port inside the container
* namespace/name: The name of the image (usually in the format username/repo)
* tag: The version of the image (often latest)


## Running multiple containers

```
i.e.:
docker run -d -p 8965:80 docker/getting-started
docker run -d -p 8966:80 docker/getting-started
docker run -d -p 8967:80 docker/getting-started
docker run -d -p 8968:80 docker/getting-started
docker run -d -p 8969:80 docker/getting-started

We use port 80 within each container because that's the port 
that the application is binding to inside the container. 
It's being forwarded to the different ports we specify on the 
host (our) machine.
```


## Stop container

* docker stop: This stops the container by issuing a SIGTERM signal 
to the container. You'll typically want to use docker stop.
* docker kill: This stops the container by issuing a SIGKILL signal 
to the container. This is a more forceful way to stop a container, 
and should be used as a last resort.

If I restart the stopped container, it will have the changes I made. 
This is only worth mentioning because sometimes developers think that 
killing an old container and starting a new one is the same as restarting 
a process - but that's not true... it's more like resetting the state of 
the entire machine to the original image.

Run `docker ps` to list running containers and use the `container id` with 
`docker stop <CONTAINER ID>` to stop the container


## Volumes


Docker does have ways to support "persistent state" through storage 
volumes. They're basically a filesystem that lives outside the 
container, but can be accessed by the container.

### General

* `docker volume create <name of the volume>`: Create a new volume
* `docker volume ls`: List volumes
* `docker volume inspect <name of the volume`: see where it is on your local machine

#### Ghost

```
docker run -d -e NODE_ENV=development -e url=http://localhost:3001 -p 3001:2368 -v ghost-vol:/var/lib/ghost ghost
```

* -d runs the image in detached mode to avoid blocking the terminal.
* -e NODE_ENV=development sets an environment variable within the container. This tells Ghost to run in "development" mode (rather than "production", for instance)
* -e url=http://localhost:3001 sets another environment variable, this one tells Ghost that we want to be able to access Ghost via a URL on our host machine.
We've used -p before. -p 3001:2368 does some port-forwarding between the container and our host machine.
* -v ghost-vol:/var/lib/ghost mounts the ghost-vol volume that we created before to the /var/lib/ghost path in the container. Ghost will use the /var/lib/ghost directory to persist stateful data (files) between runs.

A container's file system is read-write, but when you delete a container, and start 
a new one from the same image, that new container starts from scratch again with a 
copy of the image. All stateful changes are lost.
A volume's file system is read-write, but it lives outside a single container. If a 
container uses a volume, then stateful changes can be persisted to the volume even if 
the container is deleted.
Volumes are often used by applications like Ghost, Grafana, or WordPress to persist data 
so that when a container is deleted and a new one is created the state of the application 
isn't lost. Containerized applications are typically thought of as ephemeral (temporary). 
If your application breaks just because you deleted and recreated a container... it's 
not a very good containerization!

## Exec

### One-off exec

When it comes to deploying applications with Docker, you'll usually just let the container do its 
thing. For example, the Ghost container we ran in the last chapter started up its own web server 
(based on the image configuration). We didn't need to run any manual commands in addition to just 
starting the container.

That said, it is possible to run commands inside a running container! It's kinda like the container
version of sshing into a remote server and running a command.

```
# get container id
docker ps

# list files inside docker container
docker exec <container id> ls
```

### Live shell exec

Being able to run one-off commands is nice, but it's often more convenient to start a shell session
running within the container itself. Thats where the -i and -t flags come in:

* -i makes the exec command interactive
* -t gives us a tty (keyboard) interface

* Running /bin/sh gives us a shell session inside the container

```docker exec -it CONTAINER_ID /bin/sh```

Exit the shell session with the `exit` command

## Networks

###  General

This is a very common setup in backend architecture. The load balancer is exposed to the public 
internet, but the application servers are only accessible via the load balancer.

```
# create network
docker network create <network name>

# list networks
docker network ls
```

If we create container using the name tag like:

`   docker run -d --name caddy1 --network caddytest -v $PWD/index1.html:/usr/share/caddy/index.html caddy`

and we open a shell session within a network container like:

`docker run -it --network caddytest docker/getting-started /bin/sh`

then Docker has set up name resolution for us! The container names resolve to the individual containers 
from all other containers on the network, so smth like `curl caddy1`works.

### Load balancers and Caddy files

Creating a Caddy file like:

```
localhost:80

reverse_proxy caddy1:80 caddy2:80 {
lb_policy       round_robin
}
```

This tells Caddy to run on localhost:80, and to round robin any incoming traffic to 
caddy1:80 and caddy2:80. Remember, this only works because we're going to run the 
loadbalancer on the same network, so caddy1 and caddy2 will automatically resolve to our 
application server's containers.

We can start the load balancer like:

`docker run -d --network caddytest -p 8880:80 -v $PWD/Caddyfile:/etc/caddy/Caddyfile caddy`

## DockerFiles

Docker images are built from Dockerfiles. A Dockerfile is just a text file that contains
all the commands needed to assemble an image. It's essentially the "Infrastructure as Code" (IaC)
for an image. It runs commands from top to bottom, kind of like a shell script.

```
# build docker image from Dockerfile
docker build . -t helloworld:latest
```

The -t helloworld:latest flag tags the image with the name "helloworld" and the "latest" tag. 
Names are used to organize your images, and tags are used to keep track of different versions.

## Logs

When containers are running in detached mode with the -d flag, you don't see any output in your 
terminal, which is nice for keeping your terminal clean, but what if something goes wrong?

Enter the docker logs command.

i.e.: 
`docker run -d --name logdate alpine sh -c 'while true; do echo "LOGGING: $(date)"; sleep 1; done`

The sh -c 'while true; do echo "LOGGING: $(date)"; sleep 1; done' part is just a simple shell
script to execute inside the container that prints the current date and time every second.
`

Show the logs:
`docker logs <container id>`

See last 5 logs:
`docker logs --tail 5 <container id>`

See logs in real time:
`docker logs <container id> -f`

## Stats

* Run `docker stats` to see resource utilization of all running docker containers
* Run `docker top <container id>` to see the processes inside a container

## Resource limits

With `docker run` we can define resource allocation limits for a container, i.e.:

```
docker run -d --cpus="0.25" --name cpu-stress alexeiled/stress-ng --cpu 2 --timeout 10m
```

## Publishing to Docker Hub

* Build docker image: `docker build . -t <docker hub username>/<container name>`

* Push docker image to docker hub: `docker push <docker hub username>/<container name>`


## Tags

With Docker, a tag is a label that you can assign to a specific version of an image, 
similar to a tag in Git.

The latest tag is the default tag that Docker uses when you don't specify one. It's a 
convention to use latest for the most recent version of an image, but it's also common 
to include other tags, often semantic versioning tags like 0.1.0, 0.2.0, etc.

## Latest tag
If you look closely, you'll notice that your old version is tagged "latest"... that's a bit 
confusing. As it turns out, the latest tag doesn't always indicate that a specific tag is the 
latest version of an image. In reality, latest is just the default tag that's used if you don't 
explicitly supply one. We didn't use a tag on our first version, that's why it was tagged with 
"latest".

Should I Use “latest”?
The convention I'm familiar with is to use semantic versioning on all your images, but to also 
push to the "latest" tag on your most recent image. That way you can keep all of your old 
versions around, but the latest tag still always points to the latest version.

So, for example, if I were updating an application to version 5.4.6, I would probably do it like 
this:

```
docker build -t bootdotdev/awesomeimage:5.4.6 -t bootdotdev/awesomeimage:latest .
docker push bootdotdev/awesomeimage --all-tags
```

## The Bigger Picture
This is the last lesson, but before we go, I want to reiterate how Docker fits into the software development lifecycle, particularly at modern "DevOpsy" tech companies, because it's really important to understand.

The Deployment Process
The developer (you) writes some new code
The developer commits the code to Git
The developer pushes a new branch to GitHub
The developer opens a pull request to the main branch
A teammate reviews the PR and approves it (if it looks good)
The developer merges the pull request
Upon merging, an automated script, perhaps a GitHub action, is started
The script builds the code (if it's a compiled language)
The script builds a new docker image with the latest program
The script pushes the new image to Docker Hub
The server that runs the containers, perhaps a Kubernetes cluster, is told there is a new version
The k8s cluster pulls down the latest image
The k8s cluster shuts down old containers as it spins up new containers of the latest image
It's Never the Same
While the deployment process I've outlined above is a common one, especially at newer "cloud native" companies, two companies rarely have identical processes. Instead of GitHub, it might be GitLab. Instead of Docker Hub, it might be ECR. Instead of Kubernetes, it might be Docker Swarm or a more managed service.

That said, I hope this helps give you an idea of what to expect in the wild.


