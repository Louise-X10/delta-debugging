import delta_debugging
from delta_debugging.DD_mod import DDMods
import json


class TestDD(DDMods):
    def __init__(self):
        DDMods.__init__(self)
        self.debug_dd = 0
        self.verbose = 0

    def _test(self, deltas):
        print('Testing case {:11}. '.format(
            '"' + "".join([x[1] for x in deltas])))
        if deltas == []:
            print('Test passed: empty string')
            return self.PASS
        try:
            # Attempt to load the JSON
            parsed_json = json.loads(deltas_to_str(deltas))

            for key in parsed_json:
                # Check if value is a list
                if isinstance(parsed_json[key], list):
                    print(f"Test failed: {key} is a list.")
                    return self.FAIL
            return self.PASS

        except json.JSONDecodeError as e:
            # If there's a decoding error, print the error message
            print(f"Test unresolved: {e}")
            return self.UNRESOLVED


def str_to_deltas(test_input):
    deltas = list(map(lambda x: (x, test_input[x]), range(len(test_input))))
    return deltas


def deltas_to_str(deltas):
    return "".join([x[1] for x in deltas])


mydd = TestDD()
string1 = '{"baz": 7, "baaa": [1, 2]}'
print("Computing min input of ", string1)
test_input = string1
deltas = list(map(lambda x: (x, test_input[x]), range(len(test_input))))
c = mydd.ddmin(deltas)              # Invoke DDMIN
minimal = "".join([x[1] for x in c])

print("Min input of ", string1, " is ", minimal)

string1 = minimal
string2 = '{ "foo": "bar" }'
mods = mydd.get_mods(string1, string2)
c1 = str_to_deltas(string1)
c2 = str_to_deltas(string2)
c = mods

print("Expanding failure input ", mydd.pretty(c1), " to ", mydd.pretty(c2))

(c, c1, c2) = mydd.dddiff_mods(c1, c2, mods[:6])
print("The minimal failure to ", mydd.pretty(c2), " is ", mydd.pretty(c1))
print("The difference is ", c)
