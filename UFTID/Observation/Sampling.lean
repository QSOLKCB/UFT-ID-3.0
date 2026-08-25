import Mathlib

namespace UFTID.Observation

/-- The natural-number realization of the source formula
`f(i) = floor(i * L / R)` for positive `R`. -/
def uniformFloorNat (L R i : ℕ) : ℕ := i * L / R

lemma uniformFloorNat_lt
    {L R i : ℕ} (hL : 0 < L) (hR : 0 < R) (hi : i < R) :
    uniformFloorNat L R i < L := by
  unfold uniformFloorNat
  rw [Nat.div_lt_iff_lt_mul hR]
  simpa [Nat.mul_comm] using (Nat.mul_lt_mul_right hL).2 hi

/-- Uniform floor sampling as the finite map `Fin R → Fin L`. -/
def uniformFloorSample (L R : ℕ) (hL : 0 < L) (hR : 0 < R) : Fin R → Fin L :=
  fun i => ⟨uniformFloorNat L R i, uniformFloorNat_lt hL hR i.isLt⟩

/-- A sample has value `j` exactly on the half-open integer interval bounded by
the two adjacent ceiling divisions from the source proof. -/
lemma uniformFloorNat_eq_iff
    {L R : ℕ} (hL : 0 < L) (hR : 0 < R) (i j : ℕ) :
    uniformFloorNat L R i = j ↔
      (j * R) ⌈/⌉ L ≤ i ∧ i < ((j + 1) * R) ⌈/⌉ L := by
  have lower (k : ℕ) :
      (k * R) ⌈/⌉ L ≤ i ↔ k ≤ uniformFloorNat L R i := by
    calc
      (k * R) ⌈/⌉ L ≤ i ↔ k * R ≤ L * i := ceilDiv_le_iff_le_mul hL
      _ ↔ k * R ≤ i * L := by rw [Nat.mul_comm L i]
      _ ↔ k ≤ i * L / R := (Nat.le_div_iff_mul_le hR).symm
      _ ↔ k ≤ uniformFloorNat L R i := by rfl
  have upper :
      i < ((j + 1) * R) ⌈/⌉ L ↔ uniformFloorNat L R i < j + 1 := by
    simpa only [not_le] using not_congr (lower (j + 1))
  constructor
  · intro hij
    constructor
    · exact (lower j).2 (by omega)
    · exact upper.2 (by omega)
  · rintro ⟨hlo, hi⟩
    have hjle : j ≤ uniformFloorNat L R i := (lower j).1 hlo
    have hjlt : uniformFloorNat L R i < j + 1 := upper.1 hi
    omega

lemma uniformFloorUpperCeil_le
    {L R j : ℕ} (hL : 0 < L) (hj : j < L) :
    ((j + 1) * R) ⌈/⌉ L ≤ R := by
  rw [ceilDiv_le_iff_le_mul hL]
  exact Nat.mul_le_mul_right R (Nat.succ_le_iff.2 hj)

/-- The finite source indices mapping to output `j`. -/
def uniformFloorFiber (L R j : ℕ) : Finset ℕ :=
  (Finset.range R).filter fun i => uniformFloorNat L R i = j

lemma uniformFloorFiber_eq_Ico
    {L R j : ℕ} (hL : 0 < L) (hR : 0 < R) (hj : j < L) :
    uniformFloorFiber L R j =
      Finset.Ico ((j * R) ⌈/⌉ L) (((j + 1) * R) ⌈/⌉ L) := by
  classical
  ext i
  simp only [uniformFloorFiber, Finset.mem_filter, Finset.mem_range, Finset.mem_Ico]
  rw [uniformFloorNat_eq_iff hL hR i j]
  constructor
  · rintro ⟨_, hlo, hi⟩
    exact ⟨hlo, hi⟩
  · rintro ⟨hlo, hi⟩
    exact ⟨lt_of_lt_of_le hi (uniformFloorUpperCeil_le hL hj), hlo, hi⟩

/-- Exact source fibre cardinality from the canonical statement. -/
lemma uniformFloorFiber_card
    {L R j : ℕ} (hL : 0 < L) (hR : 0 < R) (hj : j < L) :
    (uniformFloorFiber L R j).card =
      (((j + 1) * R) ⌈/⌉ L) - ((j * R) ⌈/⌉ L) := by
  rw [uniformFloorFiber_eq_Ico hL hR hj, Nat.card_Ico]

lemma uniformFloorNat_strict_of_lt
    {L R i k : ℕ} (hR : 0 < R) (hRL : R < L) (hik : i < k) :
    uniformFloorNat L R i < uniformFloorNat L R k := by
  have hq : uniformFloorNat L R i * R ≤ i * L := by
    unfold uniformFloorNat
    exact Nat.div_mul_le_self _ _
  have hstep : (uniformFloorNat L R i + 1) * R ≤ k * L := by
    calc
      (uniformFloorNat L R i + 1) * R = uniformFloorNat L R i * R + R := by
        simp [Nat.add_mul]
      _ ≤ i * L + R := Nat.add_le_add_right hq R
      _ < i * L + L := Nat.add_lt_add_left hRL (i * L)
      _ = (i + 1) * L := by simp [Nat.add_mul]
      _ ≤ k * L := Nat.mul_le_mul_right L (Nat.succ_le_iff.2 hik)
  have hsucc : uniformFloorNat L R i + 1 ≤ uniformFloorNat L R k := by
    unfold uniformFloorNat
    exact (Nat.le_div_iff_mul_le hR).2 hstep
  omega

lemma uniformFloorSample_injective_of_lt
    {L R : ℕ} (hL : 0 < L) (hR : 0 < R) (hRL : R < L) :
    Function.Injective (uniformFloorSample L R hL hR) := by
  intro a b hab
  apply Fin.ext
  by_contra hne
  have hval := congrArg Fin.val hab
  change uniformFloorNat L R a.val = uniformFloorNat L R b.val at hval
  rcases lt_or_gt_of_ne hne with hablt | hbalt
  · exact (uniformFloorNat_strict_of_lt hR hRL hablt).ne hval
  · exact (uniformFloorNat_strict_of_lt hR hRL hbalt).ne hval.symm

lemma uniformFloorSample_not_surjective_of_lt
    {L R : ℕ} (hL : 0 < L) (hR : 0 < R) (hRL : R < L) :
    ¬ Function.Surjective (uniformFloorSample L R hL hR) := by
  intro hsurj
  have hcard := Fintype.card_le_of_surjective (uniformFloorSample L R hL hR) hsurj
  have : L ≤ R := by simpa using hcard
  exact (Nat.not_le_of_lt hRL) this

lemma uniformFloorSample_self (n : ℕ) (hn : 0 < n) :
    uniformFloorSample n n hn hn = id := by
  funext i
  apply Fin.ext
  change i.val * n / n = i.val
  exact Nat.mul_div_right i.val hn

lemma uniformFloorSample_surjective_of_lt
    {L R : ℕ} (hL : 0 < L) (hR : 0 < R) (hLR : L < R) :
    Function.Surjective (uniformFloorSample L R hL hR) := by
  intro y
  let a : ℕ := (y.val * R) ⌈/⌉ L
  have hupper : ((y.val + 1) * R) ⌈/⌉ L ≤ R :=
    uniformFloorUpperCeil_le hL y.isLt
  have hceil : L * a < y.val * R + L := by
    dsimp [a]
    rw [Nat.ceilDiv_eq_add_pred_div]
    calc
      L * ((y.val * R + L - 1) / L) = ((y.val * R + L - 1) / L) * L := by
        ac_rfl
      _ ≤ y.val * R + L - 1 := Nat.div_mul_le_self _ _
      _ < y.val * R + L := by omega
  have htarget : L * a < (y.val + 1) * R := by
    calc
      L * a < y.val * R + L := hceil
      _ < y.val * R + R := Nat.add_lt_add_left hLR (y.val * R)
      _ = (y.val + 1) * R := by simp [Nat.add_mul]
  have hstep : a < ((y.val + 1) * R) ⌈/⌉ L := by
    by_contra hnot
    have hle : ((y.val + 1) * R) ⌈/⌉ L ≤ a := Nat.le_of_not_gt hnot
    have hmul : (y.val + 1) * R ≤ L * a :=
      (ceilDiv_le_iff_le_mul hL).1 hle
    exact (Nat.not_le_of_lt htarget) hmul
  have haR : a < R := lt_of_lt_of_le hstep hupper
  let i : Fin R := ⟨a, haR⟩
  refine ⟨i, ?_⟩
  apply Fin.ext
  change uniformFloorNat L R a = y.val
  exact (uniformFloorNat_eq_iff hL hR a y.val).2 ⟨le_rfl, hstep⟩

lemma uniformFloorSample_not_injective_of_lt
    {L R : ℕ} (hL : 0 < L) (hR : 0 < R) (hLR : L < R) :
    ¬ Function.Injective (uniformFloorSample L R hL hR) := by
  intro hinj
  have hcard := Fintype.card_le_of_injective (uniformFloorSample L R hL hR) hinj
  have : R ≤ L := by simpa using hcard
  exact (Nat.not_le_of_lt hLR) this

/-- **UFT-OBS-005 — Uniform floor sampling.**

For positive `L` and `R`, the map `i ↦ floor(iL/R)` on `i = 0, …, R-1`
has the three source-size regimes from the canonical theorem and every output
fibre has the exact adjacent-ceiling cardinality. This is the arithmetic-focused
`LEAN-OBS-BATCH-002`; its separation preserves the v3.0.0 source freeze, where
UFT-OBS-005 was explicitly deferred from batch 001 rather than dropped.
-/
theorem uft_obs_005_uniform_floor_sampling
    (L R : ℕ) (hL : 0 < L) (hR : 0 < R) :
    (R < L →
      Function.Injective (uniformFloorSample L R hL hR) ∧
        ¬ Function.Surjective (uniformFloorSample L R hL hR)) ∧
    (R = L →
      (∀ i : Fin R, (uniformFloorSample L R hL hR i).val = i.val) ∧
        Function.Bijective (uniformFloorSample L R hL hR)) ∧
    (L < R →
      Function.Surjective (uniformFloorSample L R hL hR) ∧
        ¬ Function.Injective (uniformFloorSample L R hL hR)) ∧
    (∀ j : Fin L,
      (uniformFloorFiber L R j.val).card =
        (((j.val + 1) * R) ⌈/⌉ L) - ((j.val * R) ⌈/⌉ L)) := by
  constructor
  · intro hRL
    exact ⟨uniformFloorSample_injective_of_lt hL hR hRL,
      uniformFloorSample_not_surjective_of_lt hL hR hRL⟩
  constructor
  · intro hRL
    subst L
    have hid := uniformFloorSample_self R hR
    constructor
    · intro i
      have hi := congrArg (fun f : Fin R → Fin R => (f i).val) hid
      simpa using hi
    · rw [hid]
      exact Function.bijective_id
  constructor
  · intro hLR
    exact ⟨uniformFloorSample_surjective_of_lt hL hR hLR,
      uniformFloorSample_not_injective_of_lt hL hR hLR⟩
  · intro j
    exact uniformFloorFiber_card hL hR j.isLt

end UFTID.Observation
