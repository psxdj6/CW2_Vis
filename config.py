import plotly.express as px

# data file
AGGREGATED_DATA_FILE = "Aggregated_Data.csv"

# categories
DIET_ORDER = ["vegan", "vegetarian", "fish", "meat low", "meat medium", "meat high", "All"]
GENDER_CATEGORIES = ["female", "male", "All"]
AGE_CATEGORIES = ["20-29", "30-39", "40-49","50-59", "60-69", "70-79", "All"]

# layers
AVAILABLE_LAYERS = ["diet", "gender", "age_group"]

# indicators
BASE_INDICATOR_OPTIONS_MAP = {
    "ghgs": "GHGs",
    "land": "Land Use",
    "water_use": "Water Use",
    "eut": "Eutrophication",
    "bio": "Biodiversity Loss"}

# defaults
DEFAULT_INDICATOR = "ghgs"
DEFAULT_LAYERS    = ["diet"]

# styling
color_SCALE     = px.colors.diverging.RdYlGn_r
ROOT_color      = "lightgray"
HIGHLIGHT_COLOR = "lightblue"
LINE_color      = "white"
LINE_WIDTH      = 1.5
