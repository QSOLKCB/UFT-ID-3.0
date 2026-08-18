# Research Gaps and Decisive Tests

This document answers the practical question: **what is still missing before UFT-ID 3.0 can make a serious, publication-grade challenge to universal infodynamics?**

## Priority 1: freeze the object called information

The largest conceptual danger is switching between inequivalent notions of information while keeping the same word.

Before any headline theorem, the paper needs a comparison table and formal domain for:

- Shannon entropy of a declared distribution;
- entropy rate of a stochastic process;
- Kullback-Leibler divergence;
- mutual information;
- von Neumann entropy;
- observational/coarse-grained entropy;
- thermodynamic entropy;
- algorithmic information or practical compression estimators.

**Decisive deliverable:** every theorem and experiment names exactly one quantity and its state representation. No argument is allowed to change quantities mid-derivation.

## Priority 2: derive, do not assume, the balance law

The proposed UFT-ID information-balance equation is presently a template. It needs derivations for concrete classes of systems.

Candidate classes:

- finite deterministic maps;
- finite Markov chains;
- continuous-time Markov processes;
- open stochastic systems;
- reversible/unitary systems;
- coarse-grained observation channels;
- UFT-ID thresholded recovery systems.

**Decisive deliverable:** at least one mathematically exact balance identity and a clearly stated map from its terms to observable quantities.

## Priority 3: settle the monotonicity question with the smallest possible counterexamples

A universal law can be defeated by one valid counterexample, but only if the example satisfies the law's declared domain.

Build minimal examples for:

```text
Delta I > 0
Delta I = 0
Delta I < 0
```

under identical notation and clearly varied assumptions.

**Decisive deliverable:** a theorem identifying sufficient monotonicity conditions plus a counterexample demonstrating why weaker conditions are insufficient.

## Priority 4: representation and coarse-graining invariance

A physical law should not depend accidentally on arbitrary labels. At the same time, entropy genuinely can change when the observable partition changes.

We therefore need to distinguish:

- bijective relabeling;
- lossless recoding;
- change of alphabet;
- change of partition;
- many-to-one coarse-graining;
- change of reference measure;
- change of system boundary.

**Decisive deliverable:** an invariance ladder stating which transformations must preserve each result and explicit examples where non-invertible transformations change it.

## Priority 5: independent reproduction of the 2022 SLI examples

Do not rely on summaries. Reproduce the published digital-storage and genomic calculations from source equations and data.

**Decisive deliverable:** a containerized or dependency-locked reproduction producing the published numerical results, followed by a parameter/encoding sweep that was not selected after seeing the outcome.

## Priority 6: genomic causal separation

Observed sequence entropy is affected by mutation, selection, population bottlenecks, sequencing/sampling, reference choice, and composition. A directional entropy trend is not automatically a mutation-generating law.

**Decisive deliverable:** a phylogenetically informed model comparing an infodynamic predictor with standard evolutionary/null models on held-out lineages.

## Priority 7: the mass-information experiment must isolate logical information

The strongest test of an information-specific mass claim is not simply measuring a tiny energy difference. It is changing logical information while controlling every conventional stored-energy channel.

**Decisive deliverable:** an experimental design with two physical states matched as closely as possible in ordinary energy but differing in the claimed logical information quantity, plus a predicted invariant mass difference.

If no such invariant can be defined, that itself is a major theoretical result.

## Priority 8: audit the gravity derivation for hidden geometry

A derivation of the inverse-square law is only informative if the inverse-square structure is not already encoded through area scaling, radial cell counting, or equivalent assumptions.

**Decisive deliverable:** a dependency graph showing exactly which premises generate each power of distance, followed by a prediction outside the derivation's calibration case.

A theory that only reproduces Newton after using Newton-equivalent geometry is a reinterpretation, not an independent derivation.

## Priority 9: static symmetry versus dynamical law

The 2026 polygon result may be mathematically correct while still not establishing temporal infodynamics.

**Decisive deliverable:** separate propositions:

```text
P1: a chosen entropy functional is minimized at a symmetric configuration.
P2: a physical system evolves toward that configuration because of an infodynamic law.
```

Prove or test them separately.

## Priority 10: language entropy versus ordinary diversity dynamics

If a dominant language grows while minority categories disappear, Shannon diversity often declines by construction. The scientific question is whether an infodynamic principle predicts anything beyond that ordinary population trajectory.

**Decisive deliverable:** out-of-sample comparison between the infodynamic model and established population/diversity models, scored before seeing the test data.

## Priority 11: formal epistemic bridge to physical claims

UFT-ID's mathematics can be perfectly valid while a proposed physical interpretation is false.

For every physical application, require:

```text
abstract object
-> measurement procedure
-> physical quantity
-> units
-> prediction
-> uncertainty
-> falsifier
```

**Decisive deliverable:** no physical claim without a complete bridge chain.

## Priority 12: adversarial literature review

We need primary-source comparison against mature results that already govern information monotonicity and thermodynamics.

The minimum literature surface includes:

- data-processing inequalities;
- H-theorems and Markov semigroups;
- stochastic thermodynamics and entropy production;
- Landauer principle;
- fluctuation theorems;
- quantum channels and relative-entropy contraction;
- observational/coarse-grained entropy;
- resource theories;
- information geometry;
- transfer entropy and directed information;
- algorithmic information theory;
- entropic-gravity literature and critiques.

**Decisive deliverable:** a novelty matrix showing what UFT-ID adds beyond each established theorem family.

## Priority 13: preregister the attack surface

A cross-domain project creates enormous researcher degrees of freedom. That is exactly where accidental cherry-picking breeds.

Before the main empirical campaign, freeze:

- primary entropy measure;
- preprocessing choices;
- inclusion/exclusion criteria;
- primary counterexample class;
- significance or model-comparison criterion;
- representation-sensitivity protocol;
- stopping rule.

**Decisive deliverable:** timestamped preregistration or immutable protocol release.

## Priority 14: independent hostile review

Before publication, ask reviewers to attack UFT-ID using the same diagnostic map it applies to others.

Specific questions:

- Did we transport a theorem outside its assumptions?
- Did we reify an abstraction?
- Did we select a partition because it produced the desired sign?
- Did we confuse information loss with inaccessibility?
- Did we use a cross-domain analogy as causal evidence?
- Did we overstate what a counterexample disproves?

**Decisive deliverable:** a published response matrix with accepted, rejected, and unresolved objections.

## Priority 15: Lean, only after the freeze

Lean should eventually formalize the smallest theorem surface that matters most. It should not be used as decorative rigor.

**Entry condition:** canonical definitions and theorem statements have survived the reproduction and adversarial phases without material notation changes.

**First formal target:** finite deterministic lexicographic recovery plus the restricted monotonicity/counterexample core.

## Publication victory condition

The strongest possible paper does not need to conclude "Vopson is wrong."

A stronger scientific outcome would be:

> The direction of a declared information functional is derived from dynamics, boundaries, observation, and representation. Monotonic decrease is proved for a restricted class, while explicit counterexamples delimit any broader universal claim.

That result remains valuable even where particular infodynamic examples reproduce successfully.
