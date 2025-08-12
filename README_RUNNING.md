# How to Run the Decision Table Project

## Quick Start

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or source venv/bin/activate  # Mac/Linux
   ```

2. **Install dependencies:**
   ```bash
   pip install pytest
   ```

3. **Run tests:**
   ```bash
   python -m pytest tests/ -v
   ```

## Using the Decision Table

```python
from pathlib import Path
from app.models.decision_data_holder import DecisionDataHolder
from app.models.decision_table import DecisionTable

# Load decision rules from CSV
decision_table = DecisionTable.create_from_csv(
    Path("tests/resources/decision_tables/scoring_process_result.csv")
)

# Create input data
data = DecisionDataHolder({
    "hard_check_passed": True,
    "risk_score": 12,
    "all_data_collected": True
})

# Evaluate and get result
result = decision_table.evaluate(data)
print(f"Status: {data.get('status')}")  # Should print: Status: APPROVED
```

## What it does

The decision table reads rules from a CSV file and evaluates them against input data. It checks each rule row by row and applies the first matching rule.

Example CSV format:
```csv
hard_check_passed;risk_score;all_data_collected;*;status
=false;>-99999;=true;*;"REJECTED"
=true;>10;=true;*;"APPROVED"
```

## Troubleshooting

- Make sure you're in the project root directory
- Ensure virtual environment is activated
- Check that all tests pass: `python -m pytest tests/ -v`
