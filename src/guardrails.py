from typing import Any, Dict


class PolicyViolationError(Exception):
    """Raised when an agent action violates deterministic business rules."""
    pass


class DeterministicPolicyEngine:
    MIN_PRICE_FLOOR = 75.0
    MAX_SINGLE_ALLOCATION = 500.0

    @classmethod
    def validate(cls, action_name: str, params: Dict[str, Any], state: Dict[str, Any]) -> None:
        if action_name == "allocate_budget":
            amount = params.get("amount", 0.0)
            if amount <= 0:
                raise PolicyViolationError("Budget allocation must be greater than 0.")
            if amount > cls.MAX_SINGLE_ALLOCATION:
                raise PolicyViolationError(
                    f"Allocation ${amount} exceeds max single transaction limit (${cls.MAX_SINGLE_ALLOCATION})."
                )
            if amount > state["budget_remaining"]:
                raise PolicyViolationError(
                    f"Insufficient budget (requested: ${amount}, available: ${state['budget_remaining']})."
                )

        elif action_name == "launch_campaign":
            cost = params.get("cost", 0.0)
            if cost > state["budget_remaining"]:
                raise PolicyViolationError(
                    f"Campaign cost ${cost} exceeds remaining budget (${state['budget_remaining']})."
                )

        elif action_name == "update_price":
            sku = params.get("sku")
            new_price = params.get("new_price", 0.0)
            if sku not in state["catalog"]:
                raise PolicyViolationError(f"SKU '{sku}' not found in catalog.")
            if new_price < cls.MIN_PRICE_FLOOR:
                raise PolicyViolationError(
                    f"New price ${new_price} violates minimum price floor (${cls.MIN_PRICE_FLOOR})."
                )
        else:
            raise PolicyViolationError(f"Action '{action_name}' is not in the allowed tools list.")



