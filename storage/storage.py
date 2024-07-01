class Account:
    def __init__(self, account_id, name, balance=0.0):
        self.id = account_id
        self.name = name
        self.balance = balance

class AccountStorage:
    def create_account(self, account_id, name):
        raise NotImplementedError

    def delete_account(self, account_id):
        raise NotImplementedError

    def get_account(self, account_id):
        raise NotImplementedError

    def add_to_balance(self, account_id, amount):
        raise NotImplementedError

class Storage(AccountStorage):
    def __init__(self):
        self.accounts = {}

    def create_account(self, account_id, name):
        if account_id in self.accounts:
            raise ValueError("account already exists")
        self.accounts[account_id] = Account(account_id, name)
        return None

    def delete_account(self, account_id):
        if account_id not in self.accounts:
            raise ValueError("account doesn't exist")
        del self.accounts[account_id]
        return None

    def get_account(self, account_id):
        if account_id not in self.accounts:
            raise ValueError("account doesn't exist")
        account = self.accounts[account_id]
        return Account(account.id, account.name, account.balance)

    def add_to_balance(self, account_id, amount):
        if account_id not in self.accounts:
            raise ValueError("account doesn't exist")
        self.accounts[account_id].balance += amount
        return None