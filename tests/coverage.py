class FifoCoverage:
    def __init__(self):
        self.coverage = {
            "write_when_empty": 0,
            "write_when_full": 0,
            "read_when_empty": 0,
            "read_when_full": 0,
            "simultaneous_read_write": 0,
            "full_flag_asserted": 0,
            "empty_flag_asserted": 0
        }
        self.total_bins = len(self.coverage)

    def sample(self, dut):
        try:
            wr = int(dut.WR_EN.value)
            rd = int(dut.RD_EN.value)
            full = int(dut.FULL.value)
            empty = int(dut.EMPTY.value)
        except ValueError:
            return  # Skip if signals are 'z' or 'x'

        if wr and empty:
            self.coverage["write_when_empty"] += 1
        if wr and full:
            self.coverage["write_when_full"] += 1
        if rd and empty:
            self.coverage["read_when_empty"] += 1
        if rd and full:
            self.coverage["read_when_full"] += 1
        if wr and rd:
            self.coverage["simultaneous_read_write"] += 1
        if full:
            self.coverage["full_flag_asserted"] += 1
        if empty:
            self.coverage["empty_flag_asserted"] += 1

    def report(self):
        print("\n========= FUNCTIONAL COVERAGE REPORT =========")
        total_hit = 0
        for key, count in self.coverage.items():
            status = "yes" if count > 0 else "no"
            total_hit += 1 if count > 0 else 0
            print(f"{key:<35}: {count:>3} hits {status}")
        percent = (total_hit / self.total_bins) * 100
        print("-----------------------------------------------")
        print(f"Total Coverage: {total_hit}/{self.total_bins} bins hit ({percent:.2f}%)")
        print("===============================================\n")
