FROM mongo:latest

RUN apt-get update && apt-get install -y python3 python3-pip

COPY ./src /code

RUN pip3 install -r code/requirements.txt
 
COPY ./data /data

WORKDIR code/

EXPOSE 5000

