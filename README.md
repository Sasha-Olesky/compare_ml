# install docker
apt-get install docker.io

# enable docker
systemctl start docker
systemctl enable docker

# docker build
sudo docker build -t="webapi" .

# docker run
sudo docker run -i -p 5000:5000 -p 8080:80 -t webapi
