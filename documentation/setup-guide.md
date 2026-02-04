# Setup Guide

Complete setup instructions for running the Epidemiology AI project.

## Prerequisites

### System Requirements

- **Operating System**: Windows 10/11, macOS, or Linux
- **RAM**: Minimum 8GB (16GB recommended for large datasets)
- **Python**: Version 3.11 or higher
- **Disk Space**: At least 5GB free

### Required Software

1. **Python 3.11+**
   - Download from: https://www.python.org/downloads/
   - **Important**: Check "Add Python to PATH" during installation

2. **Git** (optional, for version control)
   - Download from: https://git-scm.com/downloads

3. **Code Editor** (recommended)
   - VS Code: https://code.visualstudio.com/
   - Or Jupyter: `pip install jupyter`

## Installation Steps

### 1. Clone/Download the Repository

If using Git:

```bash
git clone <repository-url>
cd "Epidemiology AI"
```

Or download and extract the ZIP file.

### 2. Create Virtual Environment

**Windows (PowerShell):**

```powershell
cd "d:\Projects\Epidemiology AI"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
cd ~/Projects/Epidemiology\ AI
python3 -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` in your terminal prompt.

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:

- FastAPI & Uvicorn (web framework)
- Pandas & NumPy (data processing)
- Scikit-learn & XGBoost (machine learning)
- Matplotlib & Seaborn (visualization)
- And other dependencies

**Installation time**: 5-10 minutes depending on internet speed.

### 4. Verify Installation

```bash
python -c "import pandas, numpy, sklearn, xgboost; print('All packages installed successfully!')"
```

You should see: `All packages installed successfully!`

### 5. Set Up Environment Variables (Optional)

Create a `.env` file in the project root:

```bash
# .env file
DATABASE_URL=postgresql://user:password@localhost:5432/epidemiology_ai
API_KEY=your_api_key_here
ENVIRONMENT=development
```

This is optional for the prototype but required for production deployment.

### 6. Create Data Directories

```bash
mkdir -p data/raw/dengue data/raw/weather data/processed data/models
```

Or manually create these folders:

- `data/raw/dengue/`
- `data/raw/weather/`
- `data/processed/`
- `data/models/`

### 7. Download Sample Data (Optional)

Follow the [Data Acquisition Guide](data-guide.md) to download dengue and weather datasets.

For quick testing, the prototype can generate synthetic data automatically.

## Running the Project

### Option 1: Run the Prototype Demo

```bash
python main.py
```

This runs the core outbreak prediction prototype with synthetic data.

### Option 2: Run the Jupyter Notebook

```bash
jupyter notebook
```

Then navigate to `notebooks/dengue_outbreak_prediction.ipynb` and run all cells.

### Option 3: Run the FastAPI Backend

```bash
cd src
uvicorn main:app --reload
```

Access the API at: http://localhost:8000
Interactive docs: http://localhost:8000/docs

## Troubleshooting

### "Python not found"

- **Windows**: Reinstall Python and check "Add to PATH"
- **macOS/Linux**: Use `python3` instead of `python`

### "Permission denied" when activating venv (Windows)

Run PowerShell as Administrator and execute:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "Module not found" errors

Make sure virtual environment is activated:

- You should see `(.venv)` in terminal
- Reinstall requirements: `pip install -r requirements.txt`

### "Out of memory" when training models

- Reduce dataset size in notebook
- Use smaller `n_estimators` for XGBoost (e.g., 50 instead of 100)
- Close other applications

### Jupyter notebook won't open

Install Jupyter in your virtual environment:

```bash
pip install jupyter notebook
```

### FastAPI server won't start

- Check if port 8000 is in use: `netstat -an | findstr 8000`
- Use different port: `uvicorn main:app --port 8001`

## IDE Setup Recommendations

### VS Code Extensions

- Python (Microsoft)
- Jupyter (Microsoft)
- Pylance (Microsoft)
- Python Docstring Generator

### Jupyter Notebook

For better notebook experience:

```bash
pip install jupyter-contrib-nbextensions
jupyter contrib nbextension install --user
```

## Testing Your Setup

Run the test suite:

```bash
pytest tests/
```

All tests should pass. If any fail, check the error messages and ensure:

1. Virtual environment is activated
2. All dependencies are installed
3. Data directories exist

## Next Steps

Now that your environment is set up:

1. **Read**: [Data Acquisition Guide](data-guide.md)
2. **Download**: Sample dengue dataset
3. **Explore**: Run `notebooks/dengue_outbreak_prediction.ipynb`
4. **Experiment**: Modify models and features
5. **Build**: Start developing the full application

## Development Best Practices

### 1. Always Activate Virtual Environment

Before working:

```bash
.\.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate      # macOS/Linux
```

### 2. Keep Dependencies Updated

```bash
pip list --outdated
pip install --upgrade <package-name>
```

### 3. Use Version Control

```bash
git add .
git commit -m "Your commit message"
git push
```

### 4. Document Your Changes

Update README.md and documentation as you develop new features.

## Additional Resources

- **FastAPI Tutorial**: https://fastapi.tiangolo.com/tutorial/
- **Pandas Documentation**: https://pandas.pydata.org/docs/
- **Scikit-learn Guide**: https://scikit-learn.org/stable/user_guide.html
- **XGBoost Documentation**: https://xgboost.readthedocs.io/

## Getting Help

If you encounter issues:

1. Check this troubleshooting section
2. Search project documentation in `documentation/` folder
3. Check error logs
4. Create an issue in the repository

## System Verification Checklist

- [ ] Python 3.11+ installed
- [ ] Virtual environment created and activated
- [ ] All requirements installed successfully
- [ ] Data directories created
- [ ] Can run `python main.py` without errors
- [ ] (Optional) Jupyter notebook opens
- [ ] (Optional) FastAPI server starts

Once all items are checked, you're ready to start developing!
