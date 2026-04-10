# Dashboard Leap - Data Analytics Platform

## Overview

Dashboard Leap is a comprehensive data analytics platform that provides end-to-end data processing, machine learning, and interactive visualization capabilities. The platform integrates traditional data science workflows with modern AI-powered insights.

## Features

### Data Processing Pipeline

- **Data Loading**: Support for CSV, Excel, API, and database sources
- **Data Cleaning**: Automated handling of missing values, duplicates, and outliers
- **Data Transformation**: Feature engineering, scaling, and encoding
- **Data Validation**: Comprehensive data quality checks

### Machine Learning

- **Model Training**: Support for classification and regression tasks
- **Model Evaluation**: Automated performance metrics and validation
- **Model Deployment**: Easy model saving and loading for predictions
- **Feature Selection**: Automated feature importance analysis

### Visualization

- **Static Plots**: High-quality matplotlib and seaborn visualizations
- **Interactive Dashboards**: Plotly-based interactive visualizations
- **Automated Reporting**: Generate comprehensive visual reports

### AI Integration

- **LLM Analysis**: Google Gemini-powered data insights
- **Automated Insights**: AI-generated analysis and recommendations
- **Natural Language Queries**: Ask questions about your data in plain English

## Project Structure

```
dashboard_leap/
├── main.py                 # Entry point
├── app/
│   └── app.py             # Streamlit dashboard
├── src/
│   ├── api/
│   │   └── fetch.py       # API and database connections
│   ├── data/
│   │   ├── loader.py      # Data loading utilities
│   │   ├── cleaner.py     # Data cleaning functions
│   │   └── transformer.py # Data transformation
│   ├── models/
│   │   ├── train.py       # Model training
│   │   └── predict.py     # Model predictions
│   ├── visualization/
│   │   ├── plot.py        # Static plots
│   │   └── interactive.py # Interactive plots
│   └── llm/
│       └── agent.py       # LLM integration
├── config/
│   └── db.yaml            # Configuration file
├── data/
│   ├── raw/               # Raw data files
│   ├── processed/         # Processed data
│   └── staging/           # Intermediate data
├── notebooks/
│   └── eda.ipynb          # Exploratory analysis
├── reports/
│   └── figures/           # Generated plots
└── requirements.txt       # Python dependencies
```

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd dashboard_leap
```

2. Create virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure API keys in `config/db.yaml`

## Usage

### Running the Dashboard

```bash
python main.py
```

This will launch the Streamlit dashboard where you can:

- Upload and explore data
- Perform automated data cleaning and transformation
- Train machine learning models
- Generate interactive visualizations
- Ask AI-powered questions about your data

### Using Individual Modules

```python
from src.data.loader import load_data
from src.data.cleaner import clean_data
from src.models.train import train_model_pipeline

# Load and clean data
data = load_data()
cleaned_data = clean_data(data)

# Train a model
results = train_model_pipeline(cleaned_data, target_col='target_column')
```

## Configuration

Edit `config/db.yaml` to configure:

- Database connections
- API endpoints and keys
- Model parameters

## Data Flow

1. **Data Ingestion**: Load data from various sources
2. **Data Cleaning**: Handle missing values, outliers, and inconsistencies
3. **Feature Engineering**: Create new features and transform existing ones
4. **Model Training**: Train ML models on prepared data
5. **Model Evaluation**: Assess model performance and select best models
6. **Visualization**: Create interactive dashboards and reports
7. **AI Analysis**: Generate insights using LLM integration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues, please open an issue on the GitHub repository.
