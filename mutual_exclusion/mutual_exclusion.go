package main

import (
	"fmt"
	"sync"
	"time"
)

type LamportClock struct {
	clock int
	mutex sync.Mutex
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
	lc.mutex.Lock()
	defer lc.mutex.Unlock()
	fmt.Printf("Clock: %d\n", lc.clock)
}

type CentralDatabase struct {
	data map[int]float64
	lock sync.Mutex
}

func NewCentralDatabase() *CentralDatabase {
	return &CentralDatabase{data: make(map[int]float64)}
}

func (db *CentralDatabase) ReadData(accountNumber int) *float64 {
	db.lock.Lock()
	defer db.lock.Unlock()
	if amount, ok := db.data[accountNumber]; ok {
		return &amount
	}
	return nil
}

func (db *CentralDatabase) UpdateData(accountNumber int, amount float64) {
	db.lock.Lock()
	defer db.lock.Unlock()
	if _, ok := db.data[accountNumber]; ok {
		db.data[accountNumber] += amount
	} else {
		db.data[accountNumber] = amount
	}
}

type Bank struct {
	id                int
	centralDatabase   *CentralDatabase
	lamportClock      *LamportClock
	requestQueue      []*Bank
	receivedOk        map[int]bool
	wantToEnter       bool
	inCriticalSection bool
	otherBanks        []*Bank
	myRequestTime     int
}

func NewBank(id int, centralDatabase *CentralDatabase, lamportClock *LamportClock) *Bank {
	return &Bank{
		id:              id,
		centralDatabase: centralDatabase,
		lamportClock:    lamportClock,
		receivedOk:      make(map[int]bool),
	}
}

func (b *Bank) Transfer(accountNumberFrom, accountNumberTo int, amount float64) {
	b.lamportClock.Tick()
	accountFromAmount := b.centralDatabase.ReadData(accountNumberFrom)
	if accountFromAmount == nil || *accountFromAmount < amount {
		fmt.Printf("Transfer failed: account %d has insufficient funds\n", accountNumberFrom)
		return
	}

	b.RequestAccess()
	b.WaitForPermissions()

	b.inCriticalSection = true
	b.centralDatabase.UpdateData(accountNumberFrom, -amount)
	b.centralDatabase.UpdateData(accountNumberTo, amount)
	b.inCriticalSection = false

	fmt.Printf("Transfer succeeded: %.2f from %d to %d\n", amount, accountNumberFrom, accountNumberTo)
}

func (b *Bank) SendOk(bankID int) {
	b.lamportClock.Tick()
	b.otherBanks[bankID].ReceiveOk(b.id)
}

func (b *Bank) SendOkToAll() {
	for _, bank := range b.requestQueue {
		bank.ReceiveOk(b.id)
	}
}

func (b *Bank) ReceiveOk(bankID int) {
	b.lamportClock.Tick()
	b.receivedOk[bankID] = true
}

func (b *Bank) RequestAccess() {
	b.wantToEnter = true
	b.myRequestTime = b.lamportClock.GetClock()
	for _, bank := range b.otherBanks {
		bank.ReceiveRequest(b.id, b.lamportClock.GetClock())
	}
}

func (b *Bank) WaitForPermissions() {
	for len(b.receivedOk) < len(b.otherBanks) {
		time.Sleep(100 * time.Millisecond)
	}
}

func (b *Bank) ReceiveRequest(bankID, requestTime int) {
	b.lamportClock.UpdateClock(requestTime)
	b.lamportClock.Tick()

	if !b.inCriticalSection && !b.wantToEnter {
		b.SendOk(bankID)
	} else if b.inCriticalSection {
		b.requestQueue = append(b.requestQueue, b.otherBanks[bankID])
	} else if b.wantToEnter {
		if b.myRequestTime < requestTime || (b.myRequestTime == requestTime && b.id < bankID) {
			b.SendOk(bankID)
		} else {
			b.requestQueue = append(b.requestQueue, b.otherBanks[bankID])
		}
	}
}