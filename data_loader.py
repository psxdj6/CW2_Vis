import pandas as pd
from config import (AGGREGATED_DATA_FILE, DIET_ORDER, GENDER_CATEGORIES, AGE_CATEGORIES)

def load_preprocess_data(path=AGGREGATED_DATA_FILE):
    
    # read CSV
    df = pd.read_csv(path)

    # check required
    required = ["diet", "gender", "age_group", "participants"]

    # set categories
    df["diet"]      = pd.Categorical(df["diet"],      DIET_ORDER,       ordered=True)
    df["gender"]    = pd.Categorical(df["gender"],    GENDER_CATEGORIES,ordered=True)
    df["age_group"] = pd.Categorical(df["age_group"], AGE_CATEGORIES,   ordered=True)

    # sort rows
    return df.sort_values(by=["diet", "gender", "age_group"])
