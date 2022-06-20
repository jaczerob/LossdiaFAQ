FROM python:3.10 AS setup_client

ENV IPC_ENDPOINT ipc:///tmp/windiafaq.pipe
COPY . .

WORKDIR /client
RUN pip3 install -r requirements.txt

WORKDIR /
RUN chmod +x start.sh
CMD [ "start.sh" ]
