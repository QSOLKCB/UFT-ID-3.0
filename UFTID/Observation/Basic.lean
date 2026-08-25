import Mathlib

namespace UFTID.Observation

universe u v

variable {S : Type u} {Y : Type v}

/-- Deterministic observational equivalence induced by `O`. -/
def ObservationalRel (O : S → Y) (x x' : S) : Prop := O x = O x'

/-- The equivalence class of `x`, written as the source states observationally
indistinguishable from `x`. -/
def observationalClass (O : S → Y) (x : S) : Set S :=
  {x' | ObservationalRel O x' x}

/-- The set-theoretic fibre of an observation value. -/
def observationFiber (O : S → Y) (y : Y) : Set S :=
  O ⁻¹' ({y} : Set Y)

/-- Canonical point of the set-theoretic image `Set.range O`. -/
def imagePoint (O : S → Y) (x : S) : Set.range O :=
  ⟨O x, ⟨x, rfl⟩⟩

/-- **UFT-OBS-001 — Observational equivalence.**

For any total deterministic function `O : S → Y`, equality of observations is
an equivalence relation, and the class of a state is exactly the fibre over its
observed value.
-/
theorem uft_obs_001_observational_equivalence (O : S → Y) :
    Equivalence (ObservationalRel O) ∧
      ∀ x : S, observationalClass O x = observationFiber O (O x) := by
  constructor
  · exact ⟨fun x => rfl, fun _ _ h => h.symm, fun _ _ _ hxy hyz => hxy.trans hyz⟩
  · intro x
    ext x'
    simp [observationalClass, observationFiber, ObservationalRel]

/-- The setoid whose quotient is the observational quotient `S / ~_O`. -/
def observationalSetoid (O : S → Y) : Setoid S where
  r := ObservationalRel O
  iseqv := (uft_obs_001_observational_equivalence O).1

end UFTID.Observation
