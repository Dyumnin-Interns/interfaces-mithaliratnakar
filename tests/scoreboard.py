class Scoreboard:
    def __init__(self):
        self.expected_outputs = []
        self.read_count = 0

    def expect(self, value):
        """Queue expected output from the DUT."""
        self.expected_outputs.append(value)

    def compare(self, observed):
        """Compare DUT output with expected value."""
        if not self.expected_outputs:
            raise AssertionError(f"Unexpected output from DUT: {observed} (nothing expected)")

        expected = self.expected_outputs.pop(0)
        self.read_count += 1

        assert expected == observed, f"Mismatch: Expected {expected}, got {observed}"

    def was_read_expected(self):
        """Check if we were expecting a read."""
        return len(self.expected_outputs) > 0


