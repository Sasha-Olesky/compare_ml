# install docker
sudo apt-get install docker.io

# enable docker
sudo systemctl start docker

sudo systemctl enable docker

# docker build
sudo docker build -t="webapi" .

# docker run
sudo docker run -i -p 5000:5000 -p 8080:80 -t webapi

# you need to find out which port to connect:
sudo docker ps

sudo docker exec -t -i mycontainer /bin/bash

service apache2 start

