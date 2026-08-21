# Graph Realization, Typed Incidence, and Structural Projection Calculus

**Authority:** canonical human mathematical surface for the graph-realization interlude following the merged relation-first recovery core.  
**Snapshot:** 2026-08-20.

This surface does not replace the relation calculus. It gives its finite labelled relation an exact graph representation and introduces the minimum extra typing needed to discuss modules, incidences, drawings, and lossy graph projections without turning visual resemblance into ontology.

```text
ALGEBRA != GRAPH != EMBEDDING != PHYSICS
GRAPH != DRAWING
```

## 1. Exact graph realization of `stepRel`

Let `X` be a finite labelled carrier and let

\[
\mathrm{stepRel}:X\to X\to\mathsf{Prop}.
\]

Define the simple directed graph

\[
G_{\mathrm{step}}=(X,A_{\mathrm{step}})
\]

by

\[
(x,y)\in A_{\mathrm{step}}
\iff
\mathrm{stepRel}(x,y).
\]

This construction changes representation, not semantics. The labelled carrier and every ordered one-step relation membership are preserved exactly.

### UFT-GR-001 Finite relation ↔ digraph identity

**Claim class:** `PROVED`

For finite labelled `X`, the map from `stepRel` to `G_step` defined above is exact at the one-step level.

**Proof.** This is immediate from the defining biconditional. For every ordered pair `(x,y)`, membership in the graph arc set is true exactly when `stepRel(x,y)` is true. Therefore the adjacency predicate and the relation predicate are extensionally identical.

```text
RELATION_REALIZATION == DIRECTED_ADJACENCY_PREDICATE
RELATION != DRAWING
```

## 2. Normality and outdegree

For a state `x`, the relation calculus defines

\[
\operatorname{Normal}_{\mathrm{stepRel}}(x)
\iff
\neg\exists y\in X:\mathrm{stepRel}(x,y).
\]

The outdegree of `x` in `G_step` is the number of arcs whose source is `x`.

### UFT-GR-002 Normality ↔ zero outdegree

**Claim class:** `PROVED`

\[
\operatorname{Normal}_{\mathrm{stepRel}}(x)
\iff
\deg^+_{G_{\mathrm{step}}}(x)=0.
\]

**Proof.** By UFT-GR-001, outgoing arcs from `x` are exactly the states `y` satisfying `stepRel(x,y)`. The set of such states is empty exactly when the outdegree is zero.

```text
ZERO_OUTDEGREE != ADMISSIBLE
ZERO_OUTDEGREE != FIXED_POINT
ZERO_OUTDEGREE != PHYSICAL_STABILITY
```

## 3. Reachability and matrix cross-checking

The reflexive-transitive closure of `stepRel` agrees with existence of a directed walk in `G_step`.

### UFT-GR-003 Reachability ↔ directed walk/path existence

**Claim class:** `PROVED`

For `x,y in X`,

\[
x\to^* y
\]

iff there is a directed walk from `x` to `y` in `G_step`. When `x != y`, repeated vertices may be removed from a finite walk to obtain a directed path.

**Proof.** A finite `stepRel` derivation is, by UFT-GR-001, exactly a finite sequence of directed arcs, hence a walk. Conversely every directed walk supplies a finite sequence of relation steps. Removing cycles from a finite walk preserves its endpoints and eventually yields a path.

For a labelled finite graph with adjacency matrix `C`, powers of `C` provide an independent computational witness: `(C^k)_{ij}` counts directed walks of length `k`.

The executable suite therefore computes reachability by both graph traversal and a separate Boolean transitive-closure implementation and requires exact agreement over all 530 labelled relations on `Fin1`, `Fin2`, and `Fin3`.

```text
TRAVERSAL_REACHABILITY == MATRIX_BOOLEAN_REACHABILITY
TWO_IMPLEMENTATIONS_AGREE != GENERAL_PROOF
```

## 4. Finite termination and directed cycles

### UFT-GR-004 Finite termination ↔ DAG acyclicity

**Claim class:** `PROVED`

On a finite carrier,

\[
\operatorname{Terminating}(\mathrm{stepRel})
\iff
G_{\mathrm{step}}\text{ has no directed cycle}.
\]

**Proof.**

If a directed cycle exists, following it repeatedly yields an infinite forward rewrite chain, so the relation is not terminating.

Conversely, if an infinite forward chain exists on a finite carrier, some vertex occurs at least twice by the pigeonhole principle. The segment between two occurrences supplies a directed cycle. Therefore absence of directed cycles excludes infinite forward chains.

```text
FINITE_DAG_CHECK == FINITE_TERMINATION_DECISION
FINITE_DAG_CHECK != GENERAL_WELL_FOUNDEDNESS_PROOF
```

## 5. Strong components and terminal classes

Define mutual reachability by

\[
x\sim_{\mathrm{SCC}}y
\iff
x\to^*y\land y\to^*x.
\]

Its equivalence classes are strongly connected components.

A strong component `C` is a **sink SCC** when every arc with source in `C` also has target in `C`.

### UFT-GR-005 Finite sink-SCC existence

**Claim class:** `PROVED`

Every nonempty finite directed graph has at least one sink SCC.

**Proof.** Collapse strongly connected components to component vertices. If every component had an outgoing edge to a distinct component, repeatedly following outgoing edges in the finite component graph would revisit a component and create a directed cycle of distinct SCCs. The SCCs on that cycle would then be mutually reachable and should have been one SCC, a contradiction. Therefore some component has no outgoing inter-component arc.

A sink SCC can contain a cycle and need not contain a normal vertex.

Example:

```text
a -> b
b -> a
```

If there are no outgoing arcs from `{a,b}`, then `{a,b}` is a sink SCC while neither `a` nor `b` is normal.

```text
NORMAL_VERTEX != SINK_SCC
SINK_SCC != FIXED_POINT != TERMINATION
```

This distinction supplies a future vocabulary for terminal behavioural classes without pretending every recurrent regime is a fixed point.

## 6. Condensation

Let `Cond(G)` have one vertex for each SCC and one arc `C -> D` whenever `C != D` and an original arc goes from some vertex of `C` to some vertex of `D`.

### UFT-GR-006 SCC condensation is acyclic

**Claim class:** `PROVED`

`Cond(G)` has no directed cycle.

**Proof.** If distinct SCCs formed a directed cycle in the condensation, every SCC on the cycle could reach every other SCC on the cycle. Their vertices would therefore be mutually reachable in the original graph, contradicting maximality of the SCC partition.

Thus a system may have internal cycling while its SCC quotient progresses acyclically:

```text
STATE_LEVEL_CYCLING != CLASS_LEVEL_PROGRESSION
MICROSTATE_TERMINATION != SCC_QUOTIENT_ACYCLICITY
```

## 7. Typed incidence

A list of modules does not yet define a network.

Define a typed incidence specification

```text
IncSpec = (M, L, I)
```

where:

- `M` is a set of labelled modules;
- `L` is a set of link/interface labels;
- `I subseteq M x L x M` is a typed incidence relation.

This allows the distinction between, for example, `edge-share`, `corner-share`, `couples-to`, or another declared interface relation.

An unlabelled graph projection may forget `L` and retain only whether two endpoints are adjacent.

```text
MODULE_INVENTORY != INCIDENCE
UNTYPED_ADJACENCY != TYPED_INCIDENCE
```

### CX-GR-002 Module inventory does not determine incidence

**Claim class:** `COUNTEREXAMPLE`

Take the same module set

```text
M = {a,b,c}.
```

One incidence relation forms a chain:

```text
a -- b -- c
```

while another forms a triangle:

```text
a -- b
 \  /
   c
```

The inventory is identical while the global connectivity differs.

Therefore:

```text
SAME_LOCAL_MODULES != SAME_GLOBAL_NETWORK
```

## 8. Rich-to-simple projections can lose structure

Consider a rich directed multigraph with labelled arc identities. Two parallel arcs

```text
u -alpha-> v
u -beta--> v
```

and a different object with only

```text
u -------> v
```

both project to the same simple endpoint relation `{(u,v)}` if multiplicity and arc identity are forgotten.

### CX-GR-001 Rich-to-simple projection loses arc identity

**Claim class:** `COUNTEREXAMPLE`

The projection from rich arc records to simple endpoint adjacency is non-injective in general.

```text
LOSSY_PROJECTION != STRUCTURAL_EQUIVALENCE
PROJECTION_EQUALITY != SOURCE_IDENTITY
```

This is a mathematical information-loss statement about a declared representation map. It is not a physical information-destruction claim.

## 9. Drawings and embeddings are separate objects

Let

\[
\rho:V(G)\to\mathbb R^d
\]

be an optional drawing/embedding map.

The coordinates are not part of the abstract graph unless the contract explicitly includes them.

### CX-GR-003 Multiple drawings, one graph

**Claim class:** `COUNTEREXAMPLE`

Take `K1,3` with one centre and three leaves. Place its four vertices at one set of coordinates, then at a different set, while preserving the same three centre-to-leaf edges. The drawings differ while the abstract labelled adjacency is unchanged.

```text
GRAPH != DRAWING
VISUAL_RESEMBLANCE != GRAPH_ISOMORPHISM
GRAPH_ISOMORPHISM != SEMANTIC_EQUIVALENCE
```

## 10. Tetrahedral graph precision

A geometric tetrahedron has four corner vertices and all six pairwise corner connections. Its 1-skeleton is therefore

\[
K_4.
\]

This is a statement about the **polyhedron's corner-edge graph**.

It is not a statement that every graph associated with a tetrahedral coordination unit is `K4`.

For an SiS4 local chemical bond graph that records only Si–S bonds, the central Si is connected to four S sites. At that bookkeeping level the local bond graph is star-like `K1,4`, not `K4`.

A third graph may treat each whole SiS4 tetrahedron as a module and label inter-tetrahedron relations by whether tetrahedra share an edge or a corner.

Freeze:

```text
TETRAHEDRAL_1_SKELETON_K4 != SIS4_CHEMICAL_BOND_GRAPH
LOCAL_COORDINATION_GEOMETRY != CHEMICAL_BOND_GRAPH != POLYHEDRAL_SHARING_GRAPH
```

This correction is essential to prevent a legitimate geometric analogy from becoming a false graph identity.

## 11. SiS2 positive structural control

The Evers et al. source reports SiS2 structures made from SiS4 tetrahedral coordination units whose **global sharing rules differ** across phases: edge-sharing chains, mixed edge/corner-sharing phases, and corner-sharing structure.

The UFT-ID abstraction is:

\[
\boxed{
\text{SAME LOCAL COORDINATION MOTIF}
\not\Rightarrow
\text{SAME GLOBAL CONNECTIVITY}.
}
\]

This supports typed-incidence discipline. It does not make SiS2 a model of UFT-ID, ETQ, E8, cognition, spacetime, or information.

```text
MATERIAL_POSITIVE_CONTROL != UFT_ID_PHYSICAL_PREMISE
```

## 12. ETQ / SPECTRAL visualization boundary

The existing `XR-P17` and `XR-P18` records supply public compatibility and placement context.

For visualization or future modelling, keep separate:

```text
A_alg   algebraic/module structure
G_c     coupling or transition graph
G_p     placement/incidence graph
rho     optional geometric drawing
P       any separately justified physical interpretation
```

A threefold algebraic identity such as

```text
F3^3=I3
```

does not automatically mean that the corresponding states form a graph-theoretic 3-cycle. A module count does not define coupling edges. A Fuller-like tetrahedral or space-frame drawing does not establish Fuller geometry as an algebraic or physical substrate.

```text
F3^3=I3 != GRAPH_THEORETIC_3_CYCLE
COUPLING_GRAPH != PLACEMENT_GRAPH
ALGEBRA != GRAPH != EMBEDDING != PHYSICS
```

The visual image that motivated this discussion is therefore an intuition aid only. Decorative or “sacred geometry” semantics are not imported.

## 13. Future recovery machinery unlocked by this layer

The full Grinberg source motivates several later candidates, deliberately deferred here:

### Spanning arborescences

For a target `r`, a rooted arborescence can extract one tree-like recovery skeleton from a richer relation.

```text
RELATION != ARBORESCENCE != SELECTOR
```

### Matrix-Tree redundancy

Let `tau(G,r)` count spanning arborescences rooted toward `r`.

Possible future diagnostic:

```text
tau(G,r)=0  -> no spanning recovery skeleton
tau(G,r)=1  -> one spanning recovery skeleton
tau(G,r)>1  -> multiple spanning recovery skeletons
```

But:

```text
ARBORESCENCE_COUNT != RECOVERY_PROBABILITY
COMBINATORIAL_REDUNDANCY != PHYSICAL_RELIABILITY
LAPLACIAN != PHYSICAL_HAMILTONIAN
```

### Menger robustness

Arc- or vertex-disjoint path counts can later define a structural robustness/bottleneck quantity.

```text
GRAPH_ROBUSTNESS != EMPIRICAL_FAILURE_RATE
MIN_CUT != PHYSICAL_FAILURE_PROBABILITY
```

### Graph-to-topology bridge

Incidence and boundary operators can provide a legitimate route from graphs toward chain complexes and homological invariants.

```text
DRAWING
!= GRAPH
!= CHAIN_COMPLEX
!= HOMOLOGY
!= PHYSICAL_TOPOLOGY
```

That bridge must be constructed explicitly. A topology-themed label or attractive drawing cannot substitute for it.

## 14. Finite conformance boundary

The executable suite reuses the same bounded universe as the relation core:

\[
2^{1^2}+2^{2^2}+2^{3^2}=530
\]

labelled binary relations.

For all 530 it independently checks:

- relation adjacency against the graph edge predicate;
- relation normality against zero outdegree;
- traversal reachability against Boolean matrix/transitive closure;
- the existing finite termination result against an independent DAG check;
- existence and validity of sink SCCs;
- acyclicity of the SCC condensation.

```text
FINITE_GRAPH_CONFORMANCE != GENERAL_PROOF
```

The mathematical arguments in this document, not the 530-case computation, are the authority for the general finite statements.
