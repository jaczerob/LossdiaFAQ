FROM python:3.10

WORKDIR /client
COPY . .
RUN pip3 install -r requirements.txt

WORKDIR /

CMD [ "python3", "." ]
