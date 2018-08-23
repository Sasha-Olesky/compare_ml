# install docker
sudo apt-get install docker.io

# enable docker
sudo systemctl start docker

sudo systemctl enable docker

# docker build
sudo docker build -t="webapi" .

# docker run
sudo docker run -i -p 5000:5000 -t webapi

