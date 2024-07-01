package main

import (
	"flag"
	"fmt"
	"log"
	"net"

	"google.golang.org/grpc"
	pb "trabalho2.mc714.2024s1/grpc"
	"trabalho2.mc714.2024s1/storage"
)

func main() {
	flag.Parse()
	fmt.Println("This is the server for the MC714 second assignment!")

	lis, err := net.Listen("tcp", ":50051") // Change the port if needed
    if err != nil {
        log.Fatalf("failed to listen: %v", err)
    }
	
	s := grpc.NewServer()
    pb.RegisterStorageServiceServer(s, storage.NewDatastore())

    log.Println("gRPC server listening on port 50051")
    if err := s.Serve(lis); err != nil {
        log.Fatalf("failed to serve: %v", err)
    }


	fmt.Println("Finishing server for the MC714 second assignment.")
}
