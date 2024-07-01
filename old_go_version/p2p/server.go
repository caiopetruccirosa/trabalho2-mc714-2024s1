package p2p

import (
	"context"
	"flag"
	"fmt"
	"log"
	"net"

	"google.golang.org/grpc"
	pb "trabalho2.mc714.2024s1/grpc"
)

var (
	base_port = flag.Int("base_port", 8888, "The base port of all servers")
	server_id = flag.Int("server_id", 0, "The id of the server")
)

type senderServer struct {
	pb.UnimplementedSenderServer
}

func (s *senderServer) SendRequest(ctx context.Context, in *pb.Request) (*pb.Response, error) {
	return &pb.Response{Value: "Hello " + in.Name + ", this is server"}, nil
}

func newServer() *senderServer {
	return &senderServer{}
}

func Serve() {
	flag.Parse()

	port := *base_port + *server_id
	lis, err := net.Listen("tcp", fmt.Sprintf("localhost:%d", port))
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	var opts []grpc.ServerOption
	grpcServer := grpc.NewServer(opts...)

	senderServer := newServer()

	pb.RegisterSenderServer(grpcServer, senderServer)
	grpcServer.Serve(lis)
}
