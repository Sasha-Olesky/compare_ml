FROM python:3.5

# ENV VARIABLE_NAME DEFAULT_VALUE
ENV SERVER_HOME /opt/api
ENV APP_VERSION 1.2.0
ENV APP_NAME ML_IMAGE_COMPARE

RUN apt-get update &&\
    apt-get install -y python-opencv build-essential  &&\
    apt-get install -y lsb-release &&\
    apt-get install -y apt-transport-https &&\
    apt-get clean

RUN pip3 install tensorflow &&\
    pip3 install opencv-python &&\
    pip3 install cmake &&\
    pip3 install face-recognition &&\
    pip3 install pillow &&\
    pip3 install scipy &&\
    pip3 install requests &&\
    pip3 install scikit-image &&\
    pip3 install scikit-learn &&\
    pip3 install google-cloud-pubsub &&\
    pip3 install --upgrade google-cloud-storage &&\
    pip3 install flask

COPY . ${SERVER_HOME}
WORKDIR ${SERVER_HOME}

ENTRYPOINT [ "python3" ]
CMD [ "server.py" ]
