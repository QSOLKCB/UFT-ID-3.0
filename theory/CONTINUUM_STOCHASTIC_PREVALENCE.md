# Continuum, Stochastic, and Prevalence Obligations

**Status:** canonical planned PR #17 formal surface.

**Claim boundary:** this layer defines and proves narrow obligations needed before finite relation/recovery evidence may be lifted into stochastic, infinite-horizon, prevalence, or continuum claims. It does not supply general stochastic-process or continuum theory.

```text
RELATION_REACHABLE != POSITIVE_PROBABILITY
EXISTS_PATH != POSITIVE_PROBABILITY
POSITIVE_PROBABILITY != ALMOST_SURE
FINITE_HORIZON_SUCCESS != INFINITE_PATH_LIVENESS
ONE_TRAJECTORY != DISTRIBUTION
FINITE_SAMPLE_FREQUENCY != MODEL_PROBABILITY
FINITE_COUNTEREXAMPLE != PREVALENCE_CLAIM
PREVALENCE_REQUIRES_DECLARED_MEASURE
FINITE_GRID_AGREEMENT != CONTINUUM_EQUALITY
DISCRETIZATION_CONVERGENCE != ASSUMED_WITHOUT_ERROR_CONTROL
FINITE_STOCHASTIC_CONFORMANCE != GENERAL_STOCHASTIC_OR_CONTINUUM_THEORY
```

## 1. Typed obligation layer

A bounded finite stochastic specialization uses

```text
FiniteMarkovSpec = (
  carrier,
  kernel,
  initial_distribution,
  scope
)
```

with a nonnegative row-stochastic kernel. A path/event claim additionally names a horizon and quantifier:

```text
PathEventSpec = (
  horizon,
  event,
  quantifier,
  scope
)
```

The following quantifiers are not synonyms:

```text
exists
positive_probability
almost_sure
finite_horizon
infinite_horizon
```

Prevalence is measure-relative:

```text
PrevalenceSpec = (
  population,
  measure,
  property,
  scope
)
```

A continuum lift must expose more structure than a finite grid:

```text
ContinuumLiftSpec = (
  discrete_domain,
  continuum_domain,
  bridge,
  property,
  topology,
  measure,
  regularity,
  convergence_mode,
  error_control,
  scope
)
```

A missing topology, measure, regularity hypothesis, convergence mode, or error-control statement is not silently supplied by a dense-looking numerical plot.

## 2. Finite stochastic results

## UFT-CSP-001 Finite stochastic kernels preserve total probability

**Claim class:** `PROVED`

**Canonical statement:** `For a finite carrier, a row-stochastic kernel K with nonnegative entries and unit row sums maps every probability distribution p to a probability distribution p' defined by p'(y)=sum_x p(x)K(x,y).`

**Canonical hypotheses:** `["X is finite", "p:X->Q_{>=0} has sum_x p(x)=1", "K:XxX->Q_{>=0}", "for every x, sum_y K(x,y)=1"]`

**Canonical nonclaims:** `["Finite row-stochastic mass preservation does not establish stationarity, ergodicity, continuum dynamics, empirical calibration, or physical randomness."]`

Proof: every term in `p'(y)` is nonnegative, and

```text
sum_y p'(y)
= sum_y sum_x p(x) K(x,y)
= sum_x p(x) sum_y K(x,y)
= sum_x p(x)
= 1.
```

The finite executable control uses exact rational arithmetic rather than floating tolerance.

## UFT-CSP-002 Finite atomic stochastic quantifiers are not interchangeable

**Claim class:** `PROVED`

**Canonical statement:** `For a finite probability distribution p and event E, p(E)=1 implies p(E)>0, and p(E)>0 holds exactly when E intersects the positive-mass support of p; the converses from positive probability or support existence to almost-sure truth do not hold in general.`

**Canonical hypotheses:** `["X is finite", "p:X->Q_{>=0} has total mass one", "E is a subset of X"]`

**Canonical nonclaims:** `["This finite atomic statement is not a substitute for general measure-theoretic support, almost-everywhere, or infinite-path semantics."]`

For finite `X`,

```text
p(E) = sum_{x in E} p(x).
```

The sum is positive exactly when at least one event point has positive mass. `p(E)=1` is strictly stronger than positivity unless the event already captures all probability mass.

## UFT-CSP-003 Finite-horizon path mass is the product of declared stochastic factors

**Claim class:** `PROVED`

**Canonical statement:** `For a finite Markov specification with initial distribution p and row-stochastic kernel K, the probability of a finite path (x0,...,xh) is p(x0) times the product of K(xt,xt+1), and the masses of all length-h paths sum exactly to one.`

**Canonical hypotheses:** `["X is finite", "p is a probability distribution on X", "K is a row-stochastic kernel on X", "h is a finite natural-number horizon"]`

**Canonical nonclaims:** `["A finite-horizon path formula does not by itself define an infinite path-space measure or prove infinite-horizon liveness."]`

Repeated expansion of the finite sums gives

```text
Pr[x_0,...,x_h]
= p(x_0) product_{t=0}^{h-1} K(x_t,x_{t+1}).
```

Summing over every path telescopes through the unit row sums and returns total mass one.

## UFT-CSP-004 Prevalence is indexed by a declared measure

**Claim class:** `PROVED`

**Canonical statement:** `For a declared probability measure mu on a finite population X and failure property F subseteq X, prevalence is mu(F); therefore the same failure set can have different prevalence under different declared measures, and existence of a counterexample alone does not determine prevalence.`

**Canonical hypotheses:** `["X is finite", "mu is a probability measure on X", "F is a subset of X"]`

**Canonical nonclaims:** `["A formal finite prevalence value is not an empirical population estimate, confidence interval, causal rate, or universal frequency."]`

The point is not merely terminological. If `x in F`, then existence is fixed while `mu(F)` can vary with `mu`. A universal statement is killed by one valid counterexample; a prevalence statement needs an independently declared measure or sampling model.

## UFT-CSP-005 Finite-grid agreement does not determine continuum equality

**Claim class:** `PROVED`

**Canonical statement:** `For every finite set G of real grid points, the zero function and the nonzero polynomial q(x)=product_{a in G}(x-a) agree at every point of G while differing at every real point b not in G; finite-grid equality therefore does not imply continuum equality without additional assumptions.`

**Canonical hypotheses:** `["G is a finite set of real numbers", "b is a real number not in G"]`

**Canonical nonclaims:** `["The theorem does not deny convergence when a discretization is accompanied by sufficient regularity, topology, approximation, and error-control hypotheses."]`

For every `a in G`, the factor `(a-a)` makes `q(a)=0`. For `b not in G`, every factor `(b-a)` is nonzero, so `q(b)` is nonzero. The result is deliberately elementary because the obligation it enforces is foundational:

```text
FINITE_GRID_AGREEMENT
!=
CONTINUUM_EQUALITY.
```

## 3. Adversarial counterexamples

### CX-CSP-001 Relation reachability can have zero stochastic probability

**Claim class:** `COUNTEREXAMPLE`

**Canonical statement:** `A base relation may contain the edge 0->1 while a stochastic kernel assigns K(0,1)=0, so relation reachability alone does not imply positive stochastic path probability.`

**Canonical nonclaims:** `["The counterexample does not make the relation edge invalid; it separates relational possibility from the declared stochastic support."]`

A relation can record admissible possibility while a stochastic specialization assigns zero mass to that edge. These are different objects.

### CX-CSP-002 Positive probability is not almost-sure truth

**Claim class:** `COUNTEREXAMPLE`

**Canonical statement:** `Under a fair two-outcome distribution, the event {H} has probability 1/2, which is positive but not one.`

**Canonical nonclaims:** `["The example concerns quantifier strength only and does not imply that positive-probability events are empirically common."]`

This is the minimal quantifier separator:

```text
Pr(H)>0
but
Pr(H)!=1.
```

### CX-CSP-003 Finite-horizon survival can coexist with zero infinite-survival probability

**Claim class:** `COUNTEREXAMPLE`

**Canonical statement:** `If independent survival at each step has probability q=1/2, then survival through every finite horizon n has positive probability 2^{-n}, while the probability of surviving forever is lim_{n->infinity}2^{-n}=0.`

**Canonical nonclaims:** `["The fixture does not claim that every infinite stochastic process has this limit or that finite-horizon evidence is useless."]`

For every finite `n`, `2^{-n}>0`; nevertheless the decreasing sequence tends to zero. Therefore no finite collection of positive finite-horizon survival statements is an infinite-liveness theorem.

### CX-CSP-004 One trajectory frequency is not the model probability

**Claim class:** `COUNTEREXAMPLE`

**Canonical statement:** `The length-three trajectory HHH has empirical head frequency 1 under a fair coin model whose declared single-step head probability is 1/2; one observed path therefore does not identify the generating distribution.`

**Canonical nonclaims:** `["The example does not deny statistical consistency under independently justified sampling assumptions and asymptotic theorems."]`

The trajectory probability is `1/8`, while the within-trajectory empirical frequency happens to be one. A statistic from one path is not the distribution parameter by definition.

### CX-CSP-005 One finite counterexample does not determine prevalence

**Claim class:** `COUNTEREXAMPLE`

**Canonical statement:** `On the same two-point carrier with the same failure set {x}, one probability measure can assign failure prevalence 1/100 while another assigns 99/100, so existence of x does not determine how prevalent failure is.`

**Canonical nonclaims:** `["The construction is a formal measure-dependence control, not an empirical estimate of any real population."]`

The failing point and property are held fixed. Only the measure changes.

### CX-CSP-006 Perfect finite-grid agreement can fail between grid points

**Claim class:** `COUNTEREXAMPLE`

**Canonical statement:** `The functions f(x)=0 and g(x)=x(x-1/2)(x-1) agree on the grid {0,1/2,1} but differ at x=1/4, so perfect grid conformance does not license continuum equality.`

**Canonical nonclaims:** `["The example does not refute a separately proved convergence theorem with explicit regularity and error bounds."]`

At the three grid points, `g=0`. At `x=1/4`,

```text
g(1/4) = (1/4)(-1/4)(-3/4) = 3/64 != 0.
```

## 4. Obligation matrix

Before a claim is promoted beyond the bounded finite model, it must answer the relevant questions.

| Promotion | Minimum missing obligations |
| --- | --- |
| relation -> stochastic | kernel/support identity, probability law, initial distribution, scope |
| finite horizon -> infinite horizon | infinite path-space/event semantics, limiting theorem or measure construction, liveness quantifier |
| one/few trajectories -> model probability | sampling design, independence/dependence assumptions, estimator, uncertainty, calibration |
| counterexample -> prevalence | population, measure/sampling model, property definition, denominator/scope |
| finite grid -> continuum | continuum domain, bridge/discretization, topology, regularity, convergence mode, error control |

These obligations are intentionally fail-closed. If the extra structure is not supplied, the strongest licensed statement remains the bounded one.

## 5. Exact finite conformance boundary

The reference witness checks:

```text
9 two-state exact rational kernels
3 exact initial distributions
27 one-step probability-mass preservation checks
756 finite-path mass evaluations through horizon 3
81 finite-path normalization checks
48 finite-atomic event/quantifier checks
18 almost-sure event cases
30 positive-probability event cases
30 support-witness event cases
16 positive finite-survival controls
80 exact prevalence measure/event evaluations
31 finite-grid non-lifting polynomial controls
```

All arithmetic is exact `Fraction` arithmetic. This is bounded conformance evidence only.

```text
FINITE_STOCHASTIC_CONFORMANCE
!=
GENERAL_STOCHASTIC_OR_CONTINUUM_THEORY
```

## 6. Explicit deferrals

This phase does not claim general measurable-space construction, continuous-time generators, martingale results, stopping-time theory, ergodicity, mixing, stationary measures, continuum existence or regularity, asymptotic concentration, statistical inference, or empirical prevalence. Those require their own hypotheses and evidence.
