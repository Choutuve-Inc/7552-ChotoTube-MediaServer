FROM ubuntu:latest
RUN apt-get update -y
RUN apt-get install -y python3
RUN apt-get install -y python3.7
RUN apt-get install -y python3-pip
COPY . /app
WORKDIR /app
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN pip3 install requests
ENTRYPOINT ["python3"]
CMD ["__init__.py"]