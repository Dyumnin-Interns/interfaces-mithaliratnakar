# scoreboard.py

class FifoScoreboard:
    def __init__(self):
        self.expected = []

    def add_expected(self, data):
        self.expected.append(data)

    def compare(self, actual):
        assert self.expected, "No expected data to compare"
        expected = self.expected.pop(0)
        assert actual == expected, f"Expected {expected}, got {actual}"

