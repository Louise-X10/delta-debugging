import difflib

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
            for char in insert_str:
                mods.append((-1, char, mydd.ADD))
        # Check for insertions between matches
        if i < len(matching_blocks) - 1:
            next_block = matching_blocks[i + 1]
            insert_str = string2[(block.b+1):next_block.b]
            for char in insert_str:
                mods.append((block.a, char, mydd.ADD))

    diff = list(difflib.ndiff(string1, string2))
    remove_idx = 0
    for d in diff:
        if d.startswith("- "):  # Removed character
            mods.append((remove_idx, d[2], mydd.REMOVE))
            remove_idx += 1
        elif d.startswith(" "): # Not removed character
            remove_idx += 1

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
                # Check the deleted char is the one speficied by removed
                assert delta_dict[start_idx + i] == chars[i]
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
    prepend_chars = [(-1, entry[1]) for entry in prepend]
    deltas = prepend_chars + deltas
    return deltas

def apply_mods(deltas, mods):
    prepend, inserted, removed = split_mods(mods)
    deltas = apply_remove(deltas, removed)
    deltas = apply_insert(deltas, inserted)
    deltas = apply_prepend(deltas, prepend)
    deltas = [(i, char) for i, (_, char) in enumerate(deltas)]
    return deltas
