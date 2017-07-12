FROM python:2.7-slim

RUN mkdir -p /opt/diary
WORKDIR /opt/diary

# Copy files from build machine
COPY . .


RUN pip install /opt/diary

ENTRYPOINT ["diary"]
