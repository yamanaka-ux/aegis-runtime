from typing import Any, Callable, Dict, Tuple


def forward_allocate_budget(state: Dict[str, Any], params: Dict[str, Any]) -> None:
    amount = params["amount"]
    state["budget_remaining"] -= amount
    state["allocated_pool"] += amount


def compensate_allocate_budget(state: Dict[str, Any], snapshot_before: Dict[str, Any]) -> None:
    state["budget_remaining"] = snapshot_before["budget_remaining"]
    state["allocated_pool"] = snapshot_before["allocated_pool"]


def forward_launch_campaign(state: Dict[str, Any], params: Dict[str, Any]) -> None:
    campaign_id = params["campaign_id"]
    cost = params["cost"]
    state["budget_remaining"] -= cost
    state["active_campaigns"].append(campaign_id)


def compensate_launch_campaign(state: Dict[str, Any], snapshot_before: Dict[str, Any]) -> None:
    state["budget_remaining"] = snapshot_before["budget_remaining"]
    state["active_campaigns"] = list(snapshot_before["active_campaigns"])


def forward_update_price(state: Dict[str, Any], params: Dict[str, Any]) -> None:
    sku = params["sku"]
    state["catalog"][sku]["price"] = params["new_price"]


def compensate_update_price(state: Dict[str, Any], snapshot_before: Dict[str, Any]) -> None:
    for sku, item_data in snapshot_before["catalog"].items():
        state["catalog"][sku]["price"] = item_data["price"]


TOOL_REGISTRY: Dict[str, Tuple[Callable, Callable]] = {
    "allocate_budget": (forward_allocate_budget, compensate_allocate_budget),
    "launch_campaign": (forward_launch_campaign, compensate_launch_campaign),
    "update_price": (forward_update_price, compensate_update_price),
}
