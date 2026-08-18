# VOP-2019-MEI Matched-Control Matrix

The 2019 paper proposes a mass difference between erased and information-bearing memory states. A useful test must separate **logical information content** from ordinary physical energy differences in the storage implementation.

These are experimental-design requirements, not claims that a particular device already satisfies them.

## Control families

| Control | Hold fixed | Change | Question |
|---|---|---|---|
| C1 matched physical energy | total measured internal energy, temperature, device composition, field configuration as far as experimentally controllable | logical pattern / encoded payload | Does logical information alone change measured mass? |
| C2 matched logical information | logical bit count and Shannon information under the declared coding | physical encoding energy, coercivity, charge state or other device-level energy variables | Does measured mass track implementation energy rather than logical information? |
| C3 reversible logical transform | number of logical states and information content | `0 <-> 1` permutation without erasure | Does a logically reversible change produce the proposed mass signal? |
| C4 erase/write cycle | same device, thermal environment and measurement protocol | erased versus written ensemble | Can the predicted signal be separated from ordinary write/erase heat, hysteresis and relaxation? |
| C5 coding relabel | same physical microstate ensemble where possible | semantic interpretation / codebook labels | Does semantic relabeling alter the predicted mass? It should not if the claim is about physical storage states rather than human meaning. |
| C6 temperature sweep | device and logical payload class | equilibrium temperature | Does any residual signal scale linearly with `T` as Eq. (6) predicts? |
| C7 dummy thermal cycle | logical state unchanged | matched heating/cooling and elapsed time | Can drift or buoyancy/thermal-systematics mimic the predicted mass change? |

## Null hypotheses

The minimum null model for a storage experiment is:

```text
observed mass difference = ordinary physical energy difference / c^2 + measurement systematics
```

A stronger MEI-specific result would need to show an excess component tied to the declared logical-information variable after ordinary physical energy accounting.

## Required measurement bookkeeping

Any future empirical test should record at least:

```text
device identity
storage technology
logical coding convention
physical microstate definition
erased-state definition
written-state definition
temperature and thermal history
write/erase protocol
elapsed relaxation time
power/heat history
magnetic/electric/mechanical field state
mass measurement method
blind/randomized condition order
calibration and drift controls
uncertainty model
```

## Falsification-friendly prediction

Under the source formula, a positive claim should specify the predicted excess mass as

```text
Delta m_MEI = Delta N_info * k_B T ln2 / c^2
```

only after defining what `Delta N_info` means operationally for the physical memory under test.

If a matched-energy comparison shows no excess mass at sensitivity comfortably below the predicted `Delta m_MEI`, that would count against the intrinsic-bit-mass identification for that declared system. If ordinary state-energy differences already account for the observed mass, the experiment does not uniquely support MEI.

```text
LOGICAL_DIFFERENCE != PHYSICAL_ENERGY_DIFFERENCE
CORRELATION_WITH_WRITE_STATE != INFORMATION_SPECIFIC_MASS
```
