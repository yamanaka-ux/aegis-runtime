import copy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List
from src.guardrails import DeterministicPolicyEngine


@dataclass
class ExecutedStep:
    step_id: int
    action_name: str
    params: Dict[str, Any]
    snapshot_before: Dict[str, Any]
    compensate_fn: Callable[[Dict[str, Any], Dict[str, Any]], None]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SagaTransactionManager:
    """Manages multi-step stateful execution with automatic rollback compensation."""

    def __init__(self, state: Dict[str, Any]):
        self.state = state
        self.completed_steps: List[ExecutedStep] = []
        self.audit_log: List[str] = []

    def _log(self, message: str) -> None:
        ts = datetime.now(timezone.utc).strftime("%H:%M:%S.%f")[:-3]
        entry = f"[{ts} UTC] {message}"
        self.audit_log.append(entry)
        print(entry)

    def execute_step(
        self,
        step_id: int,
        action_name: str,
        params: Dict[str, Any],
        forward_fn: Callable[[Dict[str, Any], Dict[str, Any]], None],
        compensate_fn: Callable[[Dict[str, Any], Dict[str, Any]], None],
    ) -> None:
        self._log(f"STEP {step_id} | Validating '{action_name}' with params {params}...")

        # 1. Check deterministic guardrails before mutating anything
        DeterministicPolicyEngine.validate(action_name, params, self.state)

        # 2. Capture full state snapshot before execution
        snapshot = copy.deepcopy(self.state)

        # 3. Execute forward action
        forward_fn(self.state, params)

        # 4. Record completed step for potential rollback
        self.completed_steps.append(
            ExecutedStep(
                step_id=step_id,
                action_name=action_name,
                params=params,
                snapshot_before=snapshot,
                compensate_fn=compensate_fn,
            )
        )
        self._log(f"STEP {step_id} | SUCCESS. Current state: {self.state}")

    def rollback(self) -> None:
        self._log("⚠️ INITIATING ROLLBACK (Reverting state in reverse order)...")
        for step in reversed(self.completed_steps):
            self._log(f"ROLLBACK STEP {step.step_id} | Reverting '{step.action_name}'...")
            step.compensate_fn(self.state, step.snapshot_before)
        self.completed_steps.clear()
        self._log(f"✅ ROLLBACK COMPLETE. State restored to initial condition: {self.state}")
