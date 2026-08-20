# Definition and Model Obligations

**Status:** PR #8 canonical well-definedness firewall.  
**Claim class:** `DEFINITION`.

A theorem may be syntactically beautiful and still fail before proof because one of its objects was never mathematically specified.

The governing rule is:

```text
NAMED_OBJECT != WELL_DEFINED_MATHEMATICAL_OBJECT
```

This surface combines two complementary audit patterns:

1. the TAS discipline of refusing to infer an eigenproblem from a name and giving any useful proxy a separate identity; and
2. the author-supplied independent stress-test pattern of comparing advertised mathematical/computational structure with what an implementation actually realizes.

## Minimum definition obligations

The machine authority is `machine/definition_obligations.json`.

Highlights:

### State

Before using a state in a theorem, declare the carrier/type and equality/identity relation. Metric, topology, probability, algebra and physical ontology remain absent unless actually used.

### Operator

Declare domain, codomain and action.

Linearity, boundedness and self-adjointness are conditional claims, not properties inherited from the letter `L`, `H` or `A`.

### Eigenmode

A named eigenmode requires at least:

- carrier/function space;
- operator or operator pair;
- eigen-equation;
- domain;
- boundary conditions;
- regularity where required.

A source label such as `L39` is not enough.

If UFT-ID defines a comparison proxy, then:

```text
SOURCE_OBJECT = unresolved/undefined as sourced
PROXY_OBJECT  = separately named and fully specified
```

The proxy must not be back-written into the source.

### Entropy

Declare at minimum:

- entropy family;
- state/distribution measured;
- log-base/convention;
- normalization/reference;
- observer/partition when relevant;
- scope.

### Derivative

Declare the independent variable/time model and differentiability notion.

```text
DISCRETE_UPDATE != CONTINUOUS_DERIVATIVE
```

### Continuum model

A PDE/field-style model must additionally identify:

- carrier/domain;
- state type;
- regularity class;
- governing operator/equations;
- boundary conditions;
- initial conditions or explicit non-applicability;
- metric/measure actually used;
- singularity treatment;
- regularization policy;
- existence status;
- uniqueness status;
- approximation regime.

This requirement was strengthened by the uploaded Vortex-membrane peer-review material, which explicitly separates distributional/singular objects, regularization, function spaces and weak well-posedness obligations. UFT-ID imports that specification discipline only, not the paper's physical model.

## Claim-realization obligations

The second half of the machine registry audits statements about implementation.

### `MODEL-OBL-REVERSIBLE` — Reversible / invertible

A reversible-map claim requires:

- domain;
- codomain;
- inverse construction or bijectivity evidence;
- round-trip properties appropriate to the scope.

A function name, class name or prose assertion is not evidence of invertibility.

### `n`-dimensional implementation

A dimensionality claim requires an actual represented carrier of dimension `n` and operations/tests that act on that carrier.

Decorative metadata such as `dimension: 24` is not a 24-dimensional implementation.

### Dynamics

An implemented dynamics claim requires:

- state;
- time/index model;
- evolution/update law;
- at least one nontrivial trajectory/execution witness.

### Scientific simulation

A simulation claim requires:

- governing model/equations;
- initial/boundary conditions where applicable;
- numerical/analytic method;
- observables;
- validation/comparison target;
- limitations.

```text
SOFTWARE_SCAFFOLD != VALIDATED_SCIENTIFIC_SIMULATION
```

## Fail-closed use

A missing obligation does not prove the source claim false.

It means the stronger claim is **not yet entitled** on the declared evidence surface.
