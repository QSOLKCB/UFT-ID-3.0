import UFTID.Observation.Basic

namespace UFTID.Observation

universe u v

variable {S : Type u} {Y : Type v}

/-- The canonical map `[x] ↦ O(x)` from the observational quotient to the
set-theoretic image of `O`. -/
def quotientToImage (O : S → Y) :
    Quotient (observationalSetoid O) → Set.range O :=
  Quotient.lift (imagePoint O) (by
    intro a b hab
    apply Subtype.ext
    exact hab)

/-- **UFT-OBS-002 — Quotient-to-image correspondence.**

The observational quotient is canonically bijective with `Set.range O`. The
target is deliberately the image, not the full codomain unless `O` is
surjective.
-/
theorem uft_obs_002_quotient_to_image (O : S → Y) :
    Function.Bijective (quotientToImage O) := by
  constructor
  · intro q₁ q₂ h
    revert h
    refine Quotient.inductionOn₂ q₁ q₂ ?_
    intro a b h
    apply Quotient.sound
    exact congrArg Subtype.val h
  · rintro ⟨y, ⟨x, rfl⟩⟩
    exact ⟨Quotient.mk _ x, rfl⟩

end UFTID.Observation
