FROM golang:1.22.4-alpine AS builder

WORKDIR /build

# Git must be installed because go mod requires it to download dependencies
RUN apk --no-cache add git

COPY go.mod go.sum ./
RUN go mod tidy

COPY . .

RUN CGO_ENABLED=0 go build -ldflags '-extldflags "-static"' -o trabalho2-mc714 ./cmd/trabalho2/.

FROM alpine

WORKDIR /app
USER 1000
COPY --from=builder /build/trabalho2-mc714 .

ENTRYPOINT [ "/app/trabalho2-mc714" ]