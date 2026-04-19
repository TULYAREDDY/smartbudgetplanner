from typing import List, Dict, Tuple

def greedy_optimizer(
    reducible_expenses: List[Dict],
    income: float,
    fixed_total: float,
    emi_total: float,
    target_savings: float
) -> Tuple[List[Dict], Dict]:
    """
    Reduce reducible expenses based on priority caps until net savings goal is reached.
    Net savings = income - (fixed_total + emi_total + sum(optimized reducible))
    Priority caps:
        Low: 70% reduction max
        Medium: 40% reduction max
        High: 10% reduction max
    Traverse by priority: Low → Medium → High.
    Returns modified expense list and status dict.
    """
    priority_order = {'Low': 0, 'Medium': 1, 'High': 2}
    priority_caps = {
        'Low': 0.7,
        'Medium': 0.4,
        'High': 0.1
    }
    # Sort by priority: Low first, then Medium, then High
    sorted_expenses = sorted(reducible_expenses, key=lambda e: priority_order.get(e.get('priority', 'Medium'), 1))
    optimized_expenses = []
    # Track original amounts for percent reduction
    original_map = {id(exp): exp['amount'] for exp in reducible_expenses}
    # Start with all original amounts
    current_reducible = [exp['amount'] for exp in sorted_expenses]
    # For each expense, reduce as much as possible (up to cap), stop if net savings goal is met
    for idx, expense in enumerate(sorted_expenses):
        if expense.get('isLocked', False):
            optimized_expenses.append(expense)
            continue
        priority = expense.get('priority', 'Medium')
        cap = priority_caps.get(priority, 0.4)
        original_amount = expense['amount']
        max_reduction = original_amount * cap
        # Calculate current net savings before reducing this expense
        current_optimized = [e['amount'] for e in optimized_expenses] + [original_amount] + [sorted_expenses[i]['amount'] for i in range(idx+1, len(sorted_expenses))]
        net_savings = income - (fixed_total + emi_total + sum(current_optimized))
        needed = target_savings - net_savings
        # If already met, no more reduction needed
        if net_savings >= target_savings:
            optimized_expenses.append(expense)
            continue
        # Reduce as much as possible, but not below cap or below needed
        reduction = min(max_reduction, needed, original_amount)
        new_amount = original_amount - reduction if needed > 0 else original_amount
        optimized_expense = expense.copy()
        optimized_expense['amount'] = round(new_amount, 2)
        optimized_expenses.append(optimized_expense)
    # After all reductions, recalculate net savings
    final_reducible_total = sum(e['amount'] for e in optimized_expenses if not e.get('isLocked', False))
    net_savings = income - (fixed_total + emi_total + final_reducible_total)
    goal_met = net_savings >= target_savings
    gap_remaining = max(0, target_savings - net_savings)
    total_possible_savings = net_savings if net_savings > 0 else 0
    if not reducible_expenses or all(e.get('isLocked', False) for e in reducible_expenses):
        status_message = "❌ No reducible expenses could be optimized. All expenses are marked High Priority or Locked. Try reducing priorities or setting a realistic savings target."
    elif goal_met:
        status_message = f"✅ Savings Goal Achieved! Net savings: ₹{int(round(net_savings))} meets your target of ₹{int(round(target_savings))}."
    elif total_possible_savings > 0:
        status_message = f"⚠️ Partial Optimization: Could only help you save ₹{int(round(net_savings))} out of your target ₹{int(round(target_savings))}. Gap Remaining: ₹{int(round(gap_remaining))}"
    else:
        status_message = "❌ No reducible expenses could be optimized. All expenses are marked High Priority or Locked. Try reducing priorities or setting a realistic savings target."
    status = {
        'actual_savings': round(net_savings, 2),
        'total_possible_savings': round(total_possible_savings, 2),
        'savings_goal_reached': goal_met,
        'gap_remaining': round(gap_remaining, 2),
        'status_message': status_message
    }
    # Reorder to match original input order
    optimized_expenses_final = []
    for exp in reducible_expenses:
        match = next((e for e in optimized_expenses if e.get('name') == exp.get('name') and e.get('category') == exp.get('category')), None)
        optimized_expenses_final.append(match if match else exp)
    return optimized_expenses_final, status
