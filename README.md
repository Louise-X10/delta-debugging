# Delta-Debugger

This repo is a modified version of [grimm-co/delta-debugging](https://github.com/grimm-co/delta-debugging/tree/master). The modified delta-debugger is in `DD_mod.py`, and example usages are provided in `examples/`. 

# Examples

`example_ddmod.ipynb` is a toy example on string inputs, and `example_ddmod2.ipynb` is a toy example on JSON inputs. `example_ddmod3.ipynb` is an example on binary inputs. 

## Example 3

This example is can be ran on the real-world bug found in `boringssl`. The bug can be reproduced using [ARVO](https://github.com/n132/ARVO-Meta/tree/main/). On Docker, run

```
docker run -it n132/arvo:2692-vul arvo
```

The crashing input can be downloaded from [OSSFuzz](https://issues.oss-fuzz.com/issues/42488781). Valid inputs can be found at the seed corpus directory `boringssl/fuzz/server_corpus`. For example, see `example_ddmod3.sh` for a list of commands I ran to launch delta-debugger. 