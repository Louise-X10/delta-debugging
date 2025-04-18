#! /usr/bin/env python

# $Id: DD.py,v 1.10 2004/06/21 13:12:38 zeller Exp $

# Enhanced Delta Debugging class
# Copyright (c) 1999, 2000, 2001 Andreas Zeller.

# This module (written in Python) implements the base delta debugging
# algorithms and is at the core of all our experiments.  This should
# easily run on any platform and any Python version since 1.6.
#
# To plug this into your system, all you have to do is to create a
# subclass with a dedicated `test()' method.  Basically, you would
# invoke the DD test case minimization algorithm (= the `ddmin()'
# method) with a list of characters; the `test()' method would combine
# them to a document and run the test.  This should be easy to realize
# and give you some good starting results; the file includes a simple
# sample application.
#
# This file is in the public domain; feel free to copy, modify, use
# and distribute this software as you wish - with one exception.
# Passau University has filed a patent for the use of delta debugging
# on program states (A. Zeller: `Isolating cause-effect chains',
# Saarland University, 2001).  The fact that this file is publicly
# available does not imply that I or anyone else grants you any rights
# related to this patent.
#
# The use of Delta Debugging to isolate failure-inducing code changes
# (A. Zeller: `Yesterday, my program worked', ESEC/FSE 1999) or to
# simplify failure-inducing input (R. Hildebrandt, A. Zeller:
# `Simplifying failure-inducing input', ISSTA 2000) is, as far as I
# know, not covered by any patent, nor will it ever be.  If you use
# this software in any way, I'd appreciate if you include a citation
# such as `This software uses the delta debugging algorithm as
# described in (insert one of the papers above)'.
#
# All about Delta Debugging is found at the delta debugging web site,
#
#               http://www.st.cs.uni-sb.de/dd/
#
# Happy debugging,
#
# Andreas Zeller


import string

# Start with some helpers.


class OutcomeCache:
    # This class holds test outcomes for configurations.  This avoids
    # running the same test twice.

    # The outcome cache is implemented as a tree.  Each node points
    # to the outcome of the remaining list.
    #
    # Example: ([1, 2, 3], PASS), ([1, 2], FAIL), ([1, 4, 5], FAIL):
    #
    #      (2, FAIL)--(3, PASS)
    #     /
    # (1, None)
    #     \
    #      (4, None)--(5, FAIL)

    def __init__(self):
        self.tail = {}                  # Points to outcome of tail
        self.result = None              # Result so far

    def add(self, c, result):
        """Add (C, RESULT) to the cache.  C must be a list of scalars."""
        cs = c[:]
        # cs.sort()

        p = self
        for start in range(len(c)):
            if c[start] not in p.tail:
                p.tail[c[start]] = OutcomeCache()
            p = p.tail[c[start]]

        p.result = result

    def lookup(self, c):
        """Return RESULT if (C, RESULT) is in the cache; None, otherwise."""
        p = self
        for start in range(len(c)):
            if c[start] not in p.tail:
                return None
            p = p.tail[c[start]]

        return p.result

    def lookup_superset(self, c, start=0):
        """Return RESULT if there is some (C', RESULT) in the cache with
        C' being a superset of C or equal to C.  Otherwise, return None."""

        # FIXME: Make this non-recursive!
        if start >= len(c):
            if self.result:
                return self.result
            elif self.tail != {}:
                # Select some superset
                superset = self.tail[self.tail.keys()[0]]
                return superset.lookup_superset(c, start + 1)
            else:
                return None

        if c[start] in self.tail:
            return self.tail[c[start]].lookup_superset(c, start + 1)

        # Let K0 be the largest element in TAIL such that K0 <= C[START]
        k0 = None
        for k in self.tail.keys():
            if (k0 is None or k > k0) and k <= c[start]:
                k0 = k

        if k0 is not None:
            return self.tail[k0].lookup_superset(c, start)

        return None

    def lookup_subset(self, c):
        """Return RESULT if there is some (C', RESULT) in the cache with
        C' being a subset of C or equal to C.  Otherwise, return None."""
        p = self
        for start in range(len(c)):
            if c[start] in p.tail:
                p = p.tail[c[start]]

        return p.result


# Test the outcome cache
def oc_test():
    oc = OutcomeCache()

    assert oc.lookup([1, 2, 3]) is None
    oc.add([1, 2, 3], 4)
    assert oc.lookup([1, 2, 3]) == 4
    assert oc.lookup([1, 2, 3, 4]) is None

    assert oc.lookup([5, 6, 7]) is None
    oc.add([5, 6, 7], 8)
    assert oc.lookup([5, 6, 7]) == 8

    assert oc.lookup([]) is None
    oc.add([], 0)
    assert oc.lookup([]) == 0

    assert oc.lookup([1, 2]) is None
    oc.add([1, 2], 3)
    assert oc.lookup([1, 2]) == 3
    assert oc.lookup([1, 2, 3]) == 4

    assert oc.lookup_superset([1]) == 3 or oc.lookup_superset([1]) == 4
    assert oc.lookup_superset([1, 2]) == 3 or oc.lookup_superset([1, 2]) == 4
    assert oc.lookup_superset([5]) == 8
    assert oc.lookup_superset([5, 6]) == 8
    assert oc.lookup_superset([6, 7]) == 8
    assert oc.lookup_superset([7]) == 8
    assert oc.lookup_superset([]) is not None

    assert oc.lookup_superset([9]) is None
    assert oc.lookup_superset([7, 9]) is None
    assert oc.lookup_superset([-5, 1]) is None
    assert oc.lookup_superset([1, 2, 3, 9]) is None
    assert oc.lookup_superset([4, 5, 6, 7]) is None

    assert oc.lookup_subset([]) == 0
    assert oc.lookup_subset([1, 2, 3]) == 4
    assert oc.lookup_subset([1, 2, 3, 4]) == 4
    assert oc.lookup_subset([1, 3]) is None
    assert oc.lookup_subset([1, 2]) == 3

    assert oc.lookup_subset([-5, 1]) is None
    assert oc.lookup_subset([-5, 1, 2]) == 3
    assert oc.lookup_subset([-5]) == 0


# Main Delta Debugging algorithm.
class DD:
    # Delta debugging base class.  To use this class for a particular
    # setting, create a subclass with an overloaded `test()' method.
    #
    # Main entry points are:
    # - `ddmin()' which computes a minimal failure-inducing configuration, and
    # - `dd()' which computes a minimal failure-inducing difference.
    #
    # See also the usage sample at the end of this file.
    #
    # For further fine-tuning, you can implement an own `resolve()'
    # method (tries to add or remove configuration elements in case of
    # inconsistencies), or implement an own `split()' method, which
    # allows you to split configurations according to your own
    # criteria.
    #
    # The class includes other previous delta debugging alorithms,
    # which are obsolete now; they are only included for comparison
    # purposes.

    # Test outcomes.
    PASS = "PASS"
    FAIL = "FAIL"
    UNRESOLVED = "UNRESOLVED"

    # To indicate that a set is the difference between a passing
    # and a failing run
    DIFFERENCE = "DIFFERENCE"

    # Resolving directions.
    ADD = "ADD"        # Add deltas to resolve
    REMOVE = "REMOVE"        # Remove deltas to resolve

    # Debugging output (set to 1 to enable)
    debug_test = 0
    debug_dd = 0
    debug_split = 0
    debug_resolve = 0
    verbose = 1

    state_debugger = 0

    def __init__(self):
        self.__resolving = 0
        self.__last_reported_length = 0
        self.monotony = 0
        self.outcome_cache = OutcomeCache()
        self.cache_outcomes = 1
        self.minimize = 1
        self.maximize = 1
        self.assume_axioms_hold = 1

        # Animation output (set to Animate object to enable)
        self.animate = None

        self.n_tests = 0
        self.n_passes = 0
        self.n_fails = 0
        self.n_unres = 0

    # Helpers
    def __listminus(self, c1, c2):
        """Return a list of all elements of C1 that are not in C2."""
        s2 = {}
        for delta in c2:
            s2[delta] = 1

        c = []
        for delta in c1:
            if delta not in s2:
                c.append(delta)

        return c

    def __listintersect(self, c1, c2):
        """Return the common elements of C1 and C2."""
        s2 = {}
        for delta in c2:
            s2[delta] = 1

        c = []
        for delta in c1:
            if delta in s2:
                c.append(delta)

        return c

    def __listunion(self, c1, c2):
        """Return the union of C1 and C2."""
        s1 = {}
        for delta in c1:
            s1[delta] = 1

        c = c1[:]
        for delta in c2:
            if delta not in s1:
                c.append(delta)

        return c

    def __listsubseteq(self, c1, c2):
        """Return 1 if C1 is a subset or equal to C2."""
        s2 = {}
        for delta in c2:
            s2[delta] = 1

        for delta in c1:
            if delta not in s2:
                return 0

        return 1

    # Output
    def coerce(self, c):
        """Return the configuration C as a compact string"""
        # Default: use printable representation
        return c

    def pretty(self, c):
        """Like coerce(), but sort beforehand"""
        sorted_c = c[:]
        # sorted_c.sort()
        return self.coerce(sorted_c)

    # Testing
    def test(self, c):
        """Test the configuration C.  Return PASS, FAIL, or UNRESOLVED"""
        # c.sort()

        # If we had this test before, return its result
        if self.cache_outcomes:
            cached_result = self.outcome_cache.lookup(c)
            if cached_result is not None:
                return cached_result

        if self.monotony:
            # Check whether we had a passing superset of this test before
            cached_result = self.outcome_cache.lookup_superset(c)
            if cached_result == self.PASS:
                return self.PASS

            cached_result = self.outcome_cache.lookup_subset(c)
            if cached_result == self.FAIL:
                return self.FAIL

        if self.debug_test:
            print()
            print("test(" + self.coerce(c) + ")...")

        outcome = self._test(c)

        # Statistics about actually executed tests
        self.n_tests += 1
        if outcome == self.FAIL:
            self.n_fails += 1
        elif outcome == self.PASS:
            self.n_passes += 1
        elif outcome == self.UNRESOLVED:
            self.n_unres += 1

        if self.debug_test:
            print("test(" + self.coerce(c) + ") = " + outcome)

        if self.cache_outcomes:
            self.outcome_cache.add(c, outcome)

        return outcome

    def _test(self, c):
        """Stub to overload in subclasses"""
        return self.UNRESOLVED        # Placeholder

    def init_counting(self):
        self.n_tests = 0
        self.n_passes = 0
        self.n_fails = 0
        self.n_unres = 0

    def get_counting(self):
        return {
            "TESTS": self.n_tests,
            "PASS": self.n_passes,
            "FAIL": self.n_fails,
            "UNRES": self.n_unres}

    # Splitting

    def split(self, c, n):
        """Split C into [C_1, C_2, ..., C_n]."""
        if self.debug_split:
            print("split(" + self.coerce(c) + ", " + n + ")...")

        outcome = self._split(c, n)

        if self.debug_split:
            print("split(" + self.coerce(c) + ", " + n + ") = " + outcome)

        return outcome

    def _split(self, c, n):
        """Stub to overload in subclasses"""
        subsets = []
        start = 0
        for i in range(n):
            subset = c[start:int(start + (len(c) - start) / (n - i))]
            subsets.append(subset)
            start = start + len(subset)
        return subsets

    # Resolving

    def resolve(self, csub, c, direction):
        """If direction == ADD, resolve inconsistency by adding deltas
          to CSUB.  Otherwise, resolve by removing deltas from CSUB."""

        if self.debug_resolve:
            print("resolve(" + csub + ", " + self.coerce(c) + ", " +
                  direction + ")...")

        outcome = self._resolve(csub, c, direction)

        if self.debug_resolve:
            print("resolve(" + csub + ", " + self.coerce(c) + ", " +
                  direction + ") = " + outcome)

        return outcome

    def _resolve(self, csub, c, direction):
        """Stub to overload in subclasses."""
        # By default, no way to resolve
        return None

    # Test with fixes
    def test_and_resolve(self, csub, r, c, direction):
        """Repeat testing CSUB + R while unresolved."""

        initial_csub = csub[:]
        c2 = self.__listunion(r, c)

        csubr = self.__listunion(csub, r)
        t = self.test(csubr)

        # necessary to use more resolving mechanisms which can reverse each
        # other, can (but needn't) be used in subclasses
        self._resolve_type = 0

        while t == self.UNRESOLVED:
            self.__resolving = 1
            csubr = self.resolve(csubr, c, direction)

            if csubr is None:
                # Nothing left to resolve
                break

            if len(csubr) >= len(c2):
                # Added everything: csub == c2. ("Upper" Baseline)
                # This has already been tested.
                csubr = None
                break

            if len(csubr) <= len(r):
                # Removed everything: csub == r. (Baseline)
                # This has already been tested.
                csubr = None
                break

            t = self.test(csubr)

        self.__resolving = 0
        if csubr is None:
            return self.UNRESOLVED, initial_csub

        # assert t == self.PASS or t == self.FAIL
        csub = self.__listminus(csubr, r)
        return t, csub

    # Inquiries
    def resolving(self):
        """Return 1 while resolving."""
        return self.__resolving

    # Logging

    def report_progress(self, c, title):
        if self.verbose and len(c) != self.__last_reported_length:
            print()
            print(title + ": " + str(len(c)) + " deltas left:", self.coerce(c))
            self.__last_reported_length = len(c)

    # Delta Debugging (old ESEC/FSE version)

    def old_dd(self, c, r=[], n=2):
        """Return the failure-inducing subset of C"""

        assert self.test([]) == dd.PASS
        assert self.test(c) == dd.FAIL

        if self.debug_dd:
            print("dd(" + self.pretty(c) + ", " + repr(r) + ", " + str(n) + ")...")

        outcome = self._old_dd(c, r, n)

        if self.debug_dd:
            print("dd(" + self.pretty(c) + ", " + repr(r) + ", " + str(n) +
                  ") = " + outcome)

        return outcome

    def _old_dd(self, c, r, n):
        """Stub to overload in subclasses"""

        if r == []:
            assert self.test([]) == self.PASS
            assert self.test(c) == self.FAIL
        else:
            assert self.test(r) != self.FAIL
            assert self.test(c + r) != self.PASS

        assert self.__listintersect(c, r) == []

        if len(c) == 1:
            # Nothing to split
            return c

        run = 1
        next_c = c[:]
        next_r = r[:]

        # We replace the tail recursion from the paper by a loop
        while 1:
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

            # Check subsets
            ts = []
            for i in range(n):
                if self.debug_dd:
                    print("dd: trying cs[" + i + "] =", self.pretty(cs[i]))

                t, cs[i] = self.test_and_resolve(cs[i], r, c, self.REMOVE)
                ts.append(t)
                if t == self.FAIL:
                    # Found
                    if self.debug_dd:
                        print("dd: found", len(cs[i]), "deltas:",)
                        print(self.pretty(cs[i]))
                    return self.dd(cs[i], r)

            # Check complements
            cbars = []
            tbars = []

            for i in range(n):
                cbar = self.__listminus(c, cs[i] + r)
                tbar, cbar = self.test_and_resolve(cbar, r, c, self.ADD)

                doubled = self.__listintersect(cbar, cs[i])
                if doubled != []:
                    cs[i] = self.__listminus(cs[i], doubled)

                cbars.append(cbar)
                tbars.append(tbar)

                if ts[i] == self.PASS and tbars[i] == self.PASS:
                    # Interference
                    if self.debug_dd:
                        print("dd: interference of", self.pretty(cs[i]),)
                        print("and", self.pretty(cbars[i]))

                    d = self.dd(cs[i][:], cbars[i] + r)
                    dbar = self.dd(cbars[i][:], cs[i] + r)
                    return d + dbar

                if ts[i] == self.UNRESOLVED and tbars[i] == self.PASS:
                    # Preference
                    if self.debug_dd:
                        print("dd: preferring", len(cs[i]), "deltas:",)
                        print(self.pretty(cs[i]))

                    return self.dd(cs[i][:], cbars[i] + r)

                if ts[i] == self.PASS or tbars[i] == self.FAIL:
                    if self.debug_dd:
                        excluded = self.__listminus(next_c, cbars[i])
                        print("dd: excluding", len(excluded), "deltas:",)
                        print(self.pretty(excluded))

                    if ts[i] == self.PASS:
                        next_r = self.__listunion(next_r, cs[i])
                    next_c = self.__listintersect(next_c, cbars[i])
                    self.report_progress(next_c, "dd")

            next_n = min(len(next_c), n * 2)

            if next_n == n and next_c[:] == c[:] and next_r[:] == r[:]:
                # Nothing left
                if self.debug_dd:
                    print("dd: nothing left")
                return next_c

            # Try again
            if self.debug_dd:
                print("dd: try again")

            c = next_c
            r = next_r
            n = next_n
            run = run + 1

    def test_mix(self, csub, c, direction):
        # Test the configuration CSUB.  If it fails, return FAIL.
        # Goal: minimize the difference by reducing the failing test case.
        if self.minimize:
            # print("Minimization on ", self.coerce(csub))
            (t, csub) = self.test_and_resolve(csub, [], c, direction)
            if t == self.FAIL:
                return (t, csub)

        # Test the complement of CSUB.  If it passes, return FAIL.
        # Goal: minimize the difference only by extending the passing test case.
        # If complement passes, then failure must be in original.
        if self.maximize:
            csubbar = self.__listminus(self.CC, csub)
            cbar = self.__listminus(self.CC, c)
            if direction == self.ADD:
                directionbar = self.REMOVE
            else:
                directionbar = self.ADD
            # print("Maximization on ", self.coerce(csubbar))
            (tbar, csubbar) = self.test_and_resolve(csubbar, [], cbar,
                                                    directionbar)
            csub = self.__listminus(self.CC, csubbar)

            if tbar == self.PASS:
                t = self.FAIL
            elif tbar == self.FAIL:
                t = self.PASS
            else:
                t = self.UNRESOLVED

        return (t, csub)

    # Delta Debugging (new ISSTA version)

    def ddgen(self, c, minimize, maximize):
        """Return a 1-minimal failing subset of C"""

        self.minimize = minimize
        self.maximize = maximize

        n = 2
        self.CC = c

        if self.debug_dd:
            print("dd(%s, %d)..." % (self.pretty(c), n))

        outcome = self._dd(c, n)

        if self.debug_dd:
            print("dd(%s, %d) = %s" % (self.pretty(c), n, outcome))

        return outcome

    def _dd(self, c, n):
        """Stub to overload in subclasses"""

        assert self.test([]) == self.PASS

        run = 1
        cbar_offset = 0

        # We replace the tail recursion from the paper by a loop
        while 1:
            tc = self.test(c)
            assert tc == self.FAIL or tc == self.UNRESOLVED

            if n > len(c):
                # No further minimizing
                if self.verbose:
                    print("dd: done")
                return c

            self.report_progress(c, "dd")

            cs = self.split(c, n)

            if self.verbose:
                print()
                print("dd (run #%d): trying" % run)
                for i in range(n):
                    if i > 0:
                        print("+",)
                    print(len(cs[i]),)
                print()

            c_failed = 0
            cbar_failed = 0

            next_c = c[:]
            next_n = n

            # Check subsets
# for i in range(n):
# if self.debug_dd:
# print("dd: trying", self.pretty(cs[i]))

# (t, cs[i]) = self.test_mix(cs[i], c, self.REMOVE)

# if t == self.FAIL:
# Found
# if self.debug_dd:
# print("dd: found", len(cs[i]), "deltas:",)
# print(self.pretty(cs[i]))

# c_failed = 1
# next_c = cs[i]
# next_n = 2
# cbar_offset = 0
# self.report_progress(next_c, "dd")
# break

            if not c_failed:
                # Check complements
                cbars = n * [self.UNRESOLVED]

                # print("cbar_offset =", cbar_offset)

                for j in range(n):
                    i = int((j + cbar_offset) % n)
                    cbars[i] = self.__listminus(c, cs[i])
                    # * This is the core of delta debugging!
                    t, cbars[i] = self.test_mix(cbars[i], c, self.ADD)
                    doubled = self.__listintersect(cbars[i], cs[i])
                    if doubled != []:
                        cs[i] = self.__listminus(cs[i], doubled)

                    if t == self.FAIL:
                        if self.debug_dd:
                            print("dd: reduced to", len(cbars[i]),)
                            print("deltas:",)
                            print(self.pretty(cbars[i]))

                        cbar_failed = 1
                        next_c = self.__listintersect(next_c, cbars[i])
                        next_n = next_n - 1
                        self.report_progress(next_c, "dd")

                        # In next run, start removing the following subset
                        cbar_offset = i
                        break

            if not c_failed and not cbar_failed:
                if n >= len(c):
                    # No further minimizing
                    print("dd: done")
                    return c

                next_n = min(len(c), n * 2)
                if self.verbose:
                    print("dd: increase granularity to", next_n)
                cbar_offset = (cbar_offset * next_n) / n

            c = next_c
            n = next_n
            run = run + 1

    def ddmin(self, c):
        return self.ddgen(c, 1, 0)

    def ddmax(self, c):
        return self.ddgen(c, 0, 1)

    def ddmix(self, c):
        return self.ddgen(c, 1, 1)

    # General delta debugging (new TSE version)

    def dddiff(self, c):
        n = 2

        if self.debug_dd:
            print("dddiff(" + self.pretty(c) + ", " + n + ")...")

        outcome = self._dddiff([], c, n)

        if self.debug_dd:
            print("dddiff(" + self.pretty(c) + ", " + n + ") = " +
                  outcome)

        return outcome

    def _dddiff(self, c1, c2, n):
        run = 1
        cbar_offset = 0

        c1_orig = c1[:]
        c2_orig = c2[:]

        # We replace the tail recursion from the paper by a loop
        while 1:
            if self.debug_dd:
                print("dd: c1 =", self.pretty(c1))
                print("dd: c2 =", self.pretty(c2))

            if self.assume_axioms_hold:
                t1 = self.PASS
                t2 = self.FAIL
            else:
                t1 = self.test(c1)
                t2 = self.test(c2)

            assert t1 == self.PASS
            assert t2 == self.FAIL
            assert self.__listsubseteq(c1, c2)

            c = self.__listminus(c2, c1)

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
            next_c2 = c2[:]
            next_n = n

            # Check subsets
            for j in range(n):
                i = (j + cbar_offset) % n

                if self.debug_dd:
                    print("dd: trying", self.pretty(cs[i]))

                (t, csub) = self.test_and_resolve(cs[i], c1, c, self.REMOVE)
                csub = self.__listunion(c1, csub)

                if t == self.FAIL and t1 == self.PASS:
                    # Found
                    progress = 1
                    next_c2 = csub
                    next_n = 2
                    cbar_offset = 0

                    if self.debug_dd:
                        print("dd: reduce c2 to", len(next_c2), "deltas:",)
                        print(self.pretty(next_c2))
                    break

                if t == self.PASS and t2 == self.FAIL:
                    # Reduce to complement
                    progress = 1
                    next_c1 = csub
                    next_n = max(next_n - 1, 2)
                    cbar_offset = i

                    if self.debug_dd:
                        print("dd: increase c1 to", len(next_c1), "deltas:",)
                        print(self.pretty(next_c1))
                    break

                csub = self.__listminus(c, cs[i])
                (t, csub) = self.test_and_resolve(csub, c1, c, self.ADD)
                csub = self.__listunion(c1, csub)

                if t == self.PASS and t2 == self.FAIL:
                    # Found
                    progress = 1
                    next_c1 = csub
                    next_n = 2
                    cbar_offset = 0

                    if self.debug_dd:
                        print("dd: increase c1 to", len(next_c1), "deltas:",)
                        print(self.pretty(next_c1))
                    break

                if t == self.FAIL and t1 == self.PASS:
                    # Increase
                    progress = 1
                    next_c2 = csub
                    next_n = max(next_n - 1, 2)
                    cbar_offset = i

                    if self.debug_dd:
                        print("dd: reduce c2 to", len(next_c2), "deltas:",)
                        print(self.pretty(next_c2))
                    break

            if progress:
                if self.animate is not None:
                    self.animate.write_outcome(
                        self.__listminus(next_c1, c1_orig), self.PASS)
                    self.animate.write_outcome(
                        self.__listminus(c2_orig, next_c2), self.FAIL)
                    self.animate.write_outcome(
                        self.__listminus(next_c2, next_c1), self.DIFFERENCE)
                    self.animate.next_frame()

                self.report_progress(self.__listminus(next_c2, next_c1), "dd")
            else:
                if n >= len(c):
                    # No further minimizing
                    if self.verbose:
                        print("dd: done")
                    return (c, c1, c2)

                next_n = min(len(c), n * 2)
                if self.verbose:
                    print("dd: increase granularity to", next_n)
                cbar_offset = (cbar_offset * next_n) / n

            c1 = next_c1
            c2 = next_c2
            n = next_n
            run = run + 1

    def dd(self, c):
        return self.dddiff(c)           # Backwards compatibility

    # ARD - compute All Relevant Deltas by excessivly applying ddmin.

    # Helper function: compute all different atoms of the term
    def condense_formula(self, formula):
        elems = []
        result = []
        for and_term in formula:
            elems.extend(and_term)
        for e in elems:
            if not e in result:
                result.append(e)
        # result.sort()
        return result

    # Helper function: print a term in human readable form
    def pretty_formula(self, formula):
        ostr = ""
        for and_term in formula:
            print(ostr + "(",)
            astr = ""
            for el in and_term:
                print(astr + el,)
                astr = " and "
            print(")",)
            ostr = " or "

    # Helper function: compute all sets, where min_set is not subset
    def non_supersets(self, superset, min_set):
        result = []
        for e in min_set:
            result.append(self.__listminus(superset, [e]))
        return result

    # ARD - compute All Relevant Deltas by excessivly applying ddmin.
    # ard() computes a logical formula
    def ard(self, c):
        formula = []

        testsets = [c[:]]

        while testsets != []:
            if self.debug_dd:
                print("ard: Testsets")
                print(testsets)

            # First run
            testset = testsets.pop()
            min_set = self.ddmin(testset)

            # remove subsumed testsets
            new_testsets = []
            old_testsets = []
            for test in testsets:
                if self.__listsubseteq(min_set, test):
                    new_testsets.extend(self.non_supersets(test, min_set))
                else:
                    old_testsets.append(test)

            testsets = old_testsets

            # Create new testsets
            new_testsets.extend(self.non_supersets(testset, min_set))

            # Retest new testsets
            for test in new_testsets:
                outcome = self.test(test)
                if outcome == self.FAIL:
                    testsets.append(test)
                elif outcome == self.UNRESOLVED:
                    if self.debug_dd:
                        print("ard: UNRESOLVED don't know what to do yet")
                    # Gibt es eine Untermenge, die Fail ergibt?
                    # ist test ein geeigneter Startpunkt fuer ddmin?
                else:
                    pass  # (forget this nabla)

            # Extend formula
            formula.append(min_set)

        if self.debug_dd:
            self.pretty_formula(formula)

            print("Needed " + self.n_tests + ":P:" + self.n_passes +
                  "/F:" + self.n_fails + "/U:" + self.n_unres)

        # Return a set of all relevant deltas, and a formula
        return (self.condense_formula(formula), [], c, formula)


if __name__ == '__main__':
    # Test the outcome cache
    oc_test()

    # Define our own DD class, with its own test method
    class MyDD(DD):
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

    # print("Minimizing failure-inducing input...")
    # list = range(1, 9)
    # for i in range (1, 255):
    #    list.append(i)

    # c = mydd.ddmax(list)
    # print("The 1-minimal failure-inducing input is", c)
    # print("Removing any element will make the failure go away.")
    # print()

    list = ["A King there was in days of old,",
            "ere Men yet walked upon the mould.",
            "There Juliet and her Romeo,",
            "beneath the stars sat."]
    print("Computing the failure-inducing difference...")
    (c, c1, c2) = mydd.dd(list)        # Invoke DD
    print("The 1-minimal failure-inducing difference is", c)
    print(c1, "passes,", c2, "fails")


# Local Variables:
# mode: python
# End:
