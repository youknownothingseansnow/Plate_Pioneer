import pandas as pd
import os
import yaml  # <-- New import

print("Starting plate processing (v2 - Config-Driven)...")

# --- 1. NEW: CONFIGURATION LOADING ---
def load_config(config_path="config.yml"):
    """Loads the YAML configuration file."""
    print(f"Loading configuration from {config_path}...")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

# --- 2. EXISTING LOGIC (MOVED INTO A FUNCTION) ---
def melt_plate(df, value_name):
    """Melts an 8x12 plate grid into a 96-row long format."""
    df.index = [chr(ord('A') + i) for i in range(8)]
    df_melted = df.reset_index().melt(id_vars='index', var_name='Col', value_name=value_name)
    df_melted = df_melted.rename(columns={'index': 'Row'})
    df_melted['Col'] = df_melted['Col'] + 1
    return df_melted

# --- 3. NEW: MAIN FUNCTION ---
def main(config_override=None):
    if config_override:
        config = config_override
        print("Using overridden config for testing.")
    else:
        config = load_config()
    """Main function to run the entire processing pipeline."""

    # --- Use config values instead of hard-coded strings ---
    paths = config['file_paths']
    sheets = config['sheet_names']

    input_file = paths['input_file']
    output_file = paths['output_file']
    
    # --- 2. READ ALL 4 SHEETS (using config) ---
    print(f"Loading data from {input_file}...")
    df_meta = pd.read_excel(input_file, sheet_name=sheets['metadata'], header=None)
    df_results = pd.read_excel(input_file, sheet_name=sheets['results'], header=None)
    df_antibodies = pd.read_excel(input_file, sheet_name=sheets['antibodies'], header=None)
    df_concentrations = pd.read_excel(input_file, sheet_name=sheets['concentrations'], header=None)

    # --- 3. PROCESS THE METADATA (no change) ---
    meta_dict = df_meta.set_index(0)[1].to_dict()
    print(f"Loaded metadata for Experimenter: {meta_dict.get('Experimenter')}")

    # --- 4. "MELT" THE PLATE GRIDS (no change) ---
    print("Melting plate data...")
    results_long = melt_plate(df_results, "Result_Value")
    antibodies_long = melt_plate(df_antibodies, "Antibody")
    concentrations_long = melt_plate(df_concentrations, "Concentration")

    # --- 5. MERGE THE MELTED DATA (no change) ---
    df_tidy = results_long
    df_tidy = pd.merge(df_tidy, antibodies_long, on=['Row', 'Col'])
    df_tidy = pd.merge(df_tidy, concentrations_long, on=['Row', 'Col'])

    # --- 6. ADD METADATA TO EVERY ROW (no change) ---
    print("Adding experiment metadata...")
    for key, value in meta_dict.items():
        df_tidy[key] = value

    # --- 7. SAVE THE FINAL CSV (using config) ---
    df_tidy.to_csv(output_file, index=False)
    print(f"Success! Tidy data saved to: {output_file}")


# --- 4. NEW: SCRIPT EXECUTION BLOCK ---
if __name__ == "__main__":
    main()