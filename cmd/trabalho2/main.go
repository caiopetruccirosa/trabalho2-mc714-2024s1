package main

import (
	"fmt"

	"trabalho2.mc714.2024s1/lamport_clock"
	"trabalho2.mc714.2024s1/leader_election"
	"trabalho2.mc714.2024s1/mutual_exclusion"
)

func main() {
	fmt.Println("Esse é o Trabalho 2 de MC714!")

	lamport_clock.Execute_Lamport_Clock_Example()
	leader_election.Execute_Leader_Election_Example()
	mutual_exclusion.Execute_Mutex_Example()
}
