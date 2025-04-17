
import sys
sys.path.append('../')

from delta_debugging.DD_mod import DDMods

class TestDD(DDMods):
    def __init__(self):
        DDMods.__init__(self)
        self.debug_dd = 0
        self.verbose = 0
        self.binary = False

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


test_input = "1222>"
string2 = "<55513>;"
mydd = TestDD()
(c, c1, c2) = mydd.ddiff_max(test_input, string2)
