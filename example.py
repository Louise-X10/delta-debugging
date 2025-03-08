from delta_debugging.DD import DD
import difflib

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

def get_mods(string1, string2):
    # Get list of modifications to change string1 into string2
    mods = []
    s = difflib.SequenceMatcher()
    s.set_seqs(string1, string2)
    matching_blocks = s.get_matching_blocks()

    # Traverse the matching blocks and identify insertions
    for i, block in enumerate(matching_blocks):
        # Check fore insertion before first match
        if i == 0 and block.b > 0:
            insert_str = string2[:block.b]
            mods.append((-1, insert_str, mydd.ADD))
        # Check for insertions between matches
        if i < len(matching_blocks) - 1:
            next_block = matching_blocks[i + 1]
            insert_str = string2[(block.b+1):next_block.b]
            mods.append((block.a, insert_str, mydd.ADD))

    diff = list(difflib.ndiff(string1, string2))
    index = 0
    remove = []
    remove_idx = -1
    for d in diff:
        if d.startswith("- "):  # Removed character
            if remove == []:
                remove_idx = index
            remove.append(d[2])
        elif remove != []:
            mods.append((remove_idx, "".join(remove), mydd.REMOVE))
            remove = []
        if d.startswith(" "): # Not removed character
            index += 1

    return mods

def split_mods(mods):
    prepend = []
    inserted = []
    removed = []
    for pos, char, op in mods:
        if pos == -1:
            prepend.append((pos, char))  # Collect elements with index -1
        elif op == mydd.ADD:
            inserted.append((pos, char))
        elif op == mydd.REMOVE:
            removed.append((pos, char))
    return prepend, inserted, removed

def apply_remove(deltas, removed):
    delta_dict = {idx: char for idx, char in deltas}
    for start_idx, chars in removed:
        for i in range(len(chars)):  # Remove each character from the given start index
            if start_idx + i in delta_dict:
                del delta_dict[start_idx + i]
    deltas = sorted(delta_dict.items())
    return deltas

def apply_insert(deltas, inserted):
    for insert_idx, chars in inserted:
        # Find the index in new_deltas where to insert
        for i, (idx, _) in enumerate(deltas):
            if idx == insert_idx:
                for char in chars:
                    deltas.insert(i + 1, (None, char))  # Use None as a placeholder index
                break
    return deltas

def apply_prepend(deltas, prepend):
    if prepend:
        before_idx, chars = prepend[0]  # Always inserting before the first element
        deltas = [(i, char) for i, char in enumerate(chars)] + deltas
    return deltas

def apply_mods(deltas, mods):
    prepend, inserted, removed = split_mods(mods)
    deltas = apply_remove(deltas, removed)
    deltas = apply_insert(deltas, inserted)
    deltas = apply_prepend(deltas, prepend)
    deltas = [(i, char) for i, (_, char) in enumerate(deltas)]
    return deltas

test_input = "12345678"
print('Minimizing input: "{}"'.format(test_input))
# Convert string into the delta format
deltas = list(map(lambda x: (x, test_input[x]), range(len(test_input))))