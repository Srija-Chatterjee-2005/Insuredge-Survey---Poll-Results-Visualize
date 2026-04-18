def generate_insights(avg_ratings):
    print("\n🔍 KEY INSIGHTS")

    for col, val in avg_ratings.items():
        print(f"✔ {col}: {val:.2f}")

    print("\n🎯 SUMMARY:")
    print(f"✔ Highest Rated Feature: {avg_ratings.idxmax()}")
    print(f"✔ Lowest Rated Feature: {avg_ratings.idxmin()}")