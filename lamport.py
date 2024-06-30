import threading
import time
from typing import Dict, List

class LamportClock:
    def __init__(self):
        self.clock = 0
        self.mutex = threading.Lock()

    def tick(self):
        with self.mutex:
            self.clock += 1

    def update_clock(self, received_clock):
        with self.mutex:
            if received_clock > self.clock:
                self.clock = received_clock + 1
            else:
                self.clock += 1

    def get_clock(self):
        with self.mutex:
            return self.clock

    def print_clock(self):
        with self.mutex:
            print(f"Clock: {self.clock}")


class CentralDatabase:
    def __init__(self):
        self.lock = threading.Lock()
        self.data = {}  # account_number: amount - os saldos das contas

    def read_data(self, account_number: int):
        with self.lock:
            if account_number in self.data:
                return self.data[account_number]
            else:
                return None

    def update_data(self, account_number: int, amount: float):
        with self.lock:
            if account_number in self.data:
                self.data[account_number] += amount
            else:
                self.data[account_number] = amount


class Bank:
    def __init__(self, process_id, central_database: CentralDatabase, lamport_clock: LamportClock):
        self.central_database = central_database
        self.lamport_clock = lamport_clock
        self.id = process_id
        self.request_queue: List[Bank] = []
        self.received_ok: Dict[int, bool] = {}
        self.want_to_enter = False
        self.in_critical_section = False
        self.other_banks: List[Bank] = []
        self.my_request_time = 0

    def transfer(
        self, 
        account_number_from: int, 
        account_number_to: int, 
        amount: int
    ):
        self.lamport_clock.tick()
        account_from_amount = self.central_database.read_data(account_number_from)
        if account_from_amount is None or account_from_amount < amount:
            print(f"Transfer failed: account {account_number_from} has insufficient funds")
            return
        
        self.request_acess()
        self.wait_for_permissions()
        # critical section
        self.in_critical_section = True
        self.central_database.update_data(account_number_from, -amount)
        self.central_database.update_data(account_number_to, amount)
        self.in_critical_section = False
        # end of critical section
        print(f"Transfer succeeded: {amount} from {account_number_from} to {account_number_to}")

    def send_ok(self, bank_id: int):
        self.lamport_clock.tick()
        self.other_banks[bank_id].receive_ok(self.id)

    def send_ok_to_all(self):
        for bank in self.request_queue:
            bank.receive_ok(self.id)

    def receive_ok(self, bank_id: int):
        self.lamport_clock.tick()
        self.received_ok[bank_id] = True

    def request_acess(self):
        self.want_to_enter = True
        self.my_request_time = self.lamport_clock.get_clock()
        for bank in self.other_banks:
            bank.receive_request(self.id, self.lamport_clock.get_clock())

    def wait_for_permissions(self):
        # Wait until all processes have given permission
        while len(self.received_ok) < len(self.other_banks):
            time.sleep(0.1)
    
    def receive_request(self, bank_id: int, request_time: int):
        self.lamport_clock.update_clock(request_time)
        self.lamport_clock.tick()

        if not self.in_critical_section and not self.want_to_enter:
            self.send_ok(bank_id)
        elif self.in_critical_section:
            self.request_queue.append(self.other_banks[bank_id])
        elif self.want_to_enter:
            if self.my_request_time < request_time or (self.my_request_time == request_time and self.id < bank_id):
                self.send_ok(bank_id)
            else:
                self.request_queue.append(self.other_banks[bank_id])
