
from pathlib import Path

# ==========================================
# 1. PROJECT INFORMATION
# ==========================================

PROJECT_NAME = "6M Mart"
PROJECT_TITLE = "Retail Intelligence & Performance Analytics"
CURRENCY = "PHP"

# ==========================================
# 2. DATE CONFIGURATION
# ==========================================

START_DATE = "2024-01-01"
END_DATE = "2025-12-31"

# ==========================================
# 3. DATASET CONFIGURATION
# ==========================================

RANDOM_SEED = 42

NUM_BRANCHES = 8
NUM_PRODUCTS = 120
NUM_SUPPLIERS = 15
NUM_PROMOTIONS = 15

# ==========================================
# 4. PROJECT DIRECTORIES
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = PROJECT_ROOT / "02_Raw_Data"
CLEANED_DATA_DIR = PROJECT_ROOT / "04_Cleaned_Data"

# ==========================================
# 5. SALES GENERATION SETTINGS
# ==========================================

SALES_LINE_COUNT = 120_000

RETURN_RATE = 0.02