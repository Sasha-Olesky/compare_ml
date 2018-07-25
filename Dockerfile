FROM ubuntu

RUN apt-get update
RUN apt-get install -y python3-pip git apache2

FROM python:3.5
RUN  pip3 install tensorflow==1.3.0 &&\
     pip3 install opencv-python &&\
     pip3 install flask &&\
     pip3 install flask-restful &&\
     pip3 install cmake &&\
     pip3 install face-recognition &&\
     pip3 install pillow &&\
     pip3 install scipy &&\
     pip3 install requests

# download source from github
RUN git clone https://github.com/Sasha-Olesky/compare_ml.git
RUN cd compare_ml

ENV APACHE_PATH "$APACHE_PATH/var/www/html/"
RUN service apache2 start
RUN chmod 777 -R /var/www/html

RUN chmod +x /compare_ml/run.sh
CMD ./compare_ml/run.sh

EXPOSE 5000 80
