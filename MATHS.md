# UFT-ID 3.0 Mathematical Idea Vault

**Status:** working mathematical notebook. Nothing in this file is automatically a canonical definition, theorem, proof, or physical claim.

Ideas graduate from here only after they are typed, sourced, stress-tested, and moved into `theory/DEFINITIONS.md`, `theory/THEOREM_TARGETS.md`, or a proof/experiment file.

The purpose of this document is to preserve the useful mathematics without allowing attractive notation to outrun its assumptions.

---

## 0. Core discipline

The theory should preserve the following distinctions:

```text
state != observation
observation != representation
representation != ontology
entropy != information in general
entropy change != entropy production
inaccessibility != destruction
compression != loss of declared invariants
formal proof != empirical validation
shared mathematics != shared physical mechanism
```

Every equation below should eventually declare:

- state space;
- admissible set;
- time model;
- dynamics;
- measure/reference distribution;
- observation/coarse-graining map;
- information functional;
- boundary conditions;
- regularity assumptions;
- claim class.

---

## 1. Canonical abstract system

Working object:

\[
\mathfrak U=(S,A,F,\Pi_{\rm lex},O,T,I,C).
\]

Interpretation:

\[
S = \text{total state space},
\]

\[
A\subseteq S = \text{admissible set},
\]

\[
C=\{C_j\} = \text{constraint family},
\]

\[
F = \text{proposed evolution},
\]

\[
\Pi_{\rm lex} = \text{deterministic recovery},
\]

\[
O = \text{observation/coarse-graining map},
\]

\[
T = \text{regime-transport map},
\]

\[
I = \text{declared information functional}.
\]

No component is assumed physical merely because it appears in the tuple.

---

## 2. Admissibility and residuals

### 2.1 Predicate form

\[
A=\{s\in S:C_j(s)\text{ satisfied for all hard }j\}.
\]

This form works without a metric.

### 2.2 Scalar residual

For metric or violation geometry:

\[
r:S\to\mathbb R_{\ge0}.
\]

Metric specialization:

\[
r(s)=d(s,A)=\inf_{a\in A}d(s,a).
\]

Candidate result:

\[
r(s)=0\iff s\in A
\]

under suitable assumptions such as nonempty closed `A` in a metric space.

### 2.3 Vector residual

If several constraint violations need to remain separate, introduce a distinct typed map

\[
\rho:S\to V
\]

into a real inner-product space `V`.

Do **not** silently replace scalar `r` by vector `rho`.

---

## 3. Tension / constraint energy

### 3.1 Scalar specialization

\[
\Phi(s)=\frac{k}{2}r(s)^2,
\qquad k\ge0.
\]

### 3.2 Vector specialization

For positive-semidefinite self-adjoint

\[
K:V\to V,
\]

define

\[
\Phi(s)=\frac12\langle\rho(s),K\rho(s)\rangle.
\]

Questions to resolve:

1. Is `Phi` merely a penalty functional or does a target application supply physical units?
2. Is `K` fixed, state-dependent, learned, or regime-dependent?
3. Does recovery minimize `Phi`, or only an ordered objective tuple that may differ from `Phi`?

A theorem relating recovery to decreasing `Phi` requires these choices to be compatible.

---

## 4. Deterministic lexicographic recovery

Given proposed state `x`, candidate set

\[
R_A(x)\subseteq A,
\]

and ordered objectives

\[
J_1(x,a),\ldots,J_k(x,a),
\]

select by lexicographic minimization, then apply a fixed total order only to break final ties.

Symbolically:

\[
\Pi^A_{\rm lex}(x)
=\operatorname{lexargmin}_{a\in R_A(x)}
\bigl(J_1(x,a),\ldots,J_k(x,a),\tau(a)\bigr).
\]

For finite nonempty candidate sets and a total tie-break order, existence and uniqueness should be a small theorem.

### Recovery event

\[
E=(s^-,s^+),
\qquad
s^+=\Pi^A_{\rm lex}(s^-).
\]

When subtraction is meaningful:

\[
\Delta=s^- - s^+.
\]

Otherwise retain the event pair or use a tangent/displacement object.

### Recovery shear idea

For a declared structural observable

\[
V:S\to Z,
\]

a recovery distortion can be measured by

\[
\kappa_R(s^-)
=D_Z\bigl(V(s^+),V(s^-)\bigr).
\]

Normalized variants are allowed only when the denominator is well-defined and nonzero.

---

## 5. Constrained evolution

Discrete specialization:

\[
G(s)=
\begin{cases}
F(s), & F(s)\in A,\\
\Pi^A_{\rm lex}(F(s)), & F(s)\notin A.
\end{cases}
\]

Thresholded specialization:

\[
G_{\Phi_c}(s)=
\begin{cases}
F(s), & \Phi(F(s))<\Phi_c,\\
\Pi^A_{\rm lex}(F(s)), & \Phi(F(s))\ge\Phi_c.
\end{cases}
\]

The threshold `Phi_c` is model-local unless independently justified as universal.

---

## 6. Fixed points, cycles, and stability

### 6.1 Admissible fixed point

\[
s^*\in A,
\qquad
G(s^*)=s^*.
\]

### 6.2 Proposed-dynamics fixed point

\[
F(s^*)=s^*.
\]

These are not equivalent in general.

### 6.3 Observer-consistent fixed point

Where a reconstruction map exists,

\[
\delta_M(s^*)
=d\bigl(s^*,R(O(s^*))\bigr)\le\varepsilon.
\]

A strong stability notion could require

\[
G(s^*)=s^*,
\qquad
s^*\in A,
\qquad
\delta_M(s^*)\le\varepsilon.
\]

### 6.4 Cycles matter

A system can lack fixed points and still possess periodic constrained dynamics:

\[
G^p(s)=s,
\qquad p>1.
\]

This is important when comparing asynchronous and synchronous finite dynamics. A monotone Lyapunov functional may rule cycles out under one update schedule but not another.

---

## 7. Information functionals must be explicit

The generic symbol `I` is a slot, not a universal quantity.

Candidate choices include:

### Shannon entropy

For finite distribution `p`:

\[
H(p)=-\sum_i p_i\log p_i.
\]

### Relative entropy

\[
D_{\rm KL}(p\|q)
=\sum_i p_i\log\frac{p_i}{q_i}.
\]

### Mutual information

\[
I(X;Y)=D_{\rm KL}(p_{XY}\|p_Xp_Y).
\]

### von Neumann entropy

\[
S(\rho)=-\operatorname{Tr}(\rho\log\rho).
\]

### Description length / coding proxy

\[
L(x;M)=L(M)+L(x\mid M)
\]

or another explicitly declared MDL/compression quantity.

These quantities should not be substituted for one another merely because each can be described informally as "information".

---

## 8. Information should be indexed by the observation contract

A stronger notation for representation-sensitive work is

\[
I_{O,\mu,\mathcal P}(s),
\]

where:

- `O` is the observation map;
- `mu` is a reference measure or distributional reference where required;
- `P` is a partition/alphabet/coarse-graining contract.

Then a sign claim is really about

\[
\operatorname{sgn}\left(\frac{d}{dt}I_{O,\mu,\mathcal P}(s_t)\right)
\]

or

\[
\operatorname{sgn}\left(\Delta I_{O,\mu,\mathcal P,n}\right).
\]

This forces a universal monotonicity claim to answer one of two questions:

1. Is the sign invariant over a declared class of admissible `O,mu,P`?
2. If one representation is privileged, what principle selects it?

---

## 9. Information-balance forms

### 9.1 Continuous time

For differentiable or absolutely continuous `I_t`:

\[
\frac{dI_t}{dt}
=P_I(t)-L_I(t)-B_I(t)+X_I(t).
\]

Interpretive placeholders:

\[
P_I=\text{production/source},
\]

\[
L_I=\text{internal loss/dissipation/coarse-graining term},
\]

\[
B_I=\text{net boundary flux term},
\]

\[
X_I=\text{constraint/recovery contribution}.
\]

These terms are not definitions until derived independently for a model.

### 9.2 Discrete time

\[
\Delta I_n
=I_{n+1}-I_n
=P_I[n]-L_I[n]-B_I[n]+X_I[n].
\]

### 9.3 Stochastic dynamics

One candidate expectation-level form is

\[
\frac{d}{dt}\mathbb E[I(X_t)]
=P_I(t)-L_I(t)-B_I(t)+X_I(t),
\]

when the derivative and expectation exchange are justified.

Alternative generator form:

\[
\frac{d}{dt}\mathbb E[f(X_t)]
=\mathbb E[(\mathcal L f)(X_t)]
\]

for a suitable Markov generator `L`.

Do not force stochastic dynamics into deterministic derivative notation.

---

## 10. Proposal versus recovery decomposition

For one discrete constrained step, define:

\[
s_n\xrightarrow{F}x_{n+1}
\xrightarrow{\Pi} s_{n+1}.
\]

Then

\[
\Delta I_{\rm proposal}
=I(x_{n+1})-I(s_n),
\]

\[
\Delta I_{\rm recovery}
=I(s_{n+1})-I(x_{n+1}),
\]

and exactly

\[
\Delta I_{\rm total}
=I(s_{n+1})-I(s_n)
=\Delta I_{\rm proposal}+\Delta I_{\rm recovery}.
\]

This is useful because a net decrease can hide a proposal increase followed by a larger recovery decrease, or vice versa.

---

## 11. Information directionality

### Candidate No-Universal-Sign Proposition

Without restrictions on dynamics, information functional, boundary conditions, observation, and representation, no universal sign for information change should be expected.

The cleanest proof strategy is constructive:

- System A with `Delta I > 0`;
- System B with `Delta I = 0`;
- System C with `Delta I < 0`;

all under a common declared broad class.

The proposition is only interesting if the class is stated fairly and the same information functional is used consistently.

### Restricted monotonicity template

If a balance law yields

\[
P_I=0,
\qquad
L_I\ge0,
\qquad
B_I\ge0,
\qquad
X_I\le0,
\]

then

\[
\frac{dI}{dt}\le0.
\]

This is mathematically trivial once the terms are defined. The scientific work is proving that the target model actually has those signs and that the chosen `I` matches the published claim.

A more principled route may use established contractivity/data-processing theorems rather than a hand-built balance decomposition.

---

## 12. Data processing and contractivity anchors

For a stochastic map/channel `K`, relative entropy often satisfies an established contraction inequality:

\[
D_{\rm KL}(pK\|qK)
\le
D_{\rm KL}(p\|q).
\]

Quantum analogue for a completely positive trace-preserving map `\Phi`:

\[
D(\Phi(\rho)\|\Phi(\sigma))
\le
D(\rho\|\sigma).
\]

UFT-ID should not claim novelty for these theorems. The useful role is to classify them as observation/transport/recovery specializations and expose the hypotheses under which monotonicity is legitimate.

---

## 13. Deterministic reversible and fine-grained examples

### 13.1 Finite permutation

If `F` permutes a finite probability vector without changing probabilities, Shannon entropy is invariant:

\[
H(p\circ F^{-1})=H(p).
\]

This is a clean zero-change family.

### 13.2 Hamiltonian / unitary fine-grained evolution

Fine-grained Gibbs entropy is conserved under appropriate Hamiltonian flow, and von Neumann entropy is conserved under unitary evolution.

These examples are useful as zero-change controls, while coarse-grained entropies may behave differently.

The paper should distinguish fine-grained conservation from observed/coarse-grained entropy growth.

---

## 14. Observer layer

### 14.1 Observation map

\[
O:S\to Y.
\]

If `O` is non-injective, distinct states may become observationally indistinguishable.

### 14.2 Reconstruction / mirror defect

\[
R:Y\to S,
\]

\[
\delta_M(s)
=d\bigl(s,R(O(s))\bigr).
\]

`delta_M` measures representation mismatch, not automatically destroyed information.

### 14.3 Linear dark subspace

When `S` and `Y` are linear spaces and `O` is linear:

\[
N_O=\ker O.
\]

States differing by elements of `N_O` are invisible to the observer:

\[
O(s)=O(s+n),
\qquad n\in N_O.
\]

A decomposition

\[
S=S_{\rm visible}\oplus N_O
\]

requires extra structure and should not be assumed automatically.

### 14.4 Accessible/inaccessible information

Avoid writing

\[
I_{\rm dark}=I_{\rm system}-I_{\rm observed}
\]

unless the information measure and decomposition actually justify subtraction.

Better: define observer-relative equivalence classes, sigma-algebras, conditional information, or kernel structure first.

---

## 15. Transport between regimes

Let

\[
T_{ab}:D_{ab}\to S_b,
\qquad
A_a\subseteq D_{ab}\subseteq S_a.
\]

### 15.1 Target residual

\[
r_T(s)=d_b(T_{ab}(s),A_b).
\]

### 15.2 Admissibility preservation

\[
T_{ab}(A_a)\subseteq A_b.
\]

This is a theorem target, not a default property.

### 15.3 Residual stability

Candidate Lipschitz-style bound:

\[
r_T(s)
\le L\,r_a(s)+\varepsilon.
\]

The domain must include points away from `A_a`; otherwise `r_a(s)=0` on the whole domain and the bound is vacuous.

### 15.4 Transport shear

Use structural maps distinct from constraints:

\[
V_a:D_{ab}\to Z,
\qquad
V_b:S_b\to Z.
\]

Then

\[
\kappa_T(s)
=D_Z\bigl(V_b(T_{ab}(s)),V_a(s)\bigr).
\]

If the natural codomains differ, introduce an explicit comparison map first.

---

## 16. Bridge obligations for cross-domain claims

A cross-domain map should be represented as a tuple such as

\[
\mathcal B_{ab}
=(X_a,X_b,T_{ab},V_a,V_b,L_{ab},M_{ab}),
\]

where:

- `X_a`: source objects;
- `X_b`: target objects;
- `T_ab`: mapping;
- `V_a,V_b`: structure being compared;
- `L_ab`: explicitly lost/non-preserved structure;
- `M_ab`: measurement/evidence contract.

A correspondence should not be promoted from structural analogy to shared physical mechanism without an additional bridge theorem or empirical result.

---

## 17. Information fidelity under transformation

This may be the broadest useful organizing concept.

For transformation

\[
T:S\to S'
\]

and structural maps

\[
V:S\to Z,
\qquad
V':S'\to Z,
\]

define

\[
\delta_V(T;s)
=D_Z\bigl(V'(T(s)),V(s)\bigr).
\]

Then:

\[
\delta_V=0
\]

means exact preservation of the declared structure, while

\[
\delta_V>0
\]

measures distortion relative to that structure.

This single pattern can instantiate:

- recovery shear;
- transport shear;
- observer/reconstruction defect;
- compression fidelity;
- sonification/projection fidelity;
- multi-scale invariant preservation.

Important: preservation is always **with respect to declared `V`**. A map can preserve one invariant while destroying another.

---

## 18. Compression and information loss are different questions

A deterministic compression map

\[
C:X\to Y
\]

may reduce representation size while preserving a chosen invariant:

\[
V_Y(C(x))=V_X(x).
\]

If decompression `D` exists with

\[
D(C(x))=x
\]

on the relevant domain, the representation is lossless even though description length may fall.

This is directly useful against any reasoning that conflates fewer symbols, fewer computational steps, or shorter encodings with a universal physical decrease of information.

---

## 19. Finite counterexample laboratories

### 19.1 Ternary control system

Use a finite `Z_3` state/control model with exhaustive state enumeration.

Measure on the same trajectory:

\[
V_G,
\quad H,
\quad D_{\rm KL},
\quad r,
\quad \Phi,
\quad \kappa_R.
\]

Target example:

\[
\Delta V_G<0
\quad\text{while}\quad
\Delta H>0.
\]

This would demonstrate that a monotone Lyapunov functional does not imply monotonicity of Shannon entropy.

### 19.2 Finite graph dynamics

Compare synchronous and asynchronous updates. Search for:

- fixed points;
- cycles;
- monotone potentials;
- entropy-sign disagreements.

### 19.3 Finite Markov chains

Build smallest chains exhibiting:

\[
\Delta H>0,
\qquad
\Delta H=0,
\qquad
\Delta H<0.
\]

Also track relative entropy to a stationary distribution, which may contract under stronger assumptions even when raw Shannon entropy does not obey the same sign law.

### 19.4 Constrained recovery model

Proposal `F` deliberately exits `A`; recovery returns to `A`. Measure proposal and recovery contributions separately.

### 19.5 QEC/invariant-compression model

Use deterministic receipt/invariant machinery to test whether:

\[
\text{representation size decreases}
\]

while

\[
\text{declared invariant defect}=0.
\]

---

## 20. Representation invariance tests

### 20.1 Bijective relabeling

For bijection `pi` on a finite alphabet, Shannon entropy should satisfy

\[
H(\pi_*p)=H(p).
\]

This is a sanity check.

### 20.2 Coarse-graining

For a many-to-one map `O`, the observed distribution changes. Entropy may move in a direction that depends on the grouping and distribution.

The point is not that coarse-graining always increases or decreases entropy. The point is that the observation contract is part of the theorem.

### 20.3 Reference-measure dependence

Relative entropy depends on its reference:

\[
D_{\rm KL}(p\|q).
\]

Changing `q` changes the quantity being measured.

### 20.4 Differential entropy warning

For continuous variables, differential entropy is coordinate dependent. Prefer relative entropy or explicitly reference-measure-aware formulations when coordinate robustness matters.

---

## 21. Calibration locality

A threshold or parameter calibrated in regime `a` should not automatically be treated as universal:

\[
\theta_a\not\Rightarrow\theta_b.
\]

For a transported threshold, require a map or recalibration rule:

\[
\theta_b=Q_{ab}(\theta_a;\text{calibration data}).
\]

This applies to:

- entropy thresholds;
- collapse/recovery thresholds;
- anomaly cutoffs;
- observer sensitivity;
- model-fit criteria.

---

## 22. Candidate Vopson embedding theorem

After exact reconstruction of the 2022 SLI definitions, define a class `C_V` of systems matching the actual published assumptions.

Target form:

\[
X\in\mathcal C_V
\implies
\Delta I_V(X)\le0
\]

or the appropriate continuous-time form.

Then ask whether

\[
\mathcal C_V
\subsetneq
\mathcal C_{\rm UFT-ID}.
\]

If yes, Vopson-style monotonicity is a restricted regime of a broader framework.

If no faithful class can be identified, abandon this framing rather than forcing it.

---

## 23. Candidate representation-robustness theorem

Let `G` be a group/class of admissible representation transformations. Seek conditions for

\[
\operatorname{sgn}(\Delta I_{g\cdot O,\,g\cdot\mu,\,g\cdot\mathcal P})
=
\operatorname{sgn}(\Delta I_{O,\mu,\mathcal P})
\]

for all `g in G`.

The theorem should be narrow. Bijective relabeling is a natural first case. Partition changes are not mere relabelings.

---

## 24. Candidate transport non-reification principle

Suppose a model map

\[
M:X\to Y
\]

has a property `P` in the model codomain. In general:

\[
P(M(X))\centernot\Rightarrow P(X).
\]

An additional bridge condition is required.

This is logically simple but useful as a guardrail against promoting properties of simulations, embeddings, lattices, qutrit models, or sonifications into properties of physical reality.

---

## 25. Vopson-specific mathematical audits

### 25.1 Mass-information equivalence

Questions:

- What quantity is held fixed when logical information changes?
- Is the predicted mass shift independent of ordinary stored energy?
- Does the formula introduce temperature dependence into a purported rest-mass property?
- Can matched-energy/different-information states distinguish the hypothesis from `E/c^2`?

### 25.2 Second Law of Infodynamics

For every example reconstruct:

\[
S,
\quad O,
\quad \mathcal P,
\quad p,
\quad I,
\quad \Delta I.
\]

Then sweep admissible representation choices and null models.

### 25.3 Genetics

Separate:

\[
\text{mutation},
\quad
\text{selection},
\quad
\text{drift},
\quad
\text{bottleneck},
\quad
\text{coding/window effect}.
\]

A trend in a genomic entropy statistic is not automatically a new dynamical law if ordinary evolutionary models generate the same trend.

### 25.4 Symmetry

Distinguish a static extremum:

\[
H(\text{maximally symmetric descriptor})
=\min H
\]

from a dynamical statement:

\[
\frac{dH}{dt}\le0.
\]

The first does not imply the second.

### 25.5 Gravity

Audit whether inverse-square structure is genuinely derived or imported through geometric counting.

Track dimensions through every step and identify whether a novel prediction survives after the Newtonian limit is reproduced.

---

## 26. Sonification and projection as a mathematical testbed

A sonification is an observation/projection map:

\[
O_{\rm audio}:S\to A_{\rm audio}.
\]

It may preserve selected structure but is not automatically a physical emission of the source system.

Use this as a controlled example of:

\[
\text{representation}\neq\text{referent}.
\]

A sonification homomorphism claim should state the preserved operation explicitly:

\[
O_{\rm audio}(x\star y)
=
O_{\rm audio}(x)\diamond O_{\rm audio}(y)
\]

if such operations genuinely exist. Otherwise call the relation a projection or diagnostic mapping rather than a homomorphism.

---

## 27. Multi-scale invariant preservation

For scale maps

\[
Q_{\ell\to m}:S_\ell\to S_m,
\]

seek declared invariants `V_l`, `V_m` satisfying

\[
V_m(Q_{\ell\to m}(s))=V_\ell(s)
\]

for exact preservation, or

\[
D_Z(V_m(Q_{\ell\to m}(s)),V_\ell(s))\le\varepsilon
\]

for approximate preservation.

This gives a mathematically cleaner notion of "information preserved across scale" than simply comparing representation sizes.

---

## 28. Lyapunov function versus entropy

A Lyapunov function `V` satisfies a system-specific monotonicity condition such as

\[
V(G(s))<V(s)
\]

outside the target set.

This does **not** imply

\[
H(G(s))<H(s).
\]

The two functionals may measure entirely different structures.

A minimal finite counterexample demonstrating

\[
\Delta V<0,
\qquad
\Delta H>0
\]

would be pedagogically powerful.

---

## 29. Candidate current/continuity formulation

A local information density/current picture is attractive but must be derived, not asserted.

Candidate continuity equation:

\[
\partial_t i+\nabla\cdot J_I=\sigma_I.
\]

Integrated over a region `Omega`:

\[
\frac{d}{dt}\int_\Omega i\,dV
=-\int_{\partial\Omega}J_I\cdot n\,dA
+\int_\Omega\sigma_I\,dV.
\]

This should only enter the formal core when `i`, `J_I`, and `sigma_I` are operationally defined for a concrete model.

A relativistic notation

\[
\nabla_\mu J_I^\mu=\sigma_I
\]

must not be mistaken for a Noether current unless a symmetry/action derivation actually supplies one.

---

## 30. Candidate field-theoretic specialization

If a future specialization earns a local field description, one may consider fields

\[
\psi(x),
\qquad
I[\psi],
\qquad
C_j[\psi],
\]

with an action or constrained variational problem.

But the current UFT-ID 3.0 core does not assume information is a fundamental spacetime field or that it contributes independently to stress-energy.

Earlier LQG/SU(3)/E8 constructions remain candidate specializations until bridge obligations are met.

---

## 31. Formal-proof staging order

Before Lean:

1. finite `S`;
2. decidable admissibility predicate;
3. finite nonempty candidate sets;
4. total tie-break order;
5. lexicographic recovery;
6. recovery admissibility;
7. finite residual;
8. scalar tension;
9. discrete constrained evolution;
10. explicit positive/zero/negative information-change examples;
11. restricted monotonicity theorem;
12. fixed-point/cycle lemmas.

Only after these survive should continuous/stochastic/measure-theoretic formalization be considered.

---

## 32. Notation register

| Symbol | Working meaning | Warning |
|---|---|---|
| `S` | total state space | no topology assumed by default |
| `A` | admissible subset | not necessarily a linear subspace |
| `C_j` | constraints | never reuse as invariant maps |
| `r` | scalar residual | `R_{>=0}` valued |
| `rho` | vector residual | distinct from scalar `r` |
| `Phi` | tension/penalty functional | not automatically physical energy |
| `Phi_c` | critical threshold | regime-local unless proven otherwise |
| `F` | proposed evolution | time model must be declared |
| `G` | constrained evolution | proposal plus possible recovery |
| `Pi_lex` | lexicographic recovery | needs candidate-set assumptions |
| `O` | observation/coarse-graining | may be non-injective |
| `R` | reconstruction | not necessarily inverse of `O` |
| `delta_M` | representation defect | observer-relative |
| `T_ab` | regime transport | ambient domain must be explicit |
| `V_a,V_b` | structural/invariant maps | distinct from constraints |
| `kappa_T` | transport shear | depends on declared comparison space |
| `I` | information functional | must name exact measure in theorem |
| `P_I` | production/source term | model-derived placeholder |
| `L_I` | loss/dissipation term | do not conflate with observation loss |
| `B_I` | boundary flux | sign convention must be declared |
| `X_I` | recovery/constraint contribution | may have either sign |

---

## 33. Source-lineage pointers for mathematical mining

These are research inputs, not automatic authorities for UFT-ID 3.0:

- UFT-ID 2.x / constraint-first Authorea lineage.
- ETQ-303 formal model and receiver-neutral projection machinery: `10.5281/zenodo.21494678`.
- SPECTRAL / inspectable sonification mappings: `10.5281/zenodo.21308248`.
- observation-dark / collective-mode work: `10.5281/zenodo.21292906`, `10.5281/zenodo.21293821`.
- deterministic redundancy / invariant work: `10.5281/zenodo.19099503`, `10.5281/zenodo.19102391`, `10.5281/zenodo.19104208`.
- multi-scale invariant receipts/compression: `10.5281/zenodo.20020910`, `10.5281/zenodo.20039913`.
- deterministic entropy/decay signatures: `10.5281/zenodo.20045771`.
- IRIS/invariant-driven reduction lineage: `10.5281/zenodo.19697908` / related record lineage.
- RES=RAG / transport-calibration methodology: `10.5281/zenodo.21917464`.
- QSOL-SUBSTRATE canonical-source/projection discipline: `10.5281/zenodo.21959180`.
- deterministic AI/reproducibility challenge packages such as `10.5281/zenodo.21925762` and `10.5281/zenodo.21935097` for provenance methodology.
- SAW-1 style explicit nonclaim/provenance packaging: `10.5281/zenodo.21984110`.

Every imported mathematical object must be retyped in the UFT-ID 3.0 notation and tagged with what was preserved, changed, or discarded.

---

## 34. Promotion checklist

An idea leaves `MATHS.md` only when:

- [ ] all symbols are typed;
- [ ] the domain/codomain is explicit;
- [ ] time model is explicit;
- [ ] information functional is explicit;
- [ ] regularity assumptions are explicit;
- [ ] the claim has exactly one canonical class;
- [ ] the closest established theorem has been checked;
- [ ] an adversarial companion question exists;
- [ ] at least one failure mode has been considered;
- [ ] cross-domain bridges list preserved **and lost** structure;
- [ ] physical interpretation is separated from abstract mathematics;
- [ ] the result has a destination in `DEFINITIONS.md`, `THEOREM_TARGETS.md`, experiments, or the paper.

The preferred outcome is not the most dramatic equation. It is the strongest equation that survives its assumptions being read aloud.
