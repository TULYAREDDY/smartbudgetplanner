# Smart Budget Planner

A comprehensive Flask-based web application for personal financial optimization, featuring AI-powered advice, expense tracking, EMI planning, and machine learning models for smart expense forecasting.

## Features

- **User Authentication**: Secure login and registration system
- **Financial Analysis**: Comprehensive expense categorization and optimization
- **AI-Powered Insights**: Gemini AI integration for personalized financial advice
- **EMI Optimization**: Dynamic programming-based EMI plan selection
- **Expense Forecasting**: Machine learning models for predictive analytics
- **Bank Statement Integration**: Import and analyze bank transaction data
- **Progress Tracking**: Historical financial score and trend analysis
- **Report Generation**: Downloadable JSON reports of financial analysis
- **Responsive UI**: Bootstrap-based modern web interface

## Tech Stack

- **Backend**: Python Flask
- **AI/ML**: Google Generative AI (Gemini), Scikit-learn, Pandas
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Database**: JSON-based storage (file system)
- **Deployment**: Ready for Docker/Gunicorn

## Folder Structure

```
smartbudgetplanner/
├── app/                          # Main application package
│   ├── __init__.py
│   ├── app.py                    # Flask application and routes
│   └── logic/                    # Business logic modules
│       ├── __init__.py
│       ├── backtrack_expenses.py # Backtracking optimization
│       ├── decision_tree_advice.py # Decision tree recommendations
│       ├── dp_emi_selector.py    # Dynamic programming EMI selection
│       └── greedy_optimizer.py   # Greedy algorithm optimization
├── data/                         # Data storage
│   ├── bank/                     # Bank statement JSON files
│   ├── results/                  # Analysis results and reports
│   └── users/                    # User profiles and data
├── ml_models/                    # Machine learning models
│   └── Random_Forest_Smart_Expense_Forecasting_Model.ipynb
├── static/                       # Static assets
│   ├── script.js                 # Frontend JavaScript
│   └── style.css                 # Custom CSS styles
├── templates/                    # Jinja2 templates
│   ├── index.html                # Main application page
│   └── login.html                # Authentication page
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
├── README.md                     # Project documentation
├── requirements.txt              # Python dependencies
└── run.py                        # Application entry point
```

## Installation

### Prerequisites

- Python 3.8+
- pip package manager
- Google Cloud API key (for AI features)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd smartbudgetplanner
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

6. **Access the application**
   Open http://localhost:5000 in your browser

## Usage

1. **Register/Login**: Create an account or login with existing credentials
2. **Input Financial Data**: Enter monthly salary, expenses, and EMI plans
3. **Upload Bank Statement**: (Optional) Upload JSON bank statement for enhanced analysis
4. **Run Analysis**: Click analyze to get optimization recommendations
5. **View Results**: Review AI-powered advice, optimized expenses, and savings projections
6. **Track Progress**: Monitor financial health score over time
7. **Download Reports**: Export analysis results as JSON files

## API Endpoints

- `GET /` - Main application page
- `GET/POST /login` - User authentication
- `POST /analyze` - Financial analysis
- `GET /api/past_reports` - Historical analysis data
- `GET /api/financial_score` - Financial health score
- `GET /api/download_report` - Download latest report

## Future Improvements

- Database integration (PostgreSQL/MongoDB)
- Real-time expense tracking via mobile app
- Advanced ML models for personalized recommendations
- Multi-currency support
- Integration with banking APIs
- Automated expense categorization
- Budget goal setting and notifications
- Export to PDF/Excel formats
- User dashboard with charts and graphs
- API rate limiting and security enhancements

## Contribution Guidelines

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation for API changes
- Ensure all tests pass before submitting PR

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions or support, please open an issue on GitHub.
