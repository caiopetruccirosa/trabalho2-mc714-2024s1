
class LamportClock:
    def __init__(self):
        self.clock = 0

    def tick(self):
        self.clock += 1

    def update_clock(self, received_clock):
        if received_clock > self.clock:
            self.clock = received_clock + 1
        else:
            self.clock += 1

    def get_clock(self):
        return self.clock

    def print_clock(self):
        print(f"Clock: {self.clock}")