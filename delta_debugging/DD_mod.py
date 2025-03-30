import string
from delta_debugging.DD import DD
import difflib
  

# Main Delta Debugging algorithm.
class DDMods(DD):
    # Delta debugging base class.  To use this class for a particular
    # setting, create a subclass with an overloaded `test()' method.
    #
    # Main entry points are:
    # - `ddmin()' which computes a minimal failure-inducing configuration, and
    # - `dd()' which computes a minimal failure-inducing difference.
   

    def __init__(self):
        DD.__init__(self)
        self.debug_dd = 0
        self.verbose = 0

    # Get list of modifications to change string1 into string2
    # def get_mods(self, string1, string2):   
    #     mods = []
    #     s = difflib.SequenceMatcher()
    #     s.set_seqs(string1, string2)
    #     matching_blocks = s.get_matching_blocks()

    #     # Traverse the matching blocks and identify insertions
    #     for i, block in enumerate(matching_blocks):
    #         # Check fore insertion before first match
    #         if i == 0 and block.b > 0:
    #             insert_str = string2[:block.b]
    #             mods.append((-1, insert_str, self.ADD))
    #         # Check for insertions between matches
    #         if i < len(matching_blocks) - 1:
    #             next_block = matching_blocks[i + 1]
    #             insert_str = string2[(block.b+1):next_block.b]
    #             mods.append((block.a, insert_str, self.ADD))

    #     diff = list(difflib.ndiff(string1, string2))
    #     index = 0
    #     remove = []
    #     remove_idx = -1
    #     for d in diff:
    #         if d.startswith("- "):  # Removed character
    #             if remove == []:
    #                 remove_idx = index
    #             remove.append(d[2])
    #         elif remove != []:
    #             mods.append((remove_idx, "".join(remove), self.REMOVE))
    #             remove = []
    #         if d.startswith(" "): # Not removed character
    #             index += 1

    #     return mods

    def coerce(self, c):
        """Return the configuration C as a compact string"""
        # Default: use printable representation
        return "".join([x[1] for x in c])

    def pretty(self, c):
        """Like coerce(), but sort beforehand"""
        # sorted_c = c[:]
        # c.sort()
        return self.coerce(c)

    def get_mods(self, string1, string2):
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
                    mods.append((-1, char, self.ADD))
            # Check for insertions between matches
            if i < len(matching_blocks) - 1:
                next_block = matching_blocks[i + 1]
                insert_str = string2[(block.b+1):next_block.b]
                for char in insert_str:
                    mods.append((block.a, char, self.ADD))

        diff = list(difflib.ndiff(string1, string2))
        remove_idx = 0
        for d in diff:
            if d.startswith("- "):  # Removed character
                mods.append((remove_idx, d[2], self.REMOVE))
                remove_idx += 1
            elif d.startswith(" "): # Not removed character
                remove_idx += 1

        return mods

    # Helpers
    def __modsapply(self, c1, mods):
        """Apply modification of mods onto c1."""
        c1 = self.__apply_mods(c1, mods)
        return c1
    
    def __modsminus(self, mods, submods):
        """Return a list of all elements of mods that are not in submods."""
        s2 = {}
        for delta in submods:
            s2[delta] = 1

        c = []
        for delta in mods:
            if delta not in s2:
                c.append(delta)
        return c

    def __split_mods(self, mods):
        prepend = []
        inserted = []
        removed = []
        for pos, char, op in mods:
            if pos == -1:
                prepend.append((pos, char))  # Collect elements with index -1
            elif op == self.ADD:
                inserted.append((pos, char))
            elif op == self.REMOVE:
                removed.append((pos, char))
        return prepend, inserted, removed

    def __apply_remove(self, deltas, removed):
        delta_dict = {idx: char for idx, char in deltas}
        for start_idx, chars in removed:
            for i in range(len(chars)):  # Remove each character from the given start index
                if start_idx + i in delta_dict:
                    # Check the deleted char is the one speficied by removed
                    assert delta_dict[start_idx + i] == chars[i]
                    del delta_dict[start_idx + i]
        deltas = sorted(delta_dict.items())
        return deltas

    def __apply_insert(self, deltas, inserted):
        for insert_idx, chars in inserted:
            # Find the index in new_deltas where to insert
            for i, (idx, _) in enumerate(deltas):
                if idx == insert_idx:
                    for char in chars:
                        deltas.insert(i + 1, (None, char))  # Use None as a placeholder index
                    break
        return deltas

    def __apply_prepend(self, deltas, prepend):
        prepend_chars = [(-1, entry[1]) for entry in prepend]
        deltas = prepend_chars + deltas
        return deltas

    def __apply_mods(self, deltas, mods):
        prepend, inserted, removed = self.__split_mods(mods)
        deltas = self.__apply_remove(deltas, removed)
        deltas = self.__apply_insert(deltas, inserted)
        deltas = self.__apply_prepend(deltas, prepend)
        deltas = [(i, char) for i, (_, char) in enumerate(deltas)]
        return deltas


    # Test mods (fixes not imlemented yet)
    def test_mods_and_resolve(self, csub, r, c, direction):
        """Repeat testing 'modify CSUB with R' while unresolved."""

        initial_csub = csub[:]
        # c2 = self.__listunion(r, c)

        csubr = self.__modsapply(csub, r)
        t = self.test(csubr)

        # necessary to use more resolving mechanisms which can reverse each
        # other, can (but needn't) be used in subclasses
        # self._resolve_type = 0 

        # while t == self.UNRESOLVED:
        #     self.__resolving = 1
        #     csubr = self.resolve(csubr, c, direction)

        #     if csubr is None:
        #         # Nothing left to resolve
        #         break
            
        #     if len(csubr) >= len(c2):
        #         # Added everything: csub == c2. ("Upper" Baseline)
        #         # This has already been tested.
        #         csubr = None
        #         break
                
        #     if len(csubr) <= len(r):
        #         # Removed everything: csub == r. (Baseline)
        #         # This has already been tested.
        #         csubr = None
        #         break
            
        #     t = self.test(csubr)

        # self.__resolving = 0
        if csubr is None:
            return self.UNRESOLVED, initial_csub

        # assert t == self.PASS or t == self.FAIL
        # csub = self.__listminus(csubr, r)
        return t, csubr

    # Delta debugging with list of modifications from c1 (failing) to c2 (passing)
    def dddiff_mods(self, c1, c2, mods):
        n = 2

        if self.debug_dd:
            print("dddiff(" + self.pretty(c) + ", " + n + ")...")

        outcome = self._dddiff_mods(c1, c2, mods, n)

        if self.debug_dd:
            print("dddiff(" + self.pretty(c) + ", " + n + ") = " +
                   outcome)

        return outcome
    
    # c1 = failing
    # c2 = passing
    # c = list of mods from c1 to c2
    def _dddiff_mods(self, c1, c2, mods, n):
        run = 1

        # We replace the tail recursion from the paper by a loop
        while 1:
            if self.debug_dd:
                print("dd: c1 =", self.pretty(c1))
                print("dd: c2 =", self.pretty(c2))

            if self.assume_axioms_hold:
                t1 = self.FAIL
                t2 = self.PASS
            else:
                t1 = self.test(c1)
                t2 = self.test(c2)
            
            assert t1 == self.FAIL
            assert t2 == self.PASS
            # assert self.__listsubseteq(c1, c2)

            # c = self.__listminus(c2, c1)
            # c = self.__listunion(c2, c1)
            ##* List of deltas is list of mods
            c = mods

            if self.debug_dd:
                print("dd: c2 - c1 =", self.pretty(c))

            if n > len(c):
                # No further minimizing
                if self.verbose:
                    print("dd: done")
                return (c, c1, c2)

            self.report_progress(c, "dd")

            cs = self.split(c, n)

            if self.verbose:
                print()
                print("dd (run #" + run + "): trying",)
                for i in range(n):
                    if i > 0:
                        print("+",)
                    print(len(cs[i]),)
                print()

            progress = 0

            next_c1 = c1[:]
            next_mods = c[:]
            next_n = n

            # Check subsets
            for j in range(n):
                i = j % n

                if self.debug_dd:
                    print("dd: trying", self.pretty(cs[i]))

                (t, csub) = self.test_mods_and_resolve(c1, cs[i], c2, self.REMOVE)
                # csub = self.__listunion(c1, csub)

                if t == self.FAIL:
                    # Found
                    progress    = 1
                    ##* Change lower bound to new failing test case
                    next_c1     = csub
                    next_mods   = self.__modsminus(c, cs[i])
                    next_n      = 2

                    if self.debug_dd:
                        print("dd: increase c1 to", len(next_c1), "deltas:",)
                        print(self.pretty(next_mods))
                    break
                elif t == self.PASS:
                    # Not found
                    progress    = 0

            if progress:
                # if self.animate is not None:
                #     self.animate.write_outcome(
                #         self.__listminus(next_c1, c1_orig), self.PASS)
                #     self.animate.write_outcome(
                #         self.__listminus(c2_orig, next_c2), self.FAIL)
                #     self.animate.write_outcome(
                #         self.__listminus(next_c2, next_c1), self.DIFFERENCE)
                #     self.animate.next_frame()

                self.report_progress(next_mods, "dd")
            else:
                if n >= len(c):
                    # No further minimizing
                    if self.verbose:
                        print("dd: done")
                    return (c, c1, c2)

                next_n = min(len(c), n * 2)
                if self.verbose:
                    print("dd: increase granularity to", next_n)

            c1  = next_c1
            n   = next_n
            c   = next_mods
            run = run + 1

    def dd(self, c):
        return self.dddiff(c)           # Backwards compatibility



if __name__ == '__main__':
    
    # Define our own DD class, with its own test method
    class MyDD(DDMods):        
        def _test_a(self, c):
            "Test the configuration C.  Return PASS, FAIL, or UNRESOLVED."

            # Just a sample
            # if 2 in c and not 3 in c:
            #            return self.UNRESOLVED
            # if 3 in c and not 7 in c:
            #   return self.UNRESOLVED
            if 7 in c and not 2 in c:
                return self.UNRESOLVED
            if 5 in c and 8 in c:
                return self.FAIL
            return self.PASS

        def _test_b(self, c):
            if c == []:
                return self.PASS
            if 1 in c and 2 in c and 3 in c and 4 in c and \
                5 in c and 6 in c and 7 in c and 8 in c:
                return self.FAIL
            return self.UNRESOLVED

        def _test_c(self, c):
            result = 1000

            if 1 in c and 2 in c and 3 in c and 4 in c and \
                6 in c and 8 in c:
                if 5 in c and 7 in c:
                    result = self.UNRESOLVED
                else:
                    result = self.FAIL
            if 1 in c or 2 in c or 3 in c or 4 in c or \
                6 in c or 8 in c:
                if result == 1000:
                    result = self.UNRESOLVED
            if result == 1000:
                result = self.PASS
            print("testing: ", self.coerce(c), "result = ", result)
            return result

        def _test_d(self, c):
            result = 1000

            if len(c) == 255:
                result = self.FAIL

            if result == 1000 and 17 in c and 31 in c and 63 in c and 129 in c:
                result = self.UNRESOLVED
            if result == 1000 and 1 in c and 7 in c and 11 in c and 22 in c and 41 in c and \
               47 in c and 53 in c and 61 in c and 67 in c and 71 in c and 83 in c and 91 in c and \
               97 in c and 101 in c and 103 in c and 111 in c and 113 in c and 121 in c and \
               131 in c and 162 in c and 163 in c and 164 in c and 165 in c and 166 in c and \
               167 in c and 192 in c and 197 in c and 201 in c and 203 in c and 211 in c and \
               222 in c and 223 in c and 224 in c and 225 in c and 251 in c and 252 in c and \
               253 in c:
                result = self.FAIL
            if result == 1000:
                result = self.PASS
            # print("testing: ", self.coerce(c), "result = ", result)
            return result

        def _test_e(self, c):
            if len(c) == 65535:
                return self.FAIL

            for i in c:
                if (i % 2) == 0:
                    return self.FAIL

            return self.PASS

        def _test_f(self, c):
            king = 0
            romeo = 0
            for s in c:
                if string.find(s, "King ") > -1:
                    king = 1
                if string.find(s, "Romeo") > -1:
                    romeo = 1
            if king == 1 and romeo == 1:
                return self.FAIL
            return self.PASS

        def __init__(self):
            self._test = self._test_f
            DD.__init__(self)
                        
    print("WYNOT - a tool for delta debugging.")
    mydd = MyDD()
    # mydd.debug_test     = 1        # Enable debugging output
    # mydd.debug_dd       = 1        # Enable debugging output
    # mydd.debug_split    = 1        # Enable debugging output
    # mydd.debug_resolve  = 1        # Enable debugging output

    # mydd.cache_outcomes = 0
    # mydd.monotony = 0

    #print("Minimizing failure-inducing input...")
    #list = range(1, 9)
    #for i in range (1, 255):
    #    list.append(i)

    #c = mydd.ddmax(list)
    #print("The 1-minimal failure-inducing input is", c)
    #print("Removing any element will make the failure go away.")
    #print()
    
    list = ["A King there was in days of old,",\
            "ere Men yet walked upon the mould.",\
            "There Juliet and her Romeo,",\
            "beneath the stars sat."]
    print("Computing the failure-inducing difference...")
    (c, c1, c2) = mydd.dd(list)        # Invoke DD
    print("The 1-minimal failure-inducing difference is", c)
    print(c1, "passes,", c2, "fails")
    

# Local Variables:
# mode: python
# End:
