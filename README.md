# Delta-Debugger

This repo is a modified version of [grimm-co/delta-debugging](https://github.com/grimm-co/delta-debugging/tree/master). The modified delta-debugger is in `DD_mod.py`, and example usages are provided in `examples/`. Files in `testing/` were used for developmental purposes only. 

# Implementations

The `ddiff_max` method takes a **crashing input** and **valid input**, first calls `ddmin` to minimize the crashing input, then calls `ddiff_mods` to compute a **maximized crashing input** that is minimally close to the valid input. This is done by definint a list of modifications that can be applied to change the (min) crashing input into the valid input. The iterative procedure is similar to that of the original delta-debugger, except that I only check subsets, and don't check subset complements. This is because I only need to "narrow down" on one side (from crashing towards valid), rather than "narrow down" on both sides towards the middle, which the original delta-debugger aims for. 

The `DDMods` class has an argument `.binary` that signals whether it accepts strings or binary data as input. When using this maximizing delta-debugger, the user must instantiate an instance of `DDMods` with a `_text()` method that parses input, runs target program on input, and returns `FAIL` or `PASS` accordint to whether program crashed on given input. The user must also use the correct `.binary` setting. 

P.S. Note that the valid input here may or may not cause the program to crash. We only call it "valid" because it is chosen from a seed corpus or is an input that user would expect, hence is a well-structured input that should not crash the program. If it does indeed crash the program, then it only signifies that the bug in the program affects these well-structured inputs as well. 

P.S. While my delta-debugger performs minimization on the given failing input, sometimes they are already minimal when output by fuzzers. Thus, I also have an option to skip the minimization step, by setting `skipmin=True` when calling `ddiff_max`. It is set to False for all my evaluations to be safe. 

# Examples

`example_ddmod.ipynb` is a toy example on string inputs, and `example_ddmod2.ipynb` is a toy example on JSON inputs. `example_ddmod3.py` and `example_ddmod4.py` are real-world bug examples on binary inputs. 

P.S. `example_dd.ipynb` is a simple demonstration for how the original delta debugger works to minimize failure inputs. A similar example is also available at [grimm-co/delta-debugging](https://github.com/grimm-co/delta-debugging/blob/master/scripts/dd-algorithm-example.py)

## Toy Examples

### Example 1

This target program takes string as inputs, and crashes if the input doesn't have `<` or `;`, cotains one `1` and three `2`.  The crashing input is ` "1222>"` which can be minimized to `"1222"`. The valid input is `"<55513>;"`. The resulting maximized crashing input is `551222`. 

### Example 2

This target program takes JSON inputs, and crashes if the input contains a list value. The crashing input is `{"baz": 7, "baaa": [1, 2]}` which can be minimized to `"{"":7,"":[]}"`. The valid input is `{ "foo": "bar" }`. The resulting maximized crashing input is `{ "foo": 7,"":[]}`. 

## Boringssl Examples

I took [boringssl](https://github.com/google/boringssl/tree) as an example to see how well my delta-debugger works on real-world bugs found by OSS Fuzz. I tested on three kinds of bugs discovered, all of which can be reproduced using [ARVO](https://github.com/n132/ARVO-Meta/tree/main/).

### Example 3

This boringssl [bug](https://github.com/n132/ARVO-Meta/blob/main/meta/2692.json) has crash_type "Incorrect-function-pointer-type". The crashing input can be found at [OSS Fuzz issues](https://issues.oss-fuzz.com/issues/42488781), or directly downloaded from [here](https://oss-fuzz.com/download?testcase_id=6195774643634176). To reproduce the bug, run `arvo` in the following Docker container, 

```
docker run -it n132/arvo:2692-vul bash
```

Valid inputs can be found at the seed corpus directory `boringssl/fuzz/server_corpus`. The target program is the `server` fuzzer. For example, see `example_ddmod3.sh` for the list of commands I ran to launch delta-debugger. The resulting maximized crashing input is closer to the original crashing input, improving from 410 edit distance to 396 edit distance. 

### Example 3.2

This boringssl [bug](https://github.com/n132/ARVO-Meta/blob/main/meta/10140.json) has crash_type "Use-of-uninitialized-value". The crashing input can be directly downloaded from [here](https://oss-fuzz.com/download?testcase_id=5632355033677824). To reproduce the bug, run `arvo` in the following Docker container, 

```
docker run -it n132/arvo:10140-vul bash
```

See `example_ddmod3.2.sh` for the list of commands I ran.
The crashing input is `b' '`, which is already minimal. The valid input is `b'-----BEGIN O--------'` (which actually crashes the prgram as well), and the resulting maximized crashing input is `b'-----BEG '`, which is 11 changes away from the valid input (originally 19 changes away). 

### Example 3.3

This boringssl [bug](https://github.com/n132/ARVO-Meta/blob/main/meta/9808.json) has crash_type "Heap-buffer-overflow READ 1". The crashing input can be directly downloaded from [here](https://oss-fuzz.com/download?testcase_id=5807097051611136). To reproduce the bug, run `arvo` in the following Docker container, 

```
docker run -it n132/arvo:9808-vul bash
```

See `example_ddmod3.3.sh` for the list of commands I ran. The crashing input is `b'-'`, which is already minimal. After calling my delta-debugger, I obtain a maximal crashing input that is much closer to the valid input, being only 1 edit distance away (originally 126 edits away). 

## Apache-Commons-Code Examples

### Example 4

This commons-codec [bug](https://issues.oss-fuzz.com/issues/42530374) has crash_type "Security exception". The crashing input can be directly downloaded from [here](https://oss-fuzz.com/download?testcase_id=6726368628703232), or reproduced by running `arvo` in the following Docker container, 

(This binary example is ran on the real-world bug found by OSS Fuzz, specifically a bug in [commons-codec](https://github.com/apache/commons-codec/tree/master).)
To reproduce the bug, 

```
docker run -it n132/arvo:64367-vul arvo
```

Run `arvo` to reproduce the bug, which would print the seed used and save the failure reproducer file. The crashing input is `b'7%eeeee7%'`. The target program is the `PhoeneticEngineFuzzer` program, and can be seen [here](https://github.com/google/oss-fuzz/blob/master/projects/apache-commons-codec/PhoneticEngineFuzzer.java). Therefore, I manually created a valid input to be the binary data representing `Hello`. The resulting maximized crashing input is `b'elloeee7%'`. See `example_ddmod4.sh` for the list of commands that I ran.
### Example 4.2
This commons-codec [This bug](https://issues.oss-fuzz.com/issues/42530537) has crash_type "Uncaught exception". The crashing input can be directly downloaded from [here](https://oss-fuzz.com/download?testcase_id=6195774643634176). This bug is not available on ARVO, so I had to reproduce from OSS Fuzz. Unfortunately I wasn't able to reproduce the bug successfully. Here are some attempts I made for reproducing the bug. 

```
git clone --depth=1 https://github.com/google/oss-fuzz.git
cd oss-fuzz
# Modify projects/apache-commons-code/Dockerfile (see README)
PROJECT_NAME=apache-commons-codec
python infra/helper.py pull_images
python infra/helper.py build_image $PROJECT_NAME
python infra/helper.py build_fuzzers --sanitizer address $PROJECT_NAME
TARGET=LanguageStringEncoderFuzzer
CRASH_INPUT=clusterfuzz-testcase-minimized-LanguageStringEncoderFuzzer-6195774643634176
python infra/helper.py reproduce $PROJECT_NAME $TARGET $CRASH_INPUT
```

The Dockerfile should is modified to clone the first known bad [commit](https://github.com/apache/commons-codec/commit/44e4c4d778c3ab87db09c00e9d1c3260fd42dad5) (which can be found as the regression range in the [OSS Fuzz issue page](https://issues.oss-fuzz.com/issues/42530537)), instead of the most recent commit when the bug has already been fixed. 

```
# Dockerfile

# RUN git clone --depth 1 https://gitbox.apache.org/repos/asf/commons-codec.git commons-codec 
RUN git clone https://gitbox.apache.org/repos/asf/commons-codec.git commons-codec && \
    cd commons-codec && \
    git checkout 44e4c4d778c3ab87db09c00e9d1c3260fd42dad5

```
