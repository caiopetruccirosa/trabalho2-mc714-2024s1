package main

import (
	"fmt"
	"time"
)

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