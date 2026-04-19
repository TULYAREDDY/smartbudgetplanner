from typing import List, Dict, Optional

def dp_emi_selector(emi_plans: List[Dict], income: float) -> Dict:
    """
    Use 0/1 Knapsack logic to select the best EMI plan.
    Inputs: loan amount, interest, duration, necessity, monthlyPayment
    Scored by affordability, duration, necessity.
    Returns best plan and alternative plans.
    """
    n = len(emi_plans)
    max_capacity = int(income * 0.4)  # Max EMI capacity is 40% of income
    
    # Prepare weights and values for knapsack
    weights = [int(plan['monthlyPayment']) for plan in emi_plans]
    values = []
    for plan in emi_plans:
        affordability_score = min(10, (max_capacity / plan['monthlyPayment']) * 5)
        duration = plan['durationMonths']
        duration_score = 8 if duration <= 24 else 10 if duration <= 60 else 7 if duration <= 120 else 5
        necessity = plan.get('necessity', 5)
        interest_score = max(1, 10 - (plan['interestRate'] / 2))
        total_score = (affordability_score * 0.4) + (interest_score * 0.3) + (duration_score * 0.1) + (necessity * 0.2)
        values.append(total_score)
    
    # Initialize DP table
    dp = [[0 for _ in range(max_capacity + 1)] for _ in range(n + 1)]
    
    for i in range(1, n + 1):
        for w in range(max_capacity + 1):
            if weights[i-1] <= w:
                dp[i][w] = max(dp[i-1][w], dp[i-1][w - weights[i-1]] + values[i-1])
            else:
                dp[i][w] = dp[i-1][w]
    
    # Backtrack to find selected plans
    w = max_capacity
    selected_indices = []
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            selected_indices.append(i-1)
            w -= weights[i-1]
    
    selected_plans = [emi_plans[i] for i in selected_indices]
    alternative_plans = [plan for i, plan in enumerate(emi_plans) if i not in selected_indices]
    
    # Sort selected plans by score descending
    selected_plans.sort(key=lambda x: values[emi_plans.index(x)], reverse=True)
    
    result = {
        'selected_plans': selected_plans,
        'alternative_plans': alternative_plans,
        'recommendation': "Based on your financial data, here are the recommended EMI plans that fit your budget and criteria."
    }
    
    return result
