import threading


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