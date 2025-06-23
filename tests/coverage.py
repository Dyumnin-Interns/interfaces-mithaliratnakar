from collections import defaultdict
class FunctionalCoverage:
    def __init__(self):
        self.or_combos = set()
        self.write_hits = set()
        self.read_hits = set()
        self.addr_reads = set()
        self.corner_hits = defaultdict(int)
    def track_or_input(self, a_val, b_val):
        self.or_combos.add((a_val, b_val))
    def track_write_address(self, addr):
        if addr in [0, 1, 2, 3, 4, 5]:
            self.write_hits.add(addr)
    def track_read_address(self, addr):
        if addr in [0, 1, 2, 3]:
            self.read_hits.add(addr)
    def track_corner(self, name):
        self.corner_hits[name] += 1
    def all_covered(self):
        return (
            self.or_combos == {(0, 0), (0, 1), (1, 0), (1, 1)} and
            {4, 5}.issubset(self.write_hits) and
            {0, 1, 2, 3}.issubset(self.read_hits)
        )
    def report(self):
        print("\n================ FUNCTIONAL COVERAGE REPORT ================")
        print("\nOR Input Combinations Hit:")
        for pair in sorted([(0, 0), (0, 1), (1, 0), (1, 1)]):
            status = "✔" if pair in self.or_combos else "✘"
            print(f"  OR{pair} -> {status}")
        print("\nWrite Addresses Hit:")
        for addr in sorted([4, 5]):
            status = "✔" if addr in self.write_hits else "✘"
            print(f"  Write to address {addr} -> {status}")
        print("\nRead Addresses Hit:")
        for addr in sorted([0, 1, 2, 3]):
            status = "✔" if addr in self.read_hits else "✘"
            print(f"  Read from address {addr} -> {status}")
        print("\nCorner Case Tests:")
        if not self.corner_hits:
                        print("  (No corner cases tracked)")
        else:
            for name, count in self.corner_hits.items():
                print(f"  {name}: {count} hit(s)")
        # Percentage-based overall coverage
        total_points = 4 + 2 + 4  # OR combos + write addresses + read addresses
        covered_points = (
            len(self.or_combos.intersection({(0, 0), (0, 1), (1, 0), (1, 1)})) +
            len({4, 5}.intersection(self.write_hits)) +
            len({0, 1, 2, 3}.intersection(self.read_hits))
        )
        percent = (covered_points / total_points) * 100

        print(f"\nOverall Coverage:  {percent:.0f}%")
        print("============================================================\n")
