import pandas as pd

def get_usage_counts(df, column):
    return df[column].value_counts()

def get_average_ratings(df, rating_cols):
    for col in rating_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df[rating_cols].mean()

def calculate_nps(df, column):
    promoters = df[df[column] >= 9].shape[0]
    detractors = df[df[column] <= 6].shape[0]
    total = df.shape[0]

    if total == 0:
        return 0

    nps = ((promoters - detractors) / total) * 100
    return nps