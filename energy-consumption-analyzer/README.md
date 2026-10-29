# ⚡ Energy Consumption Analyzer

A beginner-friendly Electrical Engineering + data analysis project that estimates appliance-level electricity consumption and cost.

## Features

- Calculate daily and 30-day energy consumption in kWh.
- Estimate electricity costs using a configurable rate (₹/kWh).
- Analyze multiple appliances and quantities.
- Upload your own CSV or use the included sample data.
- Edit appliance inputs interactively in the dashboard.
- Visualize appliance-level consumption and energy share.
- Download calculated results as a CSV file.
- Validate input data and show helpful error messages.

## Tech stack

- Python
- Streamlit
- pandas
- Matplotlib

## Electrical Engineering formula

Energy consumption is calculated as:

`Energy (kWh) = Power (W) × Quantity × Hours per day ÷ 1000`

Estimated daily cost:

`Daily cost (₹) = Daily energy (kWh) × Electricity rate (₹/kWh)`

The 30-day estimate assumes the same usage every day. Actual bills may include fixed charges, taxes, and tariff slabs.

## Project structure

```text
energy-consumption-analyzer/
├── app.py
├── data/
│   └── appliances.csv
├── requirements.txt
├── .gitignore
└── README.md
```

## Run locally

Python 3.10 or newer is recommended.

1. Open this folder in VS Code.
2. Open **Terminal → New Terminal**.
3. Create a virtual environment:

   **Windows**
   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, open a Command Prompt terminal and run:
   ```bat
   .venv\Scripts\activate.bat
   ```

4. Install the dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

5. Start the dashboard:

   ```bash
   python -m streamlit run app.py
   ```

6. Streamlit will show a local URL in the terminal, usually `http://localhost:8501`. Open it in your browser.

If `python` is not recognized, try using `py` in the commands where appropriate.

## CSV format

Your CSV needs these columns:

- `appliance` — name of the appliance
- `power_watts` — rated power in watts
- `hours_per_day` — typical daily operating hours (0–24)
- `quantity` — number of identical appliances (optional; defaults to 1)

Example:

```csv
appliance,power_watts,hours_per_day,quantity
Fan,75,8,2
LED Bulb,10,6,4
Laptop,65,5,1
```

## Limitations and future improvements

This project estimates consumption from rated power and operating hours; it does not measure live electrical power. Actual appliance power can vary. Future improvements could include dated smart-meter data, time-series analysis, and evaluation of a forecasting model.

## Learning goals

- Apply the electrical energy formula in code.
- Read and validate structured data.
- Summarize data with pandas.
- Create charts with Matplotlib.
- Build a small interactive data application.
- Use Git and GitHub to version and share a project.

## License

This project is shared under the MIT License. See `LICENSE`.
