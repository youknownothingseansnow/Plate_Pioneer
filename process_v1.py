import pandas as pd
import os

print("Starting plate processing...")

# --- 1. DEFINE FILE PATHS ---
INPUT_FILE = os.path.join("data", "test_plate.xlsx")
OUTPUT_FILE = os.path.join("data", "output_tidy.csv")

# --- 2. READ ALL 4 SHEETS ---
# load each sheet into its own DataFrame.

# Read the metadata sheet
df_meta = pd.read_excel(INPUT_FILE, sheet_name="experiment_meta", header=None)

# Read the 3 plate layout sheets
df_results = pd.read_excel(INPUT_FILE, sheet_name="results", header=None)
df_antibodies = pd.read_excel(INPUT_FILE, sheet_name="ta_map", header=None)
df_concentrations = pd.read_excel(INPUT_FILE, sheet_name="concentration_map", header=None)

# --- 3. PROCESS THE METADATA ---
# Convert the 2-column sheet into a clean Python dictionary.
meta_dict = df_meta.set_index(0)[1].to_dict()
print(f"Loaded metadata for Experimenter: {meta_dict.get('Experimenter')}")

# --- 4. "MELT" THE PLATE GRIDS ---
# This is the key step, convert the 8x12 grids (wide) 
# into a 96-row list (long).

def melt_plate(df, value_name):
    # Add a 'Row' column (A-H) to match the well IDs
    df.index = [chr(ord('A') + i) for i in range(8)]
    # 'Melt' the DataFrame
    df_melted = df.reset_index().melt(id_vars='index', var_name='Col', value_name=value_name)
    # Rename 'index' to 'Row' for clarity
    df_melted = df_melted.rename(columns={'index': 'Row'})
    # Convert 'Col' from 0-based index to 1-based (1-12)
    df_melted['Col'] = df_melted['Col'] + 1
    return df_melted

print("Melting plate data...")
results_long = melt_plate(df_results, "Result_Value")
antibodies_long = melt_plate(df_antibodies, "Antibody")
concentrations_long = melt_plate(df_concentrations, "Concentration")

# --- 5. MERGE THE MELTED DATA ---
# Combine the three long DataFrames into one.

# Start with the main results
df_tidy = results_long

# Merge the antibody data
df_tidy = pd.merge(df_tidy, antibodies_long, on=['Row', 'Col'])

# Merge the concentration data
df_tidy = pd.merge(df_tidy, concentrations_long, on=['Row', 'Col'])

# --- 6. ADD METADATA TO EVERY ROW ---
# Add the info from our dictionary as new columns.
print("Adding experiment metadata...")
for key, value in meta_dict.items():
    df_tidy[key] = value

# --- 7. SAVE THE FINAL CSV ---
df_tidy.to_csv(OUTPUT_FILE, index=False)

print(f"Success! Tidy data saved to: {OUTPUT_FILE}")