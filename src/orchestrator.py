from typing import Any, Dict, List
from src.guardrails import PolicyViolationError
from src.saga import SagaTransactionManager
from src.tools import TOOL_REGISTRY


class TransactionalAgentOrchestrator:
    """Executes a multi-step agent plan inside a safe, audited transaction boundary."""

    def __init__(self, initial_state: Dict[str, Any]):
        self.saga = SagaTransactionManager(initial_state)

    def run_plan(self, agent_plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        print("=== STARTING AGENT PLAN EXECUTION ===")
        try:
            for idx, step in enumerate(agent_plan, start=1):
                action = step["action"]
                params = step["params"]

                if action not in TOOL_REGISTRY:
                    raise PolicyViolationError(f"Unknown tool: '{action}'.")

                forward_fn, compensate_fn = TOOL_REGISTRY[action]
                self.saga.execute_step(
                    step_id=idx,
                    action_name=action,
                    params=params,
                    forward_fn=forward_fn,
                    compensate_fn=compensate_fn,
                )

            print("=== ALL STEPS EXECUTED & COMMITTED SUCCESSFULLY ===")
            return {"status": "COMMITTED", "final_state": self.saga.state}

        except PolicyViolationError as err:
            print(f"\n❌ POLICY VIOLATION DETECTED: {err}")
            self.saga.rollback()
            return {
                "status": "ROLLED_BACK",
                "reason": str(err),
                "final_state": self.saga.state,
            }

