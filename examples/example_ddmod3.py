import sys
sys.path.append('../')

import subprocess
from delta_debugging.DD_mod import DDMods


class TestDD(DDMods):
    def __init__(self, fuzzer_path):
        DDMods.__init__(self)
        self.debug_dd = 0
        self.verbose = 0
        self.fuzzer_path = fuzzer_path

    def _test(self, deltas):
        # Reconstruct the binary input
        binary_data = deltas_to_bytes(deltas)
        print("Testing input of length {}...".format(len(binary_data)))

        if not binary_data:
            return self.PASS

        # Run the binary with the input
        result = self.test_seed(binary_data)
        return self.PASS if result else self.FAIL

    def test_seed(self, binary_input):
        """Run fuzzer with binary_input piped to stdin and return True if it doesn't crash."""
        try:
            result = subprocess.run(
                [self.fuzzer_path],
                input=binary_input,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )
            return result.returncode == 0
        except Exception as e:
            print("Error running fuzzer: {}".format(e))
            return False


def bytes_to_deltas(b):
    print("Converting bytes to deltas...", b)
    return list(map(lambda i: (i, bytes(b[i])), range(len(b))))


def deltas_to_bytes(deltas):
    print("Converting deltas to bytes...", deltas)
    return b"".join([x[1] for x in deltas])


# Example usage
if __name__ == "__main__":
    
    if len(sys.argv) != 3:
        print("Need two arguments: crashing input and valid input")
        sys.exit(1)
    
    crashing_input = sys.argv[1]
    valid_input = sys.argv[2]
    fuzzer = "server"
    mydd = TestDD(fuzzer_path=fuzzer)

    # Load binary files
    with open(crashing_input, "rb") as f:
        crashing = f.read()

    with open(valid_input, "rb") as f:
        passing = f.read()

    # Delta debug between the two
    (c, c1, c2) = mydd.ddiff_max(crashing, passing)
    print("The minimally different failure to  ",
          mydd.pretty(c2), " is ", mydd.pretty(c1))
