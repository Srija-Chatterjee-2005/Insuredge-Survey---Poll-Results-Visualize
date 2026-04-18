from src.data_loader import load_data
from src.data_cleaning import clean_data
from src.analysis import get_usage_counts, get_average_ratings, calculate_nps
from src.visualization import plot_bar, plot_histogram, plot_count, plot_ratings, plot_wordcloud
from src.insights import generate_insights

print("🚀 Starting Project...")

# -----------------------------
# LOAD + CLEAN
# -----------------------------
df = load_data("data/OIMS(gform_responses).csv")
df = clean_data(df)

print("✅ Data Loaded")

# -----------------------------
# ANALYSIS
# -----------------------------
usage_col = 'How often do you use our online insurance management system?'

rating_cols = [
    'How would you rate the overall ease of use of our online system?',
    'How would you rate the speed and performance of the online system?',
    'How would you rate your experience with making premium payments online?',
    'How satisfied were you with customer service interactions (agent or chatbot)?',
    'How likely are you to recommend our insurance services to a friend or colleague?'
]

rec_col = rating_cols[-1]

usage = get_usage_counts(df, usage_col)
avg_ratings = get_average_ratings(df, rating_cols)

print("📊 Analysis Done")

# -----------------------------
# VISUALIZATION
# -----------------------------
plot_bar(usage, "Usage Frequency", "usage.png")
print("✔ Usage chart done")

plot_histogram(df, rec_col, "recommendation.png")
print("✔ Recommendation chart done")

plot_count(df, 'Age', "age.png")
print("✔ Age chart done")

plot_ratings(avg_ratings, "ratings_comparison.png")
print("✔ Ratings comparison done")

# -----------------------------
# WORD CLOUD
# -----------------------------
feedback_col = [col for col in df.columns if "suggest" in col.lower() or "feedback" in col.lower()]

if feedback_col:
    plot_wordcloud(df, feedback_col[0], "wordcloud.png")
    print("✔ Wordcloud done")
else:
    print("⚠️ No feedback column found")

# -----------------------------
# NPS
# -----------------------------
nps_score = calculate_nps(df, rec_col)
print(f"\n🔥 NPS Score: {nps_score:.2f}")

# -----------------------------
# INSIGHTS
# -----------------------------
generate_insights(avg_ratings)

print("🎯 Project Completed")