import delta_debugging
from delta_debugging.DD_mod import DDMods


class TestDD(DDMods):
    def __init__(self):
        DDMods.__init__(self)
        self.debug_dd = 0
        self.verbose = 0

    def _test(self, deltas):
        # Build input file
        found = []
        for (index, byte) in deltas:
            if byte == "<" or byte == ";" or byte == "1" or byte == "2":
                found.append(byte)
        ret = self.PASS
        if found.count("<") == 0 and found.count(";") == 0 and found.count("1") == 1 and found.count("2") == 3:
            ret = self.FAIL
        print('Testing case {:11}: {}'.format(
            '"' + "".join([x[1] for x in deltas]) + '"', str(ret)))
        return ret


def str_to_deltas(test_input):
    deltas = list(map(lambda x: (x, test_input[x]), range(len(test_input))))
    return deltas


def deltas_to_str(deltas):
    return "".join([x[1] for x in deltas])


mydd = TestDD()
string1 = "1222>"
string2 = "<55513>;"
mods = mydd.get_mods(string1, string2)
c1 = str_to_deltas(string1)
c2 = str_to_deltas(string2)
c = mods

print("Expanding failure input ", mydd.pretty(c1), " to ", mydd.pretty(c2))

(c, c1, c2) = mydd.dddiff_mods(c1, c2, mods[:6])
print("The minimal failure to ", mydd.pretty(c2), " is ", mydd.pretty(c1))
print("The difference is ", c)
