package p2p

import (
	"flag"
	"log"

	"google.golang.org/grpc"
	pb "trabalho2.mc714.2024s1/grpc"
)

var (
	serverAddr = flag.String("addr", "localhost:50051", "The server address in the format of host:port")
)

func GetClient() pb.SenderClient {
	flag.Parse()

	var opts []grpc.DialOption
	conn, err := grpc.NewClient(*serverAddr, opts...)

	if err != nil {
		log.Fatalf("failed to dial: %v", err)
	}

	defer conn.Close()

	client := pb.NewSenderClient(conn)

	return client
}
