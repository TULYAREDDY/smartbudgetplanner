from typing import List, Dict, Tuple

def backtrack_expenses(reducible_expenses: List[Dict], savings_goal: float) -> Tuple[List[Dict], bool]:
    """
    Use DFS to find alternate expense cuts if greedy optimizer fails.
    Returns the combination of cuts that achieve the goal and success flag.
    """
    n = len(reducible_expenses)
    priority_caps = {
        'Low': 0.7,
        'Medium': 0.4,
        'High': 0.1
    }
    
    best_solution = None
    best_reduction = 0.0
    
    def dfs(index, current_expenses, current_reduction):
        nonlocal best_solution, best_reduction
        
        if current_reduction >= savings_goal:
            if best_solution is None or current_reduction > best_reduction:
                best_solution = current_expenses.copy()
                best_reduction = current_reduction
            return
        
        if index == n:
            return
        
        expense = reducible_expenses[index]
        if expense.get('isLocked', False):
            # Skip locked expenses
            dfs(index + 1, current_expenses + [expense], current_reduction)
            return
        
        priority = expense.get('priority', 'Medium')
        cap = priority_caps.get(priority, 0.4)
        original_amount = expense['amount']
        max_reduction = original_amount * cap
        
        # Try all possible reductions from 0 to max_reduction in steps
        steps = 10
        for step in range(steps + 1):
            reduction = max_reduction * (step / steps)
            new_amount = original_amount - reduction
            new_expense = expense.copy()
            new_expense['amount'] = round(new_amount, 2)
            dfs(index + 1, current_expenses + [new_expense], current_reduction + reduction)
    
    dfs(0, [], 0.0)
    
    if best_solution is None:
        return reducible_expenses, False
    else:
        return best_solution, True
