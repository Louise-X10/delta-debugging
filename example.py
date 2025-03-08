from delta_debugging.DD import DD
from mods import *

class TestDD(DD):
	def __init__(self):
		DD.__init__(self)
		self.debug_dd = 0
		self.verbose = 0
	def _test(self, deltas):
		# Build input file
		found = []
		for (index, byte) in deltas:
			if byte == "1" or byte == "3":
				found.append(byte)
		ret = self.PASS
		if found.count("1") == 1 and found.count("3") == 1:
			ret = self.FAIL
		print('Testing case {:11}: {}'.format('"' + "".join([x[1] for x in deltas]) + '"', str(ret)))
		return ret

def str_to_deltas(test_input):
    deltas = list(map(lambda x: (x, test_input[x]), range(len(test_input))))
    return deltas

test_input = "12345678"
print('Minimizing input: "{}"'.format(test_input))
# Convert string into the delta format
deltas = list(map(lambda x: (x, test_input[x]), range(len(test_input))))