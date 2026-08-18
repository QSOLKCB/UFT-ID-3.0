# VOP-2019-MEI Derivation and Assumption Audit

**Status:** source-faithful reproduction of the 2019 arithmetic with explicit separation between established premises, source assumptions, algebra, and physical interpretation.

## 1. Binary information model

For an unbiased binary variable,

```text
P = {1/2, 1/2}
```

and base-2 Shannon entropy gives

```text
H(X) = 1 bit.
```

For `N` independent binary information-bearing elements, the source writes

```text
Omega = 2^(N H(X))
S_info = k_B ln(Omega)
       = N k_B H(X) ln 2.
```

With `H(X)=1`,

```text
S_info = N k_B ln 2.
```

This part is algebraically reproducible from the declared binary model.

## 2. Erasure model

The source models an erased memory as having one information state, hence

```text
H_erased = 0
S_info,final = 0
Delta S_info = -N k_B ln 2.
```

Using the second-law condition

```text
Delta S_total = Delta S_phys + Delta S_info >= 0,
```

one obtains the lower-bound condition

```text
Delta S_phys >= N k_B ln 2
```

for the compensating physical entropy increase under this idealized bookkeeping.

For one bit and a thermal reservoir at temperature `T`, the reversible limiting heat scale is

```text
Q_min = k_B T ln 2.
```

This is the Landauer erasure scale. It is a statement about a logically irreversible process under stated thermodynamic assumptions.

## 3. Source-text sign issue

The 2019 paper's p. 2 prose prints an inequality for the physical-entropy/heat term whose direction is inconsistent with the immediately preceding total-entropy equation and the conventional lower-bound statement. PR #6 does not silently normalize that sentence.

The reproduction therefore records two objects:

1. `SOURCE_TEXT_AS_PRINTED`, including the inconsistent inequality direction;
2. `THERMODYNAMIC_LOWER_BOUND_FORM`, used only when describing the established Landauer premise.

Eq. (6) does not depend on choosing one inequality direction once the paper identifies the characteristic energy scale with `k_B T ln 2`.

## 4. The nontrivial physical bridge

The paper next proposes that the ability of a written bit to persist without ongoing dissipation can be explained by assigning the stored bit a finite mass. The central identification is effectively

```text
E_bit := k_B T ln 2.
```

This is **not merely the Landauer bound rewritten**. Landauer supplies a minimum thermodynamic cost/heat scale for logically irreversible erasure in the relevant setting. The assignment of that process scale to an intrinsic energy of the stored logical state is an additional physical identification.

UFT-ID therefore classifies this step as:

```text
source claim:          recorded
arithmetic role:       required premise for Eq. (6)
physical validation:   unresolved
```

## 5. Mass conversion

Conditional on the additional identification, ordinary mass-energy equivalence gives

```text
m_bit c^2 = E_bit
```

and therefore

```text
m_bit(T) = k_B T ln 2 / c^2.       (source Eq. 6)
```

This implication is algebraically valid **conditional on** `E_bit = k_B T ln 2` representing an ordinary stored energy contribution.

## 6. Numerical reproduction

Using the exact SI defining constants

```text
k_B = 1.380649e-23 J/K
c   = 299792458 m/s
```

and `T=300 K`,

```text
k_B T ln 2 = 2.870978885078724e-21 J
m_bit      = 3.1943948174115975e-38 kg.
```

The paper reports approximately `3.19e-38 kg`, reproduced to its displayed precision.

At `T=2.73 K`,

```text
m_bit = 2.9068992838445533e-40 kg,
```

which reproduces the paper's reported `2.91e-40 kg`.

For the paper's decimal storage convention,

```text
1 TB = 10^12 bytes = 8e12 bits,
```

so at `300 K`,

```text
Delta m = 8e12 * m_bit
        = 2.5555158539292776e-25 kg.
```

The paper reports `2.5e-25 kg`; the difference is ordinary rounding at the displayed precision.

## 7. Temperature dependence

Under Eq. (6),

```text
m_bit(T) proportional to T.
```

That temperature dependence is an exact consequence of the source formula. It does not independently validate the formula's physical interpretation.

At `T=0`, Eq. (6) returns zero. PR #6 records that mathematical limit but does not promote the paper's further interpretive statement about whether information can exist at absolute zero.

## 8. State versus process distinction

The audit keeps the following distinct:

```text
logical state of a memory
thermodynamic state of its physical implementation
erasure process
work performed during a protocol
heat dissipated to an environment
internal/stored energy of a state
rest-mass contribution
```

A process-dependent minimum work or heat bound does not automatically equal a state function for every physical encoding of the same logical bit.

## 9. Reproduction verdict

```text
binary Shannon arithmetic                         REPRODUCED
source information-entropy algebra                REPRODUCED
Landauer lower-bound scale                        ESTABLISHED EXTERNAL PREMISE, SCOPE-QUALIFIED
source p.2 inequality prose                       INTERNAL SIGN INCONSISTENCY RECORDED
E_bit = k_B T ln 2 as intrinsic stored energy     SOURCE ASSUMPTION / PHYSICAL BRIDGE UNVALIDATED
Eq. (6) conditional algebra                       REPRODUCED
300 K bit-mass number                             REPRODUCED
2.73 K bit-mass number                            REPRODUCED
1 TB mass-change number                           REPRODUCED TO SOURCE ROUNDING
physical existence of intrinsic bit mass          UNRESOLVED
experimental confirmation                         NOT ESTABLISHED BY THIS REPRODUCTION
```

The strongest conclusion supported by PR #6 is therefore:

> The central numerical predictions of the 2019 paper follow deterministically from Eq. (6), but Eq. (6) itself requires an additional identification of the Landauer erasure energy scale with intrinsic stored-bit energy. Reproducing the arithmetic does not validate that physical identification.
