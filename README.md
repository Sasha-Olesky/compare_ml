# ml-image-compare

## using docker

build image:

```bash
docker build -t ml-image-compare .
```

pull image from gcr:

```bash
gcloud docker -- pull gcr.io/audotto/ml-image-compare:latest
```

run localy for development:

```bash
docker run -v ~/workspace/ml-image-compare:/opt/api -e IMAGE_BASE_URL=http://localhost:80 -p 5000:5000 -it --entrypoint bash gcr.io/audotto/ml-image-compare
python3 server.py
```

where:

- mount source folder into container: `-v ~/workspace/ml-image-compare:/opt/api`
- pass env variable into container `-e IMAGE_BASE_URL=http://localhost:80`
- publish API port: `-p 5000:5000`
- run bash insrtead of python: ` -it --entrypoint bash`
- run API after container starts:  `python3 server.py`
 
run localy for test:

```bash
docker run -p 5000:5000 gcr.io/audotto/ml-image-compare
```

### container variables

|name|description|default|
|----|-----------|-------|
|IMAGE_BASE_PATH|where to save images.This folder will be accessible from web server |/var/www/html|
|IMAGE_BASE_URL|base URL of webserver. for exapmle: http://ml-image-compare:8080. It used to build Image URL| your public IP from https://api.ipify.org|
|SERVER_HOME| docker WORKDIR folder |/opt/api|
|APP_VERSION| Application engine version |1.0.0|
|APP_NAME| Application name  |ML_IMAGE_COMPARE|

## install to kubernetes

### install/upgrade

```bash
helm upgrade -i ml-image-compare ./chart/ml-image-compare --set secret.data=$(cat google_creds.json | base64 -w 0)
```

where __google_creds.json__ is service account certificate

### delete

```bash
helm delete --purge ml-image-compare
```

### chart variables

|name|description|default|
|----|-----------|-------|
|replicaCount|| 1
|nginx.image.repository|| nginx
|nginx.image.pullPolicy||IfNotPresent
|nginx.imagePath|nginx www home|/usr/share/nginx/html
|nginx.service.port|nginx port|8080
|nginx.service.targetPort||80
|nginx.resources||{}
|image.repository||gcr.io/audotto/ml-image-compare
|image.pullPolicy||Always
|imagePath|see IMAGE_BASE_PATH|/var/www/html
|service.type||ClusterIP
|service.port|API port|5000
|service.targetPort||5000
|secret.data|b64 encoded json certificate| "place google credentials here"
|resources||{}
|nodeSelector||{}
|tolerations||[]
|affinity||{}
