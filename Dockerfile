FROM golang:1.18-alpine AS build_server
WORKDIR /server

COPY ./server .

RUN apk add --no-cache zeromq-dev musl-dev pkgconfig alpine-sdk libsodium-dev libzmq-static libsodium-static
RUN CGO_LDFLAGS="$CGO_LDFLAGS -lstdc++ -lm -lsodium" \
  CGO_ENABLED=1 \
  GOOS=linux \
  go build -v -a --ldflags '-extldflags "-static" -v' -o bin/server cmd/server/main.go

RUN go mod download
RUN go build -o /server cmd/server/main.go

FROM python:3.10 AS setup_client
WORKDIR /client

COPY ./client .
RUN pip3 install -r requirements.txt

WORKDIR /
ENV IPC_ENDPOINT ipc:///tmp/windiafaq.pipe
COPY .env.client .
COPY start.sh .

CMD [ "start.sh" ]
