package mutual_exclusion

import (
	"fmt"
	"sync"
	"time"
	lpc "lamport_clock"
)

type Process struct {
	id           int
	clock        *lpc.LamportClock
	requestQueue []int
	receivedOK   map[int]bool
	mutex        sync.Mutex
}

func (p *Process) ReceiveOK(senderID int) {
	p.mutex.Lock()
	defer p.mutex.Unlock()

	p.receivedOK[senderID] = true
	fmt.Printf("Process %d received OK from process %d\n", p.id, senderID)
}

func (p *Process) ReceiveRelease(releaserID int) {
	p.mutex.Lock()
	defer p.mutex.Unlock()

	fmt.Printf("Process %d received release from process %d\n", p.id, releaserID)

	// Remove the releaser from the request queue
	newQueue := []int{}
	for _, id := range p.requestQueue {
		if id != releaserID {
			newQueue = append(newQueue, id)
		}
	}
	p.requestQueue = newQueue
}

func (p *Process) sendOK(receiverID int) {
	// In a real implementation, this would be a network message.
	// Here, we simulate it by calling ReceiveOK on the receiver process directly.
	processes[receiverID].ReceiveOK(p.id)
}

func (p *Process) isIdle() bool {
	// Simulate checking if the process is idle (not accessing the resource and not wanting to)
	return true
}

func (p *Process) isAccessingResource() bool {
	// Simulate checking if the process is currently accessing the resource
	return false
}

var processes []*Process

func NewProcess(id int) *Process {
	return &Process{
		id:         id,
		clock:      lpc.NewLamportClock(),
		receivedOK: make(map[int]bool),
	}
}

func (p *Process) RequestCriticalSection(otherProcesses []*Process) {
	p.mutex.Lock()
	p.clock.Tick()
	requestTime := p.clock.GetClock()
	fmt.Printf("Process %d is requesting critical section at time %d\n", p.id, requestTime)
	p.mutex.Unlock()

	// Broadcast request to other processes
	for _, other := range otherProcesses {
		if other.id != p.id {
			other.ReceiveRequest(p.id, requestTime)
		}
	}

	// Wait for replies from all other processes
	for len(p.receivedOK) < len(otherProcesses)-1 {
		time.Sleep(100 * time.Millisecond)
	}

	// Enter critical section
	fmt.Printf("Process %d is entering critical section at time %d\n", p.id, p.clock.GetClock())
	time.Sleep(2 * time.Second) // Simulate time spent in critical section
	fmt.Printf("Process %d is leaving critical section at time %d\n", p.id, p.clock.GetClock())

	p.mutex.Lock()
	// Clear received OKs for next request
	p.receivedOK = make(map[int]bool)
	// Broadcast release to other processes
	for _, other := range otherProcesses {
		if other.id != p.id {
			other.ReceiveRelease(p.id)
		}
	}
	p.mutex.Unlock()
}

func (p *Process) ReceiveRequest(requesterID int, requestTime int) {
	p.mutex.Lock()
	p.clock.UpdateClock(requestTime)
	p.clock.Tick()

	// Decision logic based on the state of the resource
	if p.isIdle() {
		// Respond OK immediately
		p.mutex.Unlock()
		fmt.Printf("Process %d received request from process %d at time %d and is replying OK\n", p.id, requesterID, requestTime)
		p.sendOK(requesterID)
	} else if p.isAccessingResource() {
		// Queue the request
		fmt.Printf("Process %d received request from process %d at time %d and is queuing the request\n", p.id, requesterID, requestTime)
		p.requestQueue = append(p.requestQueue, requesterID)
		p.mutex.Unlock()
	} else {
		// Compare timestamps and decide
		p.mutex.Unlock()
		if requestTime < p.clock.GetClock() || (requestTime == p.clock.GetClock() && requesterID < p.id) {
			fmt.Printf("Process %d received request from process %d at time %d and is replying OK\n", p.id, requesterID, requestTime)
			p.sendOK(requesterID)
		} else {
			fmt.Printf("Process %d received request from process %d at time %d and is queuing the request\n", p.id, requesterID, requestTime)
			p.mutex.Lock()
			p.requestQueue = append(p.requestQueue, requesterID)
			p.mutex.Unlock()
		}
	}
}



func main() {
	numProcesses := 3
	processes = make([]*Process, numProcesses)

	for i := 0; i < numProcesses; i++ {
		processes[i] = NewProcess(i)
	}

	var wg sync.WaitGroup

	for i := 0; i < numProcesses; i++ {
		wg.Add(1)
		go func(proc *Process) {
			defer wg.Done()
			proc.RequestCriticalSection(processes)
		}(processes[i])
	}

	wg.Wait()
}
