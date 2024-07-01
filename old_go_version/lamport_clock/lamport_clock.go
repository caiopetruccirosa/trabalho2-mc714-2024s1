package lamport_clock

import ("fmt"; "sync")

type LamportClock struct {
	clock int
	mutex sync.Mutex
}

func NewLamportClock() *LamportClock {
	return &LamportClock{
		clock: 0,
	}
}

func (lc *LamportClock) Tick() {
	lc.mutex.Lock()
	defer lc.mutex.Unlock()

	lc.clock++
}

func (lc *LamportClock) UpdateClock(receivedClock int) {
	lc.mutex.Lock()
	defer lc.mutex.Unlock()

	if receivedClock > lc.clock {
		lc.clock = receivedClock + 1
	} else {
		lc.clock++
	}
}

func (lc *LamportClock) GetClock() int {
	lc.mutex.Lock()
	defer lc.mutex.Unlock()

	return lc.clock
}

func (lc *LamportClock) PrintClock() {
	fmt.Printf("Clock: %d\n", lc.clock)
}