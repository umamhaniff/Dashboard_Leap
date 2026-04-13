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
├── app.py                 # Streamlit dashboard entry point
├── config/
│   └── settings.py        # Configuration for Google Sheets, GCP, app settings
├── core/
│   ├── data_pipeline.py   # Data ingestion and cleaning
│   ├── llm_analyzer.py    # Gemini AI security analysis
│   └── charts.py          # Plotly visualization helpers
├── styles/
│   └── style.css          # Shared CSS for the dashboard
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

4. Configure API keys in `config/settings.py` or `.streamlit/secrets.toml`

## Usage

### Running the Dashboard

```bash
python app.py
```

Atau:

```bash
streamlit run app.py
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

Edit `config/settings.py` to configure:

- Google Sheets URL/ID
- Service account path
- Sheet names
- Project ID and app settings

For secret overrides, use `.streamlit/secrets.toml`.

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
