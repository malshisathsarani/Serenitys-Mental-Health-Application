import pandas as pd
import glob

# Read all CSV files inside data/ folder
csv_files = glob.glob("data/*.csv")

dfs = []

for file in csv_files:
    print("Reading:", file)
    dfs.append(pd.read_csv(file))

# Combine all
combined_df = pd.concat(dfs, ignore_index=True)

# Save final dataset
combined_df.to_csv("dataset.csv", index=False)

print("Combined CSV saved as dataset.csv")
