import sys
sys.path.append('../')

import json
from delta_debugging.DD_mod import DDMods

class TestDD(DDMods):
    def __init__(self):
        DDMods.__init__(self)
        self.debug_dd = 0
        self.verbose = 0

    def _test(self, deltas):
        print_text = 'Testing case {:11}: '.format(
            '"' + "".join([x[1] for x in deltas]))
        print()
        if deltas == []:
            ret = self.PASS
            print(print_text + '"', str(ret))
            return ret
        try:
            # Attempt to load the JSON
            parsed_json = json.loads(deltas_to_str(deltas))
            ret = self.PASS
            for key in parsed_json:
                # Check if value is a list
                if isinstance(parsed_json[key], list):
                    # print(f"Test failed: {key} is a list.")
                    ret = self.FAIL
                    break

        except json.JSONDecodeError as e:
            # If there's a decoding error, print the error message
            # print(f"Test unresolved: {e}")
            ret = self.UNRESOLVED

        print(print_text + '"', str(ret))
        return ret


def str_to_deltas(test_input):
    deltas = list(map(lambda x: (x, test_input[x]), range(len(test_input))))
    return deltas


def deltas_to_str(deltas):
    return "".join([x[1] for x in deltas])


mydd = TestDD()
test_input = '{"baz": 7, "baaa": [1, 2]}'
string2 = '{ "foo": "bar" }'
(c, c1, c2) = mydd.ddiff_max(test_input, string2)

print("The minimally different failure to  ",
      mydd.pretty(c2), " is ", mydd.pretty(c1))
