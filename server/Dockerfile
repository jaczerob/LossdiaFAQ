FROM golang:1.18-alpine

WORKDIR /server
COPY . .

RUN apk update \
    && apk add --no-cache ca-certificates\
        git \
        gcc \
        g++ \
        pkgconfig \
        linux-headers \
        zeromq \
        zeromq-dev \
    && rm -rf /var/cache/apk/*

RUN go mod download
RUN CGO_ENABLED=1 go build -x -o server cmd/server/main.go

RUN chmod +x server
EXPOSE 8080

CMD [ "./server" ]
