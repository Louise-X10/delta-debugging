# Delta-Debugger

This repo is a modified version of [grimm-co/delta-debugging](https://github.com/grimm-co/delta-debugging/tree/master). The modified delta-debugger is in `DD_mod.py`, and example usages are provided in `examples/`. Files in `testing/` were used for developmental purposes only. 

# Implementations

The `ddmax` method takes a **crashing input** and **valid input**, first calls `ddmin` to minimize the crashing input, then computes a **maximized crashing input** that is minimally close to the valid input. This is done by definint a list of modifications that can be applied to change the (min) crashing input into the valid input. The iterative procedure is similar to that of the original delta-debugger, except that I only check subsets, and don't check subset complements. This is because I only need to "narrow down" on one side (from crashing towards valid), rather than "narrow down" on both sides towards the middle, which the original delta-debugger aims for. 

The `DDMods` class has an argument `.binary` that signals whether it accepts strings or binary data as input. When using this maximizing delta-debugger, the user must instantiate an instance of `DDMods` with a `_text()` method that parses input, runs target program on input, and returns `FAIL` or `PASS` accordint to whether program crashed on given input. The user must also use the correct `.binary` setting. 

# Examples

`example_ddmod.ipynb` is a toy example on string inputs, and `example_ddmod2.ipynb` is a toy example on JSON inputs. `example_ddmod3.py` and `example_ddmod4.py` are real-world bug examples on binary inputs. 

P.S. `example_dd.ipynb` is a simple demonstration for how the original delta debugger works to minimize failure inputs. A similar example is also available at [grimm-co/delta-debugging](https://github.com/grimm-co/delta-debugging/blob/master/scripts/dd-algorithm-example.py)

## Example 1

This target program takes string as inputs, and crashes if the input doesn't have `<` or `;`, cotains one `1` and three `2`.  The crashing input is ` "1222>"` which can be minimized to `"1222"`. The valid input is `"<55513>;"`. The resulting maximized crashing input is `5551222`. 

## Example 2

This target program takes JSON inputs, and crashes if the input contains a list value. The crashing input is `{"baz": 7, "baaa": [1, 2]}` which can be minimized to `"{"":7,"":[]}"`. The valid input is `{ "foo": "bar" }`. The resulting maximized crashing input is `{ "foo": 7,"":[]}`. 

## Example 3

This binary example is ran on the real-world bug found by OSS Fuzz, specifically a bug in [boringssl](https://github.com/google/boringssl/tree/5386d908a663a424d154cbae7f76f2266c60c2fe). This bug can be reproduced using [ARVO](https://github.com/n132/ARVO-Meta/tree/main/). On Docker, run

```
docker run -it n132/arvo:2692-vul arvo
```

The crashing input can be downloaded from [OSS Fuzz issues](https://issues.oss-fuzz.com/issues/42488781). Valid inputs can be found at the seed corpus directory `boringssl/fuzz/server_corpus`. The target program is the `server` fuzzer. For example, see `example_ddmod3.sh` for a list of commands I ran to launch delta-debugger. Unfortunately, it doesn't seem to make any improvements on the crashing input. Hence the resulting maximized crashing input is the same as the original crashing input. 


## Example 4

This binary example is ran on the real-world bug found by OSS Fuzz, specifically a bug in [commons-codec](https://github.com/apache/commons-codec/tree/master). This bug can be reproduced using [ARVO](https://github.com/n132/ARVO-Meta/tree/main/). On Docker, run

```
docker run -it n132/arvo:64367-vul arvo
```

Run `arvo` to reproduce the bug, which would print the seed used and save the failure reproducer file. The crashing input `b'7%eeeee7%'` can be identified by running the target fuzzer with the given seed. The target program is the `PhoeneticEngineFuzzer` program, as can be seen [here](https://github.com/google/oss-fuzz/blob/master/projects/apache-commons-codec/PhoneticEngineFuzzer.java). Therefore, I manually created a valid input to be the binary data representing `Hello`. The resulting maximized crashing input is `b'elloeeeee7%'`. See `example_ddmod4.sh` for a list of commands I that I ran.