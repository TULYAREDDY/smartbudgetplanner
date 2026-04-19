from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file, make_response
from .logic.greedy_optimizer import greedy_optimizer
from .logic.dp_emi_selector import dp_emi_selector
from .logic.decision_tree_advice import decision_tree_advice
from .logic.backtrack_expenses import backtrack_expenses
from typing import List, Dict
import json
import google.generativeai as genai
from datetime import datetime
import os
from dotenv import load_dotenv
import re
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from calendar import month_name
import shutil

# Load environment variables
load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    print("Warning: GOOGLE_API_KEY not found in environment variables. AI analysis will be disabled.")
    GOOGLE_API_KEY = "dummy_key"

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')  # Needed for session management

USERS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'users.json')
USERS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'users')
if not os.path.exists(USERS_DIR):
    os.makedirs(USERS_DIR)

# Ensure required folders exist at startup
data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
for folder in ['results', 'users']:
    folder_path = os.path.join(data_dir, folder)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

# Helper to load users
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# Helper to save users
def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2)

# Helper to load user profile
def load_user_profile(username):
    profile_path = os.path.join(USERS_DIR, username, 'profile.json')
    if os.path.exists(profile_path):
        with open(profile_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

# Helper to save user profile
def save_user_profile(username, profile):
    user_dir = os.path.join(USERS_DIR, username)
    os.makedirs(user_dir, exist_ok=True)
    profile_path = os.path.join(user_dir, 'profile.json')
    with open(profile_path, 'w', encoding='utf-8') as f:
        json.dump(profile, f, indent=2)

def get_ai_advice(expenses: List[Dict], salary: float, emi_plans: List[Dict], bank_statement: Dict = None) -> Dict:
    """Get AI-powered financial advice using Gemini API."""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if GOOGLE_API_KEY == "dummy_key":
        return {
            'detailed_analysis': "Smart Model analysis is disabled. Please set GOOGLE_API_KEY in .env file to enable analysis.",
            'timestamp': current_time
        }
    
    prompt = f"""
    Analyze the following financial situation and provide structured advice. Your response MUST be a JSON array of objects. Each object in the array should represent a section and MUST have two keys:
    - `header`: A string for the section title (e.g., "1. Budget Analysis").
    - `body`: A multi-line string for the detailed content of that section.

    Here is the financial data:
    Monthly Salary: ₹{salary:,.2f}
    
    Current Expenses:
    {json.dumps(expenses, indent=2)}
    
    EMI Plans:
    {json.dumps(emi_plans, indent=2)}
    """
    
    if bank_statement:
        prompt += f"""
        
    Bank Statement Analysis:
    {json.dumps(bank_statement, indent=2)}
    """
    
    prompt += """
    Ensure your response includes sections on:
    1. Budget Analysis
    2. Expense Optimization Suggestions
    3. Investment Recommendations
    4. Emergency Fund Advice
    5. Long-Term Financial Planning
    6. Transaction Pattern Analysis
    7. Spending Behavior Insights
    8. Cash Flow Optimization
    9. Banking Product Recommendations
    
    Each section should be concise and actionable. Ensure the JSON is valid.
    """
    
    try:
        response = model.generate_content(prompt)
        raw_gemini_text = response.text

        # Attempt to extract JSON from a markdown code block using string slicing for robustness
        json_start_tag = "```json"
        json_end_tag = "```"

        start_index = raw_gemini_text.find(json_start_tag)
        if start_index != -1:
            # Adjust start_index to point right after the ```json marker
            start_index += len(json_start_tag)
            end_index = raw_gemini_text.rfind(json_end_tag, start_index)
            
            if end_index != -1:
                json_string = raw_gemini_text[start_index:end_index].strip()
                
                if json_string:
                    try:
                        parsed_response = json.loads(json_string)
                        return {
                            'detailed_analysis': parsed_response,
                            'timestamp': current_time
                        }
                    except json.JSONDecodeError as e:
                        return {
                            'detailed_analysis': f"AI response contained JSON markdown, but parsing failed (JSONDecodeError: {str(e)}). Extracted JSON string: '{json_string}'. Raw Gemini text: {raw_gemini_text}",
                            'timestamp': current_time,
                            'error': "JSON parsing failed"
                        }
                else:
                    return {
                        'detailed_analysis': f"AI response contained an empty JSON markdown block. Raw Gemini text: {raw_gemini_text}",
                        'timestamp': current_time,
                        'error': "Empty JSON block"
                    }
            else:
                return {
                    'detailed_analysis': f"AI response contained ```json but no closing ```. Raw Gemini text: {raw_gemini_text}",
                    'timestamp': current_time,
                    'error': "Missing closing JSON markdown fence"
                }
        else:
            return {
                'detailed_analysis': f"AI response not in expected ```json``` markdown format. Raw Gemini text: {raw_gemini_text}",
                'timestamp': current_time,
                'error': "JSON markdown not found"
            }
    except Exception as e:
        return {
            'detailed_analysis': f"Unable to get Smart Model analysis from Gemini at this time. Error: {str(e)}",
            'timestamp': current_time,
            'error': "Gemini API call failed"
        }

def format_currency(amount: float) -> str:
    """Format amount as Indian currency."""
    return f"₹{amount:,.2f}"

def analyze_expenses_by_category(expenses: List[Dict]) -> Dict:
    """Analyze expenses by category."""
    category_totals = {}
    for expense in expenses:
        category = expense['category']
        if category not in category_totals:
            category_totals[category] = 0
        category_totals[category] += expense['amount']
    return category_totals

def save_results_to_json(results: Dict, user_name: str):
    """Save results to a JSON file in the results/ directory."""
    safe_filename = "".join(c for c in user_name if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_filename = safe_filename.replace(' ', '_').lower()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_filename}_{timestamp}.json"
    results_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'results')
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    filepath = os.path.join(results_dir, filename)
    try:
        if 'smart_model_summary' in results and 'formatted_analysis' in results['smart_model_summary']:
            formatted_text = results['smart_model_summary']['formatted_analysis']
            formatted_text = formatted_text.replace('\n', '\\n').replace('"', '\\"')
            results['smart_model_summary']['formatted_analysis'] = formatted_text

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        content = content.replace('\\n', '\n')

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return filename  # Return just the filename, not the full path
    except Exception as e:
        return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        action = request.form.get('action')
        users = load_users()
        if action == 'register':
            if username in users:
                return render_template('login.html', error='Username already exists.')
            users[username] = {"password": password}
            save_users(users)
            # Create user folder and profile
            profile = {"username": username, "created_at": datetime.now().isoformat()}
            save_user_profile(username, profile)
            session['username'] = username
            return redirect(url_for('index'))
        # Login
        if username in users and users[username]['password'] == password:
            # Ensure user profile exists
            if not load_user_profile(username):
                profile = {"username": username, "created_at": datetime.now().isoformat()}
                save_user_profile(username, profile)
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid username or password.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# Decorator to require login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Protect index and analyze routes
@app.route('/')
@login_required
def index():
    """Render the main page."""
    # Get list of available bank statements
    bank_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'bank')
    bank_statements = [f for f in os.listdir(bank_dir) if f.endswith('.json')]
    
    # Generate a unique version string for cache busting
    current_time_version = datetime.now().timestamp()
    
    return render_template('index.html', bank_statements=bank_statements, current_time_version=current_time_version, username=session.get('username'))

@app.route('/get_bank_statement/<filename>')
def get_bank_statement(filename):
    """Get bank statement data."""
    try:
        bank_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'bank')
        with open(os.path.join(bank_dir, filename), 'r') as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/analyze', methods=['POST'])
@login_required
def analyze():
    """Analyze financial data and return results."""
    try:
        data = request.json
        user_name = session.get('username', data.get('user_name', 'user_' + datetime.now().strftime("%Y%m%d_%H%M%S")))
        salary = float(data.get('salary', 0))
        expenses = data.get('expenses', [])
        emi_plans = data.get('emi_plans', [])
        bank_statement = data.get('bank_statement')
        target_savings = float(data.get('target_savings', 0))
        if target_savings < 0:
            return jsonify({'success': False, 'error': 'Target savings must be a positive number.'}), 400
        
        # Separate fixed and reducible expenses
        fixed_expenses = [exp for exp in expenses if exp.get('expense_type') == 'Fixed']
        reducible_expenses = [exp for exp in expenses if exp.get('expense_type') == 'Reducible']

        # Calculate totals for fixed and EMI before optimization
        total_fixed = sum(e.get('amount', 0) for e in fixed_expenses)
        emi_total = 0
        emi_recommendation = dp_emi_selector(emi_plans, salary)
        if emi_recommendation and 'selected_plans' in emi_recommendation:
            emi_total = sum(plan.get('monthlyPayment', 0) for plan in emi_recommendation['selected_plans'])

        # Run optimization only on reducible expenses (now with net savings logic)
        optimized_reducible_expenses, optimizer_status = greedy_optimizer(
            reducible_expenses, salary, total_fixed, emi_total, target_savings
        )

        # Merge fixed expenses back with optimized reducible expenses
        optimized_expenses = fixed_expenses + optimized_reducible_expenses

        advice = decision_tree_advice(optimized_expenses, emi_recommendation, salary)
        # Get AI advice
        ai_advice = get_ai_advice(optimized_expenses, salary, emi_plans, bank_statement)

        # Calculate balance and savings
        total_optimized = sum(e.get('amount', 0) for e in optimized_expenses)
        balance = salary - total_fixed - total_optimized
        savings_rate = (balance / salary) if salary > 0 else 0

        # Prepare results
        results = {
            'user_name': user_name,
            'salary': salary,
            'target_savings': target_savings,
            'expenses': expenses,
            'optimized_expenses': optimized_expenses,
            'emi_recommendation': emi_recommendation,
            'advice': advice,
            'smart_model_summary': ai_advice,
            'bank_statement': bank_statement,
            'balance': balance,
            'savings_rate': savings_rate,
            'amount_saved': optimizer_status.get('actual_savings', 0),
            'total_possible_savings': optimizer_status.get('total_possible_savings', 0),
            'gap_remaining': optimizer_status.get('gap_remaining', 0),
            'goal_met': optimizer_status.get('savings_goal_reached', False),
            'status_message': optimizer_status.get('status_message', '')
        }

        # Save results to JSON
        filename = save_results_to_json(results, user_name)

        # --- Log storage: save every analysis with timestamp ---
        now = datetime.now()
        timestamp_str = now.strftime("%Y_%m_%d_%H%M%S")
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        user_dir = os.path.join(data_dir, user_name)
        os.makedirs(user_dir, exist_ok=True)
        log_path = os.path.join(user_dir, f"{user_name}_{timestamp_str}.json")
        # Compose log dict
        monthly_log = {
            'income': salary,
            'fixed_expenses': [e for e in expenses if e.get('expense_type') == 'Fixed'],
            'reducible_expenses': [e for e in expenses if e.get('expense_type') == 'Reducible'],
            'optimized_expenses': results.get('optimized_expenses'),
            'emi_plans': emi_plans,
            'selected_emis': results.get('selected_emis'),
            'balance': balance,
            'savings_rate': savings_rate,
            'alerts': results.get('alerts'),
            'tips': results.get('tips'),
            'investment_suggestions': results.get('investment_suggestions'),
            'summary': results.get('bank_statement_summary') or bank_statement,
            'analysis': results.get('smart_model_summary', {}).get('detailed_analysis', [])
        }
        # Ensure all expected fields are present in monthly_log
        for key in [
            'income', 'fixed_expenses', 'reducible_expenses', 'optimized_expenses',
            'emi_plans', 'selected_emis', 'balance', 'savings_rate', 'alerts',
            'tips', 'investment_suggestions', 'summary', 'analysis']:
            if key not in monthly_log or monthly_log[key] is None:
                if key in ['fixed_expenses', 'reducible_expenses', 'optimized_expenses', 'emi_plans', 'selected_emis', 'alerts', 'tips', 'investment_suggestions', 'analysis']:
                    monthly_log[key] = []
                elif key in ['income', 'balance', 'savings_rate']:
                    monthly_log[key] = 0
                else:
                    monthly_log[key] = ""
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(monthly_log, f, indent=2, ensure_ascii=False)

        return jsonify({
            'success': True,
            'results': results,
            'filename': filename
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/past_reports')
@login_required
def api_past_reports():
    username = session['username']
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    user_dir = os.path.join(data_dir, username)
    logs = []
    if os.path.exists(user_dir):
        files = sorted([f for f in os.listdir(user_dir) if f.endswith('.json')], reverse=True)
        for f in files[:6]:
            with open(os.path.join(user_dir, f), 'r', encoding='utf-8') as fp:
                log = json.load(fp)
                # Compose summary for table/charts
                # Extract timestamp from filename for display
                ts = f.replace(f'{username}_','').replace('.json','')
                total_expenses = sum(e['amount'] for e in log.get('fixed_expenses',[])) + sum(e['amount'] for e in log.get('reducible_expenses',[]))
                category_expenses = {}
                for e in log.get('fixed_expenses',[]) + log.get('reducible_expenses',[]):
                    cat = e.get('category','Other')
                    category_expenses[cat] = category_expenses.get(cat,0) + e.get('amount',0)
                top_categories = sorted(category_expenses, key=category_expenses.get, reverse=True)[:2]
                logs.append({
                    'month': ts,
                    'total_expenses': total_expenses,
                    'balance': log.get('balance',0),
                    'savings_rate': log.get('savings_rate',0),
                    'top_categories': top_categories,
                    'category_expenses': category_expenses,
                    'analysis': log.get('analysis',[])
                })
        logs = list(reversed(logs))
    # If no logs, return empty logs
    return jsonify({'logs': logs})

@app.route('/api/financial_score')
@login_required
def api_financial_score():
    username = session['username']
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    user_dir = os.path.join(data_dir, username)
    logs = []
    if os.path.exists(user_dir):
        files = sorted([f for f in os.listdir(user_dir) if f.endswith('.json')], reverse=True)
        for f in files[:6]:
            with open(os.path.join(user_dir, f), 'r', encoding='utf-8') as fp:
                logs.append(json.load(fp))
        logs = list(reversed(logs))
    score = 0
    suggestions = []
    emoji = '⚠️'
    summary = 'Needs review.'
    # +25: Balance improving
    if len(logs) >= 2 and logs[-1]['balance'] > logs[-2]['balance']:
        score += 25
    else:
        suggestions.append('Try to improve your balance month over month.')
    # +25: Savings rate improving
    if len(logs) >= 2 and logs[-1]['savings_rate'] > logs[-2]['savings_rate']:
        score += 25
    else:
        suggestions.append('Try to improve your savings rate month over month.')
    # +25: Reduction in low-priority spending
    def low_priority_sum(log):
        return sum(e['amount'] for e in log.get('reducible_expenses',[]) if e.get('priority','Medium')=='Low')
    if len(logs) >= 2 and low_priority_sum(logs[-1]) < low_priority_sum(logs[-2]):
        score += 25
    else:
        suggestions.append('Reduce low-priority spending for a better score.')
    # +25: EMI <= 40% of income
    if logs and sum(e.get('emi',0) for e in logs[-1].get('emi_plans',[])) <= 0.4 * logs[-1]['income']:
        score += 25
    else:
        suggestions.append('Keep your total EMI below 40% of your income.')
    # +25: No overspending in last 3 logs
    overspending = any(l.get('balance',0)<0 for l in logs[-3:])
    if not overspending:
        score += 25
    else:
        suggestions.append('Avoid overspending to maintain a healthy balance.')
    # Cap score at 100
    score = min(score, 100)
    # Emoji/summary
    if score >= 100:
        emoji = '📈'
        summary = 'Excellent! Your finances are improving.'
    elif score >= 75:
        emoji = '🙂'
        summary = 'Good! Keep up the progress.'
    elif score >= 50:
        emoji = '📉'
        summary = 'Caution: Some areas need attention.'
    else:
        emoji = '⚠️'
        summary = 'Risky: Take action to improve your finances.'
    return jsonify({'score': score, 'emoji': emoji, 'summary': summary, 'suggestions': suggestions})

@app.route('/api/download_report')
@login_required
def api_download_report():
    username = session['username']
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    results_dir = os.path.join(data_dir, 'results')
    if not os.path.exists(results_dir):
        return make_response('No report found (results folder missing).', 404)
    user_files = sorted([f for f in os.listdir(results_dir) if f.startswith(username)], reverse=True)
    if user_files:
        latest = user_files[0]
        return send_file(os.path.join(results_dir, latest), as_attachment=True, download_name=f"{username}_{datetime.now().strftime('%Y_%m')}_analysis.json")
    return make_response('No report found.', 404)

if __name__ == '__main__':
    app.run(debug=True) 