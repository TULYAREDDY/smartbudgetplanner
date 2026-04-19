from typing import List, Dict

def decision_tree_advice(optimized_expenses: List[Dict], recommended_emi_plan: Dict, income: float) -> Dict:
    """
    Interpret the final data to generate alerts, tips, and recommendations.
    Returns a dict with alert messages and tips.
    """
    alerts = []
    tips = []
    
    total_expenses = sum(expense['amount'] for expense in optimized_expenses)
    balance = income - total_expenses
    savings_rate = (balance / income) * 100 if income > 0 else 0
    
    # Alerts based on financial situation
    if balance < 0:
        alerts.append("Your expenses exceed your income. Immediate action required!")
    if 0 <= savings_rate < 10:
        alerts.append("Your savings rate is below 10%. Consider reducing non-essential expenses.")
    if recommended_emi_plan and recommended_emi_plan.get('monthlyPayment', 0) > income * 0.4:
        alerts.append("Your recommended EMI payments exceed 40% of your income, which is higher than recommended.")
    
    # Tips based on analysis
    tips.append("Try the 50/30/20 rule: 50% for needs, 30% for wants, and 20% for savings.")
    tips.append("Consider automating your savings by setting up automatic transfers.")
    tips.append("Review your subscriptions and cancel those you don't use regularly.")
    tips.append("Look for ways to increase your income through side gigs or skill development.")
    
    # Additional advice based on expense priorities
    high_priority_expenses = [e for e in optimized_expenses if e.get('priority') == 'High' and not e.get('isLocked', False)]
    if high_priority_expenses:
        tips.append("Review high priority expenses carefully before making cuts.")
    
    return {
        'alerts': alerts,
        'tips': tips
    }
