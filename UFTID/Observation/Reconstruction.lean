import UFTID.Observation.Basic

namespace UFTID.Observation

universe u v

variable {S : Type u} {Y : Type v}

/-- **UFT-OBS-003 — Image-scoped exact reconstruction iff injective.**

A deterministic observation admits an exact left inverse on its image exactly
when it is injective.
-/
theorem uft_obs_003_image_reconstruction_iff_injective (O : S → Y) :
    Function.Injective O ↔
      ∃ R : Set.range O → S, ∀ x : S, R (imagePoint O x) = x := by
  constructor
  · intro hO
    classical
    let R : Set.range O → S := fun y => Classical.choose y.property
    refine ⟨R, ?_⟩
    intro x
    apply hO
    simpa [R, imagePoint] using Classical.choose_spec (imagePoint O x).property
  · rintro ⟨R, hR⟩
    intro x x' hOx
    calc
      x = R (imagePoint O x) := (hR x).symm
      _ = R (imagePoint O x') := by
        apply congrArg R
        apply Subtype.ext
        exact hOx
      _ = x' := hR x'

/-- **UFT-OBS-004 — Noninjective observation blocks global exact
reconstruction.**

If `O` is noninjective, no total map from the full codomain can be a global
exact left inverse. This does not rule out partial, representative,
probabilistic, or task-specific reconstruction.
-/
theorem uft_obs_004_noninjective_no_global_left_inverse
    (O : S → Y) (hO : ¬ Function.Injective O) :
    ¬ ∃ R : Y → S, ∀ x : S, R (O x) = x := by
  rintro ⟨R, hR⟩
  apply hO
  apply (uft_obs_003_image_reconstruction_iff_injective O).2
  refine ⟨(fun y => R y.1), ?_⟩
  intro x
  exact hR x

end UFTID.Observation
