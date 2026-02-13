"""
Dimension-to-Slider Mapping for Cap/Ops Balance Simulation.

Two-layer model:

Layer 1 — STRUCTURAL BASELINE (derivable from dimensions alone):
    S_i = clamp(b_i + sum_j(w_ij * T_ij(D_j)), 0, 1)

    Where:
        D_j   = dimension j value (1-5 integer)
        T_ij  = piecewise transform mapping D_j -> [0, 1] for slider i
        w_ij  = weight of dimension j on slider i
        b_i   = bias term for slider i

    This layer captures ~80% of slider variation for structurally stable
    projects. It fails for temporal, crisis, and transitional states where
    slider values encode history rather than current project characteristics.

Layer 2 — STATE MODIFIERS (require additional context beyond dimensions):
    S_i_final = clamp(S_i_structural + sum_k(modifier_k), 0, 1)

    Four modifier categories:
        - project_phase:     Planning inflates Time, late execution compresses it
        - crisis_level:      Degrades Investment/Recovery, amplifies Overwork
        - delivery_culture:  DevOps culture boosts Recovery beyond dimensions
        - resource_erosion:  Legacy/declining projects lose Investment capacity

    State modifiers are domain-derived (not optimised) and applied additively.
    They represent information that the 8 dimensions structurally cannot encode:
    where the project HAS BEEN, not just what it IS.

Calibrated against 12 validated MIRA personas mapped to 15 structural
archetypes with known slider profiles.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
try:
    from scipy.optimize import minimize
except ImportError:
    minimize = None  # Only needed for calibrate(), not runtime


# ---------------------------------------------------------------------------
# Dimension definitions
# ---------------------------------------------------------------------------

DIMENSION_NAMES = [
    "D1: Consequence of Failure",
    "D2: Market Pressure",
    "D3: System Complexity",
    "D4: Regulatory Burden",
    "D5: Team Stability",
    "D6: Outsourcing Dependency",
    "D7: Product Lifecycle Stage",
    "D8: Organisational Coherence",
]

DIMENSION_SHORT = ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8"]

SLIDER_NAMES = [
    "Investment Capacity",
    "Recovery Capacity",
    "Overwork Capacity",
    "Time Capacity",
]

SLIDER_SHORT = ["Investment", "Recovery", "Overwork", "Time"]

# Categorical label thresholds for display
CATEGORICAL_BANDS = [
    (0.00, 0.15, "Very Low"),
    (0.15, 0.30, "Low"),
    (0.30, 0.40, "Low-Med"),
    (0.40, 0.55, "Medium"),
    (0.55, 0.70, "Med-High"),
    (0.70, 0.85, "High"),
    (0.85, 1.01, "Very High"),
]


def to_categorical(value: float) -> str:
    """Convert a continuous slider value [0,1] to a categorical label."""
    for low, high, label in CATEGORICAL_BANDS:
        if low <= value < high:
            return label
    return "Very High"


# ---------------------------------------------------------------------------
# Calibration data: 12 MIRA personas
# ---------------------------------------------------------------------------

# Each persona: (name, archetype_name, dimensions[8], target_sliders[4])
# Dimensions are D1-D8 on 1-5 scale
# Target sliders are [Investment, Recovery, Overwork, Time] on [0,1]
# Target values derived from archetype default slider profiles

CALIBRATION_DATA = [
    ("P1 Startup Chaos",        "#1 Micro Startup",       [2, 5, 1, 1, 1, 1, 1, 5], [0.10, 0.10, 0.80, 0.10]),
    ("P2 Small Agile Team",     "#2 Small Agile",         [2, 4, 2, 1, 2, 1, 2, 4], [0.25, 0.25, 0.65, 0.25]),
    ("P3 Govt Waterfall",       "#8 Reg Stage-Gate",      [3, 1, 4, 4, 4, 4, 3, 3], [0.80, 0.65, 0.25, 0.80]),
    ("P4 Enterprise Financial", "#9 Ent Balanced",        [4, 2, 4, 5, 4, 3, 3, 3], [0.80, 0.80, 0.25, 0.65]),
    ("P5 Medical Device",       "#8 Reg Stage-Gate",      [5, 1, 3, 5, 5, 2, 3, 4], [0.80, 0.65, 0.25, 0.80]),
    ("P6 Failing Automation",   "#3 Scaling Startup",     [2, 3, 2, 1, 3, 1, 2, 2], [0.50, 0.35, 0.50, 0.35]),
    ("P7 Greenfield Cloud",     "#4 DevOps Native",       [2, 4, 2, 1, 2, 1, 1, 2], [0.50, 0.50, 0.35, 0.25]),
    ("P8 UAT Crisis",           "#12 Crisis/Firefight",   [3, 2, 4, 1, 3, 3, 2, 1], [0.25, 0.25, 0.80, 0.10]),
    ("P9 Planning Phase",       "#13 Planning/Pre-Deliv", [2, 3, 2, 2, 3, 1, 1, 4], [0.50, 0.50, 0.25, 0.80]),
    ("P10 Golden Enterprise",   "#9 Ent Balanced",        [3, 3, 3, 3, 5, 2, 3, 5], [0.80, 0.80, 0.25, 0.65]),
    ("P11 Automotive Embedded", "#8 Reg Stage-Gate",      [5, 1, 5, 5, 4, 4, 3, 2], [0.80, 0.65, 0.25, 0.80]),
    ("P12 Legacy Modernisation","#10 Legacy Maintenance",  [3, 2, 3, 3, 1, 1, 4, 3], [0.10, 0.25, 0.25, 0.50]),
]

# Reference: all 15 archetype slider defaults
ARCHETYPE_SLIDER_DEFAULTS = {
    "#1 Micro Startup":       [0.10, 0.10, 0.80, 0.10],
    "#2 Small Agile":         [0.25, 0.25, 0.65, 0.25],
    "#3 Scaling Startup":     [0.50, 0.35, 0.50, 0.35],
    "#4 DevOps Native":       [0.50, 0.50, 0.35, 0.25],
    "#5 Component Heroes":    [0.50, 0.50, 0.50, 0.50],
    "#6 Matrix Programme":    [0.65, 0.50, 0.25, 0.50],
    "#7 Outsource-Managed":   [0.65, 0.65, 0.25, 0.65],
    "#8 Reg Stage-Gate":      [0.80, 0.65, 0.25, 0.80],
    "#9 Ent Balanced":        [0.80, 0.80, 0.25, 0.65],
    "#10 Legacy Maintenance":  [0.10, 0.25, 0.25, 0.50],
    "#11 Modernisation":      [0.35, 0.25, 0.50, 0.50],
    "#12 Crisis/Firefight":   [0.25, 0.25, 0.80, 0.10],
    "#13 Planning/Pre-Deliv": [0.50, 0.50, 0.25, 0.80],
    "#14 Platform/Internal":  [0.50, 0.80, 0.25, 0.50],
    "#15 Regulated Startup":  [0.25, 0.10, 0.80, 0.50],
}


# ---------------------------------------------------------------------------
# Layer 2: State modifiers (domain-derived, not optimised)
# ---------------------------------------------------------------------------
# These capture information that dimensions structurally cannot encode:
# where the project HAS BEEN, not just what it IS.

@dataclass
class ProjectState:
    """Additional context beyond dimensions that affects slider values.

    All fields default to the neutral/"no modifier" value so the state
    layer is opt-in — omitting it gives pure structural baseline.
    """
    project_phase: str = "execution"       # planning | early_execution | execution | late_execution | transition | maintenance
    crisis_level: str = "none"             # none | emerging | acute | terminal
    delivery_culture: str = "traditional"  # traditional | hybrid | devops_native
    resource_erosion: str = "none"         # none | moderate | severe


# Modifier tables: adjustments to [Investment, Recovery, Overwork, Time]
# Each row is additive to the structural baseline.

PHASE_MODIFIERS = {
    #                              Inv    Rec    Owk    Time
    "planning":        np.array([ 0.05,  0.05, -0.20,  0.35]),  # No execution pressure, time abundant
    "early_execution": np.array([ 0.00,  0.00, -0.05,  0.05]),  # Ramp-up, slightly relaxed
    "execution":       np.array([ 0.00,  0.00,  0.00,  0.00]),  # Baseline — no adjustment
    "late_execution":  np.array([-0.05, -0.05,  0.10, -0.15]),  # Crunch time, resources thinning
    "transition":      np.array([-0.05,  0.00,  0.05, -0.10]),  # Handover pressure
    "maintenance":     np.array([ 0.00,  0.05, -0.10,  0.05]),  # Stable cadence, low urgency
}

CRISIS_MODIFIERS = {
    #                              Inv    Rec    Owk    Time
    "none":     np.array([ 0.00,  0.00,  0.00,  0.00]),
    "emerging": np.array([-0.05, -0.05,  0.08, -0.05]),  # Early warning signs
    "acute":    np.array([-0.15, -0.10,  0.20, -0.25]),  # Active crisis: resources spent, recovery eroded
    "terminal": np.array([-0.25, -0.20,  0.25, -0.35]),  # Beyond recovery: everything degraded
}

CULTURE_MODIFIERS = {
    # DevOps culture provides resilience and reduces overwork through
    # automation, BUT only when dimensions don't already capture this
    # (i.e., D5 < 4 and D8 < 4 — otherwise culture is already reflected
    # in the structural baseline via team stability and coherence).
    #                              Inv    Rec    Owk    Time
    "traditional":  np.array([ 0.00,  0.00,  0.00,  0.00]),
    "hybrid":       np.array([ 0.00,  0.05, -0.05,  0.00]),
    "devops_native": np.array([-0.05,  0.15, -0.20,  0.00]),
}

EROSION_MODIFIERS = {
    # Resource erosion for legacy/declining projects where investment
    # capacity has been cut over time. Distinct from lifecycle stage
    # (D7) — a mature product at D7=3 is well-funded; a legacy product
    # at D7=4 with erosion has had its budget stripped.
    #                              Inv    Rec    Owk    Time
    "none":     np.array([ 0.00,  0.00,  0.00,  0.00]),
    "moderate": np.array([-0.15, -0.05, -0.05,  0.00]),  # Budget cuts, team shrinking
    "severe":   np.array([-0.25, -0.15, -0.10, -0.05]),  # Skeleton crew, minimal investment
}


def compute_state_modifier(state: ProjectState,
                           dimensions: Optional[list[int]] = None) -> np.ndarray:
    """Compute total state modifier as sum of all applicable adjustments.

    The dimensions parameter is used for the culture modifier gate:
    DevOps culture bonus only applies when D5 < 4 AND D8 < 4, because
    otherwise the culture benefits are already captured by the structural
    baseline's team stability and coherence weights.
    """
    modifier = np.zeros(4)
    modifier += PHASE_MODIFIERS.get(state.project_phase, np.zeros(4))
    modifier += CRISIS_MODIFIERS.get(state.crisis_level, np.zeros(4))
    modifier += EROSION_MODIFIERS.get(state.resource_erosion, np.zeros(4))

    # Culture modifier with dimension gate
    culture_mod = CULTURE_MODIFIERS.get(state.delivery_culture, np.zeros(4))
    if dimensions is not None and state.delivery_culture in ("hybrid", "devops_native"):
        d5 = dimensions[4]  # Team stability
        d8 = dimensions[7]  # Organisational coherence
        if d5 >= 4 and d8 >= 4:
            # Culture already captured by high D5/D8 — skip to avoid double-counting
            culture_mod = np.zeros(4)
    modifier += culture_mod

    return modifier


# Persona state assignments (validated against persona narratives)
PERSONA_STATES = {
    "P1 Startup Chaos":        ProjectState(),  # Pure structural — startup extremity is in the dimensions
    "P2 Small Agile Team":     ProjectState(),  # Stable state, well-captured by dimensions
    "P3 Govt Waterfall":       ProjectState(),  # Stable state
    "P4 Enterprise Financial": ProjectState(),  # Stable state
    "P5 Medical Device":       ProjectState(),  # Stable state
    "P6 Failing Automation":   ProjectState(),  # Scaling growing pains — not a crisis, just structural
    "P7 Greenfield Cloud":     ProjectState(delivery_culture="devops_native"),  # DevOps culture beyond what D5=2/D8=2 capture
    "P8 UAT Crisis":           ProjectState(project_phase="late_execution", crisis_level="acute"),  # Active crisis: resources spent, recovery eroded
    "P9 Planning Phase":       ProjectState(project_phase="planning"),  # Planning phase grants time
    "P10 Golden Enterprise":   ProjectState(delivery_culture="devops_native"),  # DevOps culture, but D5=5/D8=5 → gate blocks modifier
    "P11 Automotive Embedded": ProjectState(),  # Stable state
    "P12 Legacy Modernisation": ProjectState(project_phase="maintenance", resource_erosion="moderate"),  # Budget stripped, maintenance mode
}


# ---------------------------------------------------------------------------
# Piecewise transform functions
# ---------------------------------------------------------------------------

@dataclass
class PiecewiseTransform:
    """Maps dimension values (1-5) to [0,1] via piecewise linear interpolation.

    values: dict mapping integer levels {1,2,3,4,5} to float in [0,1].
    For non-integer inputs, linearly interpolates between adjacent levels.
    """
    values: dict[int, float]
    name: str = "custom"

    def __call__(self, d: float) -> float:
        # Clamp to valid range
        d = max(1.0, min(5.0, float(d)))
        if d == int(d) and int(d) in self.values:
            return self.values[int(d)]
        # Interpolate
        lo = int(np.floor(d))
        hi = int(np.ceil(d))
        lo = max(1, min(4, lo))
        hi = min(5, lo + 1)
        frac = d - lo
        return self.values[lo] * (1 - frac) + self.values[hi] * frac

    def __repr__(self) -> str:
        vals = [f"{k}:{v:.2f}" for k, v in sorted(self.values.items())]
        return f"T<{self.name}>({', '.join(vals)})"


# Pre-defined transform shapes
def linear() -> PiecewiseTransform:
    """Monotonic positive: low dimension → low output, high → high."""
    return PiecewiseTransform(
        {1: 0.0, 2: 0.25, 3: 0.50, 4: 0.75, 5: 1.0}, name="linear"
    )


def inverse() -> PiecewiseTransform:
    """Monotonic negative: low dimension → high output, high → low."""
    return PiecewiseTransform(
        {1: 1.0, 2: 0.75, 3: 0.50, 4: 0.25, 5: 0.0}, name="inverse"
    )


def bell() -> PiecewiseTransform:
    """Peaks at midpoint (level 3), low at extremes."""
    return PiecewiseTransform(
        {1: 0.0, 2: 0.50, 3: 1.0, 4: 0.50, 5: 0.0}, name="bell"
    )


def mature_peak() -> PiecewiseTransform:
    """Peaks at level 3 (mature), drops at greenfield and legacy/EOL."""
    return PiecewiseTransform(
        {1: 0.10, 2: 0.40, 3: 0.90, 4: 0.20, 5: 0.10}, name="mature_peak"
    )


def startup_peak() -> PiecewiseTransform:
    """Peaks at level 1 (greenfield/startup), decays toward mature."""
    return PiecewiseTransform(
        {1: 0.90, 2: 0.70, 3: 0.30, 4: 0.20, 5: 0.20}, name="startup_peak"
    )


def time_lifecycle() -> PiecewiseTransform:
    """D7→Time: mature has established pace, legacy/EOL moderate."""
    return PiecewiseTransform(
        {1: 0.10, 2: 0.30, 3: 0.70, 4: 0.60, 5: 0.50}, name="time_lifecycle"
    )


# ---------------------------------------------------------------------------
# Slider model
# ---------------------------------------------------------------------------

@dataclass
class SliderSpec:
    """Specification for a single slider's computation.

    active_dims: indices (0-7) of dimensions that contribute
    transforms:  PiecewiseTransform per active dimension
    weights:     float weight per active dimension (optimisable)
    bias:        additive bias term (optimisable)
    """
    name: str
    active_dims: list[int]
    transforms: list[PiecewiseTransform]
    weights: np.ndarray  # shape (len(active_dims),)
    bias: float = 0.0

    def compute(self, dimensions: list[int]) -> float:
        """Compute slider value from dimension vector."""
        total = self.bias
        for idx, dim_idx in enumerate(self.active_dims):
            transformed = self.transforms[idx](dimensions[dim_idx])
            total += self.weights[idx] * transformed
        return max(0.0, min(1.0, total))


@dataclass
class SliderModel:
    """Complete two-layer model mapping dimensions + state to 4 sliders.

    Layer 1 (structural): Weighted piecewise transforms of 8 dimensions.
    Layer 2 (state):      Additive modifiers from project phase, crisis
                          level, delivery culture, and resource erosion.
    """
    sliders: list[SliderSpec]

    def compute_structural(self, dimensions: list[int]) -> list[float]:
        """Layer 1: Compute slider values from dimensions alone."""
        return [s.compute(dimensions) for s in self.sliders]

    def compute_all(self, dimensions: list[int],
                    state: Optional[ProjectState] = None) -> list[float]:
        """Compute slider values with both layers.

        If state is None, returns pure structural baseline (Layer 1 only).
        If state is provided, applies state modifiers (Layer 2) additively.
        """
        structural = np.array(self.compute_structural(dimensions))
        if state is not None:
            modifier = compute_state_modifier(state, dimensions)
            combined = np.clip(structural + modifier, 0.0, 1.0)
            return combined.tolist()
        return structural.tolist()

    def compute_dict(self, dimensions: list[int],
                     state: Optional[ProjectState] = None) -> dict[str, float]:
        """Compute sliders as a named dictionary."""
        values = self.compute_all(dimensions, state)
        return {s.name: v for s, v in zip(self.sliders, values)}

    def get_parameter_vector(self) -> np.ndarray:
        """Flatten all optimisable parameters (weights + biases) into a vector."""
        params = []
        for s in self.sliders:
            params.extend(s.weights.tolist())
            params.append(s.bias)
        return np.array(params)

    def set_parameter_vector(self, params: np.ndarray) -> None:
        """Set model parameters from a flat vector."""
        idx = 0
        for s in self.sliders:
            n = len(s.active_dims)
            s.weights = params[idx:idx + n].copy()
            idx += n
            s.bias = float(params[idx])
            idx += 1

    def get_parameter_bounds(self) -> list[tuple[float, float]]:
        """Bounds for each parameter: weights in [-1, 1], biases in [-0.5, 0.5]."""
        bounds = []
        for s in self.sliders:
            for _ in s.active_dims:
                bounds.append((-1.0, 1.0))
            bounds.append((-0.5, 0.5))
        return bounds

    def parameter_count(self) -> int:
        return sum(len(s.active_dims) + 1 for s in self.sliders)


# ---------------------------------------------------------------------------
# Domain-derived initial model
# ---------------------------------------------------------------------------

def build_initial_model() -> SliderModel:
    """Construct the model with domain-derived initial weights and transforms.

    Weights are hand-tuned starting points based on the qualitative
    relationships described in the SIMULATION_HANDOFF document.
    These will be refined by calibration against the 12 persona targets.
    """

    # S1: Investment Capacity
    # "Can you afford to move on the grid?"
    # Drivers: complexity (bigger org), regulation (forced funding),
    #          team stability (established org), outsourcing (budget exists),
    #          lifecycle (mature = budget, greenfield/legacy = constrained)
    investment = SliderSpec(
        name="Investment",
        active_dims=[2, 3, 4, 5, 6],  # D3, D4, D5, D6, D7
        transforms=[linear(), linear(), linear(), linear(), mature_peak()],
        weights=np.array([0.18, 0.22, 0.22, 0.12, 0.18]),
        bias=0.02,
    )

    # S2: Recovery Capacity
    # "Can you survive if things go wrong?"
    # Drivers: consequence (weak positive — high-stakes domains tend to have
    #          resilient orgs, though consequence itself doesn't create buffers),
    #          complexity (inverse — harder to recover from complex failures),
    #          regulation (weak positive — regulated industries have institutional
    #          resilience, insurance, legal buffers),
    #          team stability (strong — resilient teams = resilient org),
    #          lifecycle (mature = capital buffers; startup/legacy = fragile),
    #          coherence (coordinated crisis response)
    recovery = SliderSpec(
        name="Recovery",
        active_dims=[0, 2, 3, 4, 6, 7],  # D1, D3, D4, D5, D7, D8
        transforms=[linear(), inverse(), linear(), linear(), mature_peak(), linear()],
        weights=np.array([0.08, 0.10, 0.10, 0.28, 0.18, 0.20]),
        bias=0.02,
    )

    # S3: Overwork Capacity
    # "Can the team compensate through effort?"
    # Drivers: market pressure (survival instinct), regulation (inverse — can't
    #          cut corners), team stability (inverse — institutionalised = won't
    #          overwork), lifecycle (startup_peak — startups will do anything),
    #          coherence (inverse — fragmented orgs overwork reactively: P8),
    #          consequence (inverse — high-stakes domains don't overwork recklessly)
    overwork = SliderSpec(
        name="Overwork",
        active_dims=[0, 1, 3, 4, 6, 7],  # D1, D2, D4, D5, D7, D8
        transforms=[inverse(), linear(), inverse(), inverse(), startup_peak(), inverse()],
        weights=np.array([0.10, 0.18, 0.14, 0.20, 0.22, 0.12]),
        bias=0.05,
    )

    # S4: Time Capacity
    # "Can you afford to be slow?"
    # Drivers: consequence (high = must be careful = time granted),
    #          market pressure (inverse — strongest single relationship),
    #          regulation (deliberate pace mandated),
    #          lifecycle (complex: greenfield can go either way depending on
    #                    market pressure; mature = established cadence)
    time_cap = SliderSpec(
        name="Time",
        active_dims=[0, 1, 3, 6],  # D1, D2, D4, D7
        transforms=[linear(), inverse(), linear(), time_lifecycle()],
        weights=np.array([0.15, 0.32, 0.30, 0.14]),
        bias=0.05,
    )

    return SliderModel(sliders=[investment, recovery, overwork, time_cap])


# ---------------------------------------------------------------------------
# Calibration
# ---------------------------------------------------------------------------

def _build_calibration_arrays() -> tuple[list[list[int]], np.ndarray]:
    """Extract dimension vectors and target matrices from calibration data."""
    dims = [row[2] for row in CALIBRATION_DATA]
    targets = np.array([row[3] for row in CALIBRATION_DATA])
    return dims, targets


def _compute_loss(params: np.ndarray, model: SliderModel,
                  dims: list[list[int]], targets: np.ndarray,
                  prior_params: Optional[np.ndarray] = None,
                  reg_lambda: float = 0.0) -> float:
    """Mean squared error + L2 regularisation toward domain-derived priors.

    The regularisation term penalises weights that drift far from the
    hand-tuned initial values, preventing the optimiser from finding
    spurious correlations in only 12 data points.
    """
    model.set_parameter_vector(params)
    predictions = np.array([model.compute_all(d) for d in dims])
    mse = float(np.mean((predictions - targets) ** 2))
    if prior_params is not None and reg_lambda > 0:
        reg = reg_lambda * float(np.mean((params - prior_params) ** 2))
        return mse + reg
    return mse


def calibrate(model: SliderModel,
              dims: Optional[list[list[int]]] = None,
              targets: Optional[np.ndarray] = None,
              reg_lambda: float = 0.15,
              verbose: bool = True) -> dict:
    """Optimise model weights against calibration data with L2 regularisation.

    reg_lambda: strength of L2 penalty toward domain-derived initial weights.
        Higher values keep weights closer to domain priors (reduces overfitting
        but limits in-sample fit). 0.15 balances in-sample vs LOO-CV performance.

    Returns dict with: optimised model, initial/final loss, optimisation result.
    """
    if dims is None or targets is None:
        dims, targets = _build_calibration_arrays()

    initial_params = model.get_parameter_vector()
    prior_params = initial_params.copy()  # Domain-derived priors
    initial_loss = _compute_loss(initial_params, model, dims, targets)

    if verbose:
        print(f"Initial MSE: {initial_loss:.6f}  (RMSE: {np.sqrt(initial_loss):.4f})")
        print(f"Regularisation lambda: {reg_lambda}")

    result = minimize(
        _compute_loss,
        initial_params,
        args=(model, dims, targets, prior_params, reg_lambda),
        method="L-BFGS-B",
        bounds=model.get_parameter_bounds(),
        options={"maxiter": 5000, "ftol": 1e-12},
    )

    model.set_parameter_vector(result.x)
    # Report pure MSE (without regularisation term) for interpretability
    final_mse = _compute_loss(result.x, model, dims, targets)
    final_total = _compute_loss(result.x, model, dims, targets, prior_params, reg_lambda)

    if verbose:
        print(f"Final MSE:   {final_mse:.6f}  (RMSE: {np.sqrt(final_mse):.4f})")
        print(f"Final total: {final_total:.6f}  (MSE + reg)")
        print(f"Converged:   {result.success}  ({result.message})")

    return {
        "model": model,
        "initial_loss": initial_loss,
        "final_loss": final_mse,
        "result": result,
    }


def leave_one_out_cv(model_factory=build_initial_model,
                     verbose: bool = True) -> list[dict]:
    """Leave-one-out cross-validation across 12 personas.

    For each persona, fits on the other 11 and predicts the held-out one.
    Returns list of dicts with per-persona prediction errors.
    """
    dims, targets = _build_calibration_arrays()
    n = len(dims)
    results = []

    for i in range(n):
        # Build fresh model for each fold
        model = model_factory()
        train_dims = dims[:i] + dims[i + 1:]
        train_targets = np.vstack([targets[:i], targets[i + 1:]])

        calibrate(model, train_dims, train_targets, reg_lambda=0.15, verbose=False)

        predicted = np.array(model.compute_all(dims[i]))
        actual = targets[i]
        errors = predicted - actual
        abs_errors = np.abs(errors)

        results.append({
            "persona": CALIBRATION_DATA[i][0],
            "archetype": CALIBRATION_DATA[i][1],
            "predicted": predicted.tolist(),
            "actual": actual.tolist(),
            "errors": errors.tolist(),
            "abs_errors": abs_errors.tolist(),
            "mae": float(np.mean(abs_errors)),
        })

    if verbose:
        print("\n=== Leave-One-Out Cross-Validation ===\n")
        print(f"{'Persona':<28} {'MAE':>6}  {'Inv':>6} {'Rec':>6} {'Owk':>6} {'Time':>6}")
        print("-" * 72)
        for r in results:
            errs = r["abs_errors"]
            print(f"{r['persona']:<28} {r['mae']:>6.3f}  "
                  f"{errs[0]:>6.3f} {errs[1]:>6.3f} {errs[2]:>6.3f} {errs[3]:>6.3f}")

        overall_mae = np.mean([r["mae"] for r in results])
        print(f"\n{'Overall LOO-CV MAE:':<28} {overall_mae:.3f}")

    return results


# ---------------------------------------------------------------------------
# Residual report
# ---------------------------------------------------------------------------

def residual_report(model: SliderModel, use_state: bool = False,
                    verbose: bool = True) -> list[dict]:
    """Compute per-persona residuals for the fitted model.

    use_state: if True, applies Layer 2 state modifiers from PERSONA_STATES.
    """
    dims, targets = _build_calibration_arrays()
    results = []

    for i, (name, archetype, dim_vec, target) in enumerate(CALIBRATION_DATA):
        state = PERSONA_STATES.get(name) if use_state else None
        predicted = np.array(model.compute_all(dim_vec, state))
        structural = np.array(model.compute_structural(dim_vec))
        actual = np.array(target)
        errors = predicted - actual
        abs_errors = np.abs(errors)
        pred_cats = [to_categorical(v) for v in predicted]
        act_cats = [to_categorical(v) for v in actual]
        has_modifier = state is not None and state != ProjectState()

        results.append({
            "persona": name,
            "archetype": archetype,
            "structural": structural.tolist(),
            "predicted": predicted.tolist(),
            "actual": actual.tolist(),
            "pred_categories": pred_cats,
            "actual_categories": act_cats,
            "errors": errors.tolist(),
            "abs_errors": abs_errors.tolist(),
            "mae": float(np.mean(abs_errors)),
            "category_matches": sum(p == a for p, a in zip(pred_cats, act_cats)),
            "has_modifier": has_modifier,
        })

    if verbose:
        layer_label = "Structural + State" if use_state else "Structural Only"
        print(f"\n=== Residual Report ({layer_label}) ===\n")
        print(f"{'Persona':<28} {'MAE':>6}  {'Cat':>3} {'Mod':>4}  "
              f"{'Inv':>12} {'Rec':>12} {'Owk':>12} {'Time':>12}")
        print("-" * 108)
        for r in results:
            inv_str = f"{r['predicted'][0]:.2f}({r['actual'][0]:.2f})"
            rec_str = f"{r['predicted'][1]:.2f}({r['actual'][1]:.2f})"
            owk_str = f"{r['predicted'][2]:.2f}({r['actual'][2]:.2f})"
            tim_str = f"{r['predicted'][3]:.2f}({r['actual'][3]:.2f})"
            mod_flag = " *" if r["has_modifier"] else "  "
            print(f"{r['persona']:<28} {r['mae']:>6.3f}  {r['category_matches']:>3}/4 {mod_flag}  "
                  f"{inv_str:>12} {rec_str:>12} {owk_str:>12} {tim_str:>12}")

        overall_mae = np.mean([r["mae"] for r in results])
        overall_cat = np.mean([r["category_matches"] for r in results])
        print(f"\n{'Overall MAE:':<28} {overall_mae:.3f}")
        print(f"{'Avg category matches:':<28} {overall_cat:.1f}/4")

        # Split report: stable vs state-dependent personas
        stable = [r for r in results if not r["has_modifier"]]
        modified = [r for r in results if r["has_modifier"]]
        if stable:
            stable_mae = np.mean([r["mae"] for r in stable])
            stable_cat = np.mean([r["category_matches"] for r in stable])
            print(f"{'  Structural-only MAE:':<28} {stable_mae:.3f}  ({len(stable)} personas)")
            print(f"{'  Structural-only cat:':<28} {stable_cat:.1f}/4")
        if modified:
            mod_mae = np.mean([r["mae"] for r in modified])
            mod_cat = np.mean([r["category_matches"] for r in modified])
            print(f"{'  State-modified MAE:':<28} {mod_mae:.3f}  ({len(modified)} personas, marked *)")
            print(f"{'  State-modified cat:':<28} {mod_cat:.1f}/4")

    return results


# ---------------------------------------------------------------------------
# Sensitivity analysis
# ---------------------------------------------------------------------------

def slider_sensitivity(model: SliderModel, base_dimensions: list[int],
                       dimension_idx: int) -> dict:
    """Vary one dimension across 1-5, hold others fixed. Return slider values."""
    results = {}
    for level in range(1, 6):
        test_dims = list(base_dimensions)
        test_dims[dimension_idx] = level
        sliders = model.compute_all(test_dims)
        results[level] = {
            "values": sliders,
            "categories": [to_categorical(v) for v in sliders],
        }
    return results


def sensitivity_matrix(model: SliderModel,
                       base_dimensions: Optional[list[int]] = None,
                       verbose: bool = True) -> dict:
    """Full sensitivity analysis: all 8 dimensions x all 4 sliders.

    For each dimension, shows how each slider changes as that dimension
    moves from 1 to 5 (others held at base values).
    """
    if base_dimensions is None:
        # Default: mid-range profile [3,3,3,3,3,3,3,3]
        base_dimensions = [3, 3, 3, 3, 3, 3, 3, 3]

    base_sliders = model.compute_all(base_dimensions)
    results = {}

    for d_idx in range(8):
        sens = slider_sensitivity(model, base_dimensions, d_idx)
        # Compute range (max - min) for each slider across D=1..5
        all_vals = np.array([sens[level]["values"] for level in range(1, 6)])
        ranges = all_vals.max(axis=0) - all_vals.min(axis=0)
        results[d_idx] = {
            "dimension": DIMENSION_SHORT[d_idx],
            "sensitivity": sens,
            "ranges": ranges.tolist(),
        }

    if verbose:
        print(f"\n=== Sensitivity Matrix (base: {base_dimensions}) ===\n")
        print(f"{'Dimension':<10} {'Inv range':>10} {'Rec range':>10} "
              f"{'Owk range':>10} {'Time range':>10}")
        print("-" * 55)
        for d_idx in range(8):
            r = results[d_idx]["ranges"]
            print(f"{DIMENSION_SHORT[d_idx]:<10} {r[0]:>10.3f} {r[1]:>10.3f} "
                  f"{r[2]:>10.3f} {r[3]:>10.3f}")

        print(f"\nBase slider values: ", end="")
        for name, val in zip(SLIDER_SHORT, base_sliders):
            print(f"{name}={val:.2f} ({to_categorical(val)})", end="  ")
        print()

        # Identify top-2 most influential dimensions per slider
        print("\nTop-2 influential dimensions per slider:")
        for s_idx, s_name in enumerate(SLIDER_SHORT):
            dim_ranges = [(results[d]["ranges"][s_idx], d) for d in range(8)]
            dim_ranges.sort(reverse=True)
            top2 = dim_ranges[:2]
            print(f"  {s_name:<12}: {DIMENSION_SHORT[top2[0][1]]} ({top2[0][0]:.3f}), "
                  f"{DIMENSION_SHORT[top2[1][1]]} ({top2[1][0]:.3f})")

    return results


# ---------------------------------------------------------------------------
# Model parameter report
# ---------------------------------------------------------------------------

def print_model_parameters(model: SliderModel) -> None:
    """Print the current model weights and transforms for inspection."""
    print("\n=== Model Parameters ===\n")
    for spec in model.sliders:
        print(f"--- {spec.name} (bias={spec.bias:.4f}) ---")
        for i, dim_idx in enumerate(spec.active_dims):
            print(f"  {DIMENSION_SHORT[dim_idx]:<5} w={spec.weights[i]:>7.4f}  "
                  f"T={spec.transforms[i]}")
        print()


# ---------------------------------------------------------------------------
# Edge case validation
# ---------------------------------------------------------------------------

def validate_edge_cases(model: SliderModel, verbose: bool = True) -> None:
    """Check that extreme dimension profiles produce sensible slider values."""
    cases = [
        ("All minimum [1,1,1,1,1,1,1,1]", [1, 1, 1, 1, 1, 1, 1, 1]),
        ("All maximum [5,5,5,5,5,5,5,5]", [5, 5, 5, 5, 5, 5, 5, 5]),
        ("All mid-range [3,3,3,3,3,3,3,3]", [3, 3, 3, 3, 3, 3, 3, 3]),
        ("High stakes, no resources [5,5,5,5,1,1,1,1]", [5, 5, 5, 5, 1, 1, 1, 1]),
        ("Low stakes, high resources [1,1,1,1,5,5,5,5]", [1, 1, 1, 1, 5, 5, 5, 5]),
        ("Regulated startup [3,4,2,5,2,1,1,3]", [3, 4, 2, 5, 2, 1, 1, 3]),
    ]

    if verbose:
        print("\n=== Edge Case Validation ===\n")
        print(f"{'Profile':<45} {'Inv':>10} {'Rec':>10} {'Owk':>10} {'Time':>10}")
        print("-" * 90)
        for label, dims in cases:
            sliders = model.compute_all(dims)
            cats = [to_categorical(v) for v in sliders]
            print(f"{label:<45} "
                  f"{sliders[0]:.2f} {cats[0]:>4}  "
                  f"{sliders[1]:.2f} {cats[1]:>4}  "
                  f"{sliders[2]:.2f} {cats[2]:>4}  "
                  f"{sliders[3]:.2f} {cats[3]:>4}")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Run full calibration pipeline and report results."""
    print("=" * 70)
    print("  Dimension-to-Slider Mapping: Two-Layer Model")
    print("  Layer 1: Structural baseline (from dimensions)")
    print("  Layer 2: State modifiers (phase, crisis, culture, erosion)")
    print("=" * 70)

    # 1. Build and calibrate structural model (Layer 1)
    print("\n--- Phase 1: Calibrate Structural Baseline (Layer 1) ---\n")
    model = build_initial_model()
    cal_result = calibrate(model, verbose=True)
    print_model_parameters(model)

    # 2. Layer 1 residuals (structural only)
    print("\n--- Phase 2: Layer 1 Residuals (Structural Only) ---")
    structural_results = residual_report(model, use_state=False)

    # 3. Layer 1 + Layer 2 residuals (with state modifiers)
    print("\n--- Phase 3: Layer 1+2 Residuals (Structural + State) ---")
    combined_results = residual_report(model, use_state=True)

    # 4. Layer comparison summary
    print("\n--- Phase 4: Layer Comparison ---\n")
    s_mae = np.mean([r["mae"] for r in structural_results])
    c_mae = np.mean([r["mae"] for r in combined_results])
    s_cat = np.mean([r["category_matches"] for r in structural_results])
    c_cat = np.mean([r["category_matches"] for r in combined_results])
    print(f"{'Metric':<30} {'Layer 1 Only':>14} {'Layer 1+2':>14} {'Improvement':>14}")
    print("-" * 75)
    print(f"{'Overall MAE':<30} {s_mae:>14.3f} {c_mae:>14.3f} {s_mae - c_mae:>+14.3f}")
    print(f"{'Avg category matches':<30} {s_cat:>13.1f}/4 {c_cat:>13.1f}/4 {c_cat - s_cat:>+13.1f}/4")

    # Per-persona improvement breakdown
    print(f"\n{'Persona':<28} {'L1 MAE':>8} {'L1+2 MAE':>10} {'Delta':>8}  State")
    print("-" * 75)
    for s, c in zip(structural_results, combined_results):
        delta = s["mae"] - c["mae"]
        state = PERSONA_STATES.get(s["persona"], ProjectState())
        state_desc = []
        if state.project_phase != "execution":
            state_desc.append(f"phase={state.project_phase}")
        if state.crisis_level != "none":
            state_desc.append(f"crisis={state.crisis_level}")
        if state.delivery_culture != "traditional":
            state_desc.append(f"culture={state.delivery_culture}")
        if state.resource_erosion != "none":
            state_desc.append(f"erosion={state.resource_erosion}")
        state_str = ", ".join(state_desc) if state_desc else "(structural only)"
        print(f"{s['persona']:<28} {s['mae']:>8.3f} {c['mae']:>10.3f} {delta:>+8.3f}  {state_str}")

    # 5. LOO-CV (structural layer only — state modifiers are domain-derived, not fitted)
    print("\n--- Phase 5: Leave-One-Out Cross-Validation (Layer 1) ---")
    loo_results = leave_one_out_cv()

    # 6. Sensitivity analysis
    print("\n--- Phase 6: Sensitivity Analysis (Structural Baseline) ---")
    sensitivity_matrix(model)

    # 7. Edge cases (structural only — state modifiers are context-specific)
    print("\n--- Phase 7: Edge Case Validation (Structural Baseline) ---")
    validate_edge_cases(model)


if __name__ == "__main__":
    main()
