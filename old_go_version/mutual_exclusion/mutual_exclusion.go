package mutual_exclusion

import (
	"fmt"
	"sync"
	"time"
)

func Execute_Mutex_Example() {
	// create mutex
	var mutex = &sync.Mutex{}

	// Create a wait group to synchronize goroutines
	wg := &sync.WaitGroup{}

	// Number of goroutines
	numGoroutines := 5

	// Add goroutines to the wait group
	wg.Add(numGoroutines)

	// Start goroutines
	for i := 0; i < numGoroutines; i++ {
		go func(id int) {
			// Acquire the lock
			mutex.Lock()

			// Critical section
			fmt.Printf("Goroutine %d entrou na seção crítica\n", id)
			time.Sleep(1 * time.Second)
			fmt.Printf("Goroutine %d saiu da seção crítica\n", id)

			// Release the lock
			mutex.Unlock()

			// Notify the wait group that the goroutine is done
			wg.Done()
		}(i)
	}

	// Wait for all goroutines to finish
	wg.Wait()

	fmt.Println("All goroutines have finished")
}
