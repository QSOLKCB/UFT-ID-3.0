# VOP-2019-MEI Dimensional Audit

This audit checks units independently of the physical interpretation.

## Defining constants

```text
[k_B] = J K^-1 = kg m^2 s^-2 K^-1
[T]   = K
[ln2] = 1
[c]   = m s^-1
```

Therefore

```text
[k_B T ln2] = J = kg m^2 s^-2.
```

If the source identification

```text
E_bit = k_B T ln2
```

is accepted as a stored energy, then

```text
[m_bit] = [E_bit / c^2]
        = (kg m^2 s^-2) / (m^2 s^-2)
        = kg.
```

So source Eq. (6)

```text
m_bit = k_B T ln2 / c^2
```

is dimensionally consistent.

## What dimensional consistency does not establish

Dimensional consistency cannot decide whether the Landauer erasure scale is an intrinsic energy of a stored bit. Both a process energy and a stored-state energy have units of joules.

```text
SAME_DIMENSION != SAME_PHYSICAL_QUANTITY
DIMENSIONALLY_VALID != DERIVED_FROM_PREMISES
```

## Storage-device prediction

For a count `N_bits`,

```text
Delta m = N_bits * m_bit.
```

`N_bits` is dimensionless, so `Delta m` has unit kg.

For the source's decimal convention,

```text
1 TB = 10^12 bytes = 8e12 bits.
```

No binary-tebibyte convention is used in reproducing the paper's stated example.

## Temperature sweep

Because the source formula is linear in temperature,

```text
d m_bit / dT = k_B ln2 / c^2
```

with units

```text
kg K^-1.
```

The linear scaling is a mathematical property of Eq. (6), not independent empirical evidence for intrinsic information mass.
