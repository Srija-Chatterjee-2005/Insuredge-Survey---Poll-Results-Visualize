import matplotlib.pyplot as plt
import seaborn as sns
import os

def plot_bar(data, title, filename):
    os.makedirs("images", exist_ok=True)  # 🔥 auto-create folder
    plt.figure()
    data.plot(kind='bar')
    plt.title(title)
    plt.savefig(f"images/{filename}")
    plt.show()

def plot_histogram(df, column, filename):
    plt.figure()
    sns.histplot(df[column], bins=5)
    plt.title("Recommendation Score Distribution")
    plt.savefig(f"images/{filename}")
    plt.show()

def plot_count(df, column, filename):
    plt.figure()
    sns.countplot(x=column, data=df)
    plt.title(f"{column} Distribution")
    plt.savefig(f"images/{filename}")
    plt.show()

# 🔥 NEW: multiple rating comparison
def plot_ratings(avg_ratings, filename):
    plt.figure()
    avg_ratings.plot(kind='bar')
    plt.title("Average Ratings Comparison")
    plt.xticks(rotation=45)
    plt.savefig(f"images/{filename}")
    plt.show()

from wordcloud import WordCloud
import os
import matplotlib.pyplot as plt

def plot_wordcloud(df, column, filename):
    os.makedirs("images", exist_ok=True)

    text = " ".join(df[column].dropna().astype(str))

    if text.strip() == "":
        print("⚠️ No text available for wordcloud")
        return

    wc = WordCloud(width=800, height=400, background_color='white').generate(text)

    plt.figure()
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    plt.title("Feedback Word Cloud")
    plt.savefig(f"images/{filename}")
    plt.show()