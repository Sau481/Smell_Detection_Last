import pandas as pd
import os

def merge_datasets():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_folder = os.path.join(BASE_DIR, "dataset")

    long_method_file = os.path.join(dataset_folder, "longmethod_smell.csv")
    large_class_file = os.path.join(dataset_folder, "largeclass_smell.csv")
    merged_file = os.path.join(dataset_folder, "merged_dataset.csv")

    df_long = pd.read_csv(long_method_file)
    df_large = pd.read_csv(large_class_file)

    df_long["smell_type"] = "LongMethod"
    df_large["smell_type"] = "LargeClass"

    merged = pd.concat([df_long, df_large], ignore_index=True, sort=False)

    # Put smell type last
    cols = [c for c in merged.columns if c != "smell_type"] + ["smell_type"]
    merged = merged[cols]

    merged.to_csv(merged_file, index=False)
    print("Done:", merged_file)

if __name__ == "__main__":
    merge_datasets()
