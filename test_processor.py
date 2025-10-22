import pytest
import pandas as pd
from processor import load_config, main  # Import our own functions

def test_full_pipeline(tmp_path):
    """
    A test that runs the entire pipeline from start to finish
    and checks the output file.
    """
    
    # --- 1. ARRANGE ---
    # Load our *real* config file
    config = load_config("config.yml")
    
    # Create a new, temporary output path *for this test*
    # `tmp_path` is a special 'fixture' from pytest
    test_output_dir = tmp_path / "test_output"
    test_output_dir.mkdir()
    test_output_file = test_output_dir / "test_results.csv"
    
    # *Override* the output path in our config to use the temporary one
    config['file_paths']['output_file'] = str(test_output_file)

    # --- 2. ACT ---
    # Run our main processing function, giving it our modified config
    main(config_override=config)

    # --- 3. ASSERT ---
    # Now, we check the results
    
    # Check that the output file was actually created
    assert test_output_file.exists(), "The output CSV file was not created."
    
    # Read the CSV file our script just made
    df_output = pd.read_csv(test_output_file)
    
    # Check that it has the correct number of rows
    assert len(df_output) == 96, "Output file does not have 96 rows."
    
    # Check for a specific, known value
    # Let's check the metadata for the first well (A01, index 0)
    # Note: Adjust 'Antibody_1' if your test data is different!
    assert df_output.loc[0, 'Antibody'] == 'Antibody_1', "Data in well A01 is incorrect."
    assert df_output.loc[0, 'Experimenter'] == 'SS', "Experimenter metadata is incorrect."