package storage

import (
	"errors"

	"trabalho2.mc714.2024s1/model"
)

var (
	// ErrAccountExists is returned when an account already exists
	ErrAccountExists = errors.New("account already exists")

	// ErrAccountNotFound is returned when an account doesn't exist
	ErrAccountNotFound = errors.New("account doesn't exist")
)

type AccountStorage interface {
	CreateAccount(accountID int, name string) error
	DeleteAccount(accountID int) error
	GetAccount(accountID int) (*model.Account, error)
	AddToBalance(accountID int, amount float64) error
}

type storage struct {
	accounts map[int]*model.Account
}

func NewDatastore() AccountStorage {
	return &storage{
		accounts: make(map[int]*model.Account),
	}
}

func (s *storage) CreateAccount(accountID int, name string) error {
	if _, ok := s.accounts[accountID]; ok {
		return ErrAccountExists
	}

	s.accounts[accountID] = &model.Account{
		ID:      accountID,
		Name:    name,
		Balance: 0.0,
	}
	return nil
}

func (s *storage) DeleteAccount(accountID int) error {
	if _, ok := s.accounts[accountID]; !ok {
		return ErrAccountNotFound
	}
	delete(s.accounts, accountID)
	return nil
}

func (s *storage) GetAccount(accountID int) (*model.Account, error) {
	if _, ok := s.accounts[accountID]; !ok {
		return nil, ErrAccountNotFound
	}
	accCopy := &model.Account{
		ID:      s.accounts[accountID].ID,
		Name:    s.accounts[accountID].Name,
		Balance: s.accounts[accountID].Balance,
	}
	return accCopy, nil
}

func (s *storage) AddToBalance(accountID int, amount float64) error {
	if _, ok := s.accounts[accountID]; !ok {
		return ErrAccountNotFound
	}
	s.accounts[accountID].Balance += amount
	return nil
}
