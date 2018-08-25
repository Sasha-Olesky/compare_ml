FROM ubuntu:16.04

RUN apt-get update
RUN apt-get install -y python3-pip git

FROM python:3.5
RUN  pip3 install tensorflow &&\
     pip3 install opencv-python &&\
     pip3 install cmake &&\
     pip3 install face-recognition &&\
     pip3 install pillow &&\
     pip3 install scipy &&\
     pip3 install requests &&\
     pip3 install scikit-image &&\
     pip3 install scikit-learn &&\
	 pip3 install google-cloud-pubsub &&\
	 pip3 install google-cloud-storage

# download source from github
RUN git clone https://github.com/Sasha-Olesky/compare_ml.git
RUN cd compare_ml

RUN apt-get update
ENV APP_VERSION "$APP_VERSION 1.1.0 "
ENV APP_NAME "$APP_NAME ML_IMAGE_COMPARE "

RUN chmod +x /compare_ml/run.sh
CMD ./compare_ml/run.sh




