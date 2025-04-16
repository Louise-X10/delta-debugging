# Delta-Debugger

This repo is a modified version of [grimm-co/delta-debugging](https://github.com/grimm-co/delta-debugging/tree/master). The modified delta-debugger is in `DD_mod.py`, and example usages are provided in `examples/`. Files in `testing/` were used for developmental purposes only. 

# Examples

`example_ddmod.ipynb` is a toy example on string inputs, and `example_ddmod2.ipynb` is a toy example on JSON inputs. `example_ddmod3.ipynb` is an example on binary inputs. 

## Example 3

This binary example can be ran on the real-world bug found by OSS Fuzz, for example a bug in [boringssl](https://github.com/google/boringssl/tree/5386d908a663a424d154cbae7f76f2266c60c2fe). This bug can be reproduced using [ARVO](https://github.com/n132/ARVO-Meta/tree/main/). On Docker, run

```
docker run -it n132/arvo:2692-vul arvo
```

The crashing input can be downloaded from [OSS Fuzz issues](https://issues.oss-fuzz.com/issues/42488781). Valid inputs can be found at the seed corpus directory `boringssl/fuzz/server_corpus`. The target program is the `server` fuzzer. For example, see `example_ddmod3.sh` for a list of commands I ran to launch delta-debugger. Unfortunately, it doesn't seem to make any improvements on the crashing input. 


## Example 4

This JSON example can be ran on the real-world bug found by OSS Fuzz, for example a bug in [commons-codec](https://github.com/apache/commons-codec/tree/master). This bug can be reproduced using [ARVO](https://github.com/n132/ARVO-Meta/tree/main/). On Docker, run

```
docker run -it n132/arvo:64367-vul arvo
```

Run `arvo` to reproduce the bug, which prints the seed used and saves the reproducer file. The crashing input can be found by running the fuzzer with the given seed. The target program is the `PhoeneticEngineFuzzer` program, as can be seen [here](https://github.com/google/oss-fuzz/blob/master/projects/apache-commons-codec/PhoneticEngineFuzzer.java). Therefore, I manually created a valid input to be the binary data representing `Hello`. 