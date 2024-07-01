package main

import (
	"fmt"
)

func main() {
	fmt.Println("Hello world!")

	// Primeiro iremos inicializar cada nó do sistema com seu próprio banco de dados

	// Depois iremos inicializar o algoritmo de consenso Raft

	// Sempre que um nó quiser escrever um valor no banco de dados, ele irá usar Relogio de Lamport para garantir a exclusão mútua
}
