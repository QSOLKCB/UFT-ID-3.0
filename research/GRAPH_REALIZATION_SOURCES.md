# Graph Realization and Typed Incidence Source Map

**Claim class:** `DIAGNOSTIC`

This source map supports the graph-realization interlude that follows the merged relation-first recovery core. It imports mathematical structure and carefully bounded empirical examples. It does not import physical ontology.

```text
MATHEMATICAL_DONOR != PHYSICAL_PREMISE
EMPIRICAL_POSITIVE_CONTROL != UNIVERSAL_MECHANISM
PRIVATE_CORRESPONDENCE != PUBLIC_SOURCE_AUTHORITY
```

## 1. Darij Grinberg — graph-theory donor

Canonical source:

> Darij Grinberg, *An introduction to graph theory*, arXiv:2308.04512v3, Spring 2025 edition, version dated 8 June 2025. DOI `10.48550/arXiv.2308.04512`.

Source status: public arXiv course notes / mathematical preprint. The source is not treated as a peer-reviewed empirical paper.

Relevant mathematical locations in v3:

- pp. 11–14: graph drawings are representations of an abstract graph; the position of vertices and shapes of edge-curves may vary while the graph remains unchanged. The discussion of `K5` explicitly separates a planar-drawing/topology question from the underlying combinatorics.
- pp. 105–106: a simple digraph is a finite vertex set together with an arc subset of `V x V`.
- p. 108: indegree and outdegree.
- pp. 120–124: powers of the adjacency matrix count directed walks of fixed length.
- pp. 126–130: strong components and sink components; every nonempty finite multidigraph has a sink component.
- pp. 193–249: arborescences, spanning arborescences, Laplacians, and Matrix-Tree machinery.
- pp. 278–284: the weighted Matrix-Tree theorem.
- pp. 392–426: Menger-type path/cut theorems.
- pp. 93–94: an incidence-matrix exercise with `rank M = |V| - conn(G)` and the observation that the matrix represents the boundary operator `C1(G) -> C0(G)` when a graph is regarded as a CW-complex.

UFT-ID imports only the typed mathematics needed here:

```text
binary relation <-> directed adjacency
normal state <-> zero outdegree
reachability <-> directed walk/path existence
finite termination <-> directed acyclicity
strong component
sink strong component
condensation graph
adjacency-matrix cross-check
```

The later arborescence, Matrix-Tree, Menger, kernel, and chain-complex ideas remain roadmap targets rather than current physical claims.

## 2. Evers et al. — SiS2 positive structural control

Canonical source:

> Jürgen Evers, Peter Mayer, Leonhard Möckl, Gilbert Oehlinger, Ralf Köppe, and Hansgeorg Schnöckel, “Two High-Pressure Phases of SiS2 as Missing Links between the Extremes of Only Edge-Sharing and Only Corner-Sharing Tetrahedra,” *Inorganic Chemistry* **54**(4), 1240–1253 (2015). DOI `10.1021/ic501825r`.

Source status: peer-reviewed journal article.

The abstract reports:

- ambient-pressure NP-SiS2 contains chains of distorted **edge-sharing** SiS4 tetrahedra;
- HP3-SiS2 contains distorted **corner-sharing** SiS4 tetrahedra;
- the HP1 and HP2 phases contain both edge- and corner-sharing SiS4 tetrahedra.

The reusable UFT-ID lesson is deliberately narrower than the chemistry:

```text
SAME_LOCAL_COORDINATION_MOTIF != SAME_GLOBAL_CONNECTIVITY
MODULE_CONTENT != MODULE_INCIDENCE
LOCAL_STRUCTURE != GLOBAL_STRUCTURE
```

The SiS2 result is therefore a positive control for why a list of local modules is insufficient to determine a global network. It is not evidence for ETQ, E8, information physics, Fuller geometry, or a universal tetrahedral ontology.

## 3. K4 precision correction

A geometric tetrahedron has four corner vertices and six corner-to-corner edges. Its **1-skeleton** is therefore the complete graph `K4`.

That does **not** mean the chemical bond graph of an SiS4 coordination unit is `K4`.

If the chemical graph records only Si–S bonds, it has a central silicon site connected to four sulfur sites and is star-like (`K1,4` at that local bookkeeping level). A polyhedral-sharing graph is different again: its vertices may represent whole SiS4 tetrahedra and its typed links may record edge-sharing or corner-sharing.

UFT-ID therefore freezes:

```text
TETRAHEDRAL_1_SKELETON_K4 != SIS4_CHEMICAL_BOND_GRAPH
LOCAL_COORDINATION_GEOMETRY != CHEMICAL_BOND_GRAPH != POLYHEDRAL_SHARING_GRAPH
```

This is not pedantry. It prevents three legitimate but different graph constructions from being merged because they can all be drawn with tetrahedral-looking geometry.

## 4. ETQ and Fuller-like visualization boundary

The existing canonical registry records `XR-P17` and `XR-P18` already provide bounded ETQ/SPECTRAL compatibility and placement context.

The useful abstraction is to distinguish at least:

```text
A_alg   algebraic/module structure
G_c     coupling or transition graph
G_p     placement/incidence graph
rho     optional geometric drawing/embedding
P       separately justified physical interpretation, if any
```

A visual composition may make threefold modules, triangular scaffolds, tetrahedral motifs, or Fuller-like space-frame organization easy to see. That is a visualization/design fact, not a theorem that the underlying algebra is a tetrahedral material or that a Fuller construction is physically realized.

```text
ALGEBRA != GRAPH != EMBEDDING != PHYSICS
COUPLING_GRAPH != PLACEMENT_GRAPH
VISUAL_RESEMBLANCE != GRAPH_ISOMORPHISM
GRAPH_ISOMORPHISM != SEMANTIC_EQUIVALENCE
F3^3=I3 != GRAPH_THEORETIC_3_CYCLE
```

No decorative “sacred geometry” image is used as source authority in this repository.

## 5. Public provenance only

The historical observation that the SiS2 / tetrahedron / K4 idea had been discussed informally is not needed as scientific or mathematical authority. Private email, attachment identifiers, connector locators, and personal correspondence are intentionally excluded.

The public evidence chain is sufficient:

```text
Grinberg graph mathematics
+
Evers et al. SiS2 structural observation
+
existing public XR-P17 / XR-P18 context
->
bounded UFT-ID abstractions and adversarial fixtures
```

## 6. Future donor targets

The current PR freezes only what is needed to make graph realization and typed incidence explicit. Later work may investigate:

1. spanning arborescences as deterministic recovery skeletons;
2. arborescence counts and weighted Matrix-Tree quantities as combinatorial redundancy diagnostics;
3. Menger path/cut quantities as structural recovery robustness;
4. digraph kernels as absorbing-independent-set diagnostics;
5. incidence and boundary operators as a disciplined bridge from graph structure to chain-complex/homological structure;
6. SCC-level terminal classes for history/metastability work.

Every promotion must preserve:

```text
GRAPH_QUANTITY != PHYSICAL_OBSERVABLE
COMBINATORIAL_REDUNDANCY != EMPIRICAL_RELIABILITY
LAPLACIAN != PHYSICAL_HAMILTONIAN
CHAIN_COMPLEX != PHYSICAL_TOPOLOGY
```
