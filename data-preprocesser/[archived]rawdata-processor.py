import os
import pandas as pd
import csv
from pathlib import Path
from collections import defaultdict
import io

def save_error_rows(error_rows, headers, output_dir):
    """Save error rows to a CSV file with headers and source file information"""
    error_file = output_dir / "error-data.csv"
    
    # Add source_file and error_type to headers
    error_headers = list(headers) + ['source_file', 'error_type', 'row_number']
    
    # Create or append to error file
    mode = 'a' if error_file.exists() else 'w'
    with open(error_file, mode, encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        # Write headers only if creating new file
        if mode == 'w':
            writer.writerow(error_headers)
        # Write error rows
        for row_data in error_rows:
            writer.writerow(row_data)
    
    return error_file

def fix_csv_file(file_path, encoding='utf-8'):
    """Fix CSV files with quote/delimiter issues by reading and writing with csv module"""
    try:
        # Read the original file
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            content = f.read()
        
        # Create a string buffer
        output = io.StringIO()
        
        # Read the content as CSV and write it back properly quoted
        csv_reader = csv.reader(io.StringIO(content))
        csv_writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        
        # Get the expected number of columns from the first row
        header = next(csv_reader)
        expected_columns = len(header)
        csv_writer.writerow(header)
        
        # Store error rows for later saving
        error_rows = []
        
        # Process remaining rows
        for row_idx, row in enumerate(csv_reader, 2):  # Start from 2 as 1 is header
            if len(row) != expected_columns:
                # Pad row with None to match header length
                padded_row = row + [None] * (expected_columns - len(row))
                # Trim row if too long
                padded_row = padded_row[:expected_columns]
                # Add source file and error information
                error_row = padded_row + [
                    str(file_path),
                    f"Wrong column count (expected {expected_columns}, got {len(row)})",
                    row_idx
                ]
                error_rows.append(error_row)
                continue
            csv_writer.writerow(row)
        
        # Save error rows if any
        if error_rows:
            error_file = save_error_rows(error_rows, header, file_path.parent)
            print(f"\n  ! Saved {len(error_rows)} problematic rows to {error_file}")
        
        # Return the fixed content as a string buffer
        output.seek(0)
        return output
        
    except Exception as e:
        print(f"  ✗ Error fixing CSV file: {e}")
        # Try to save the entire file content as error data if possible
        try:
            error_rows = [[str(file_path), f"File parsing error: {str(e)}", 0]]
            error_file = save_error_rows(error_rows, [], file_path.parent)
            print(f"  ! Saved error information to {error_file}")
        except Exception as save_error:
            print(f"  ✗ Could not save error information: {save_error}")
        return None

def analyze_and_combine_csv_files():
    print("\n=== Starting CSV Analysis and Combination Process ===")
    
    # Get the property-infos directory and verify it exists
    property_infos_dir = Path("property-infos")
    if not property_infos_dir.exists():
        print(f"Error: Directory not found: {property_infos_dir.absolute()}")
        return
    
    # Initialize error data file
    error_file = property_infos_dir / "error-data.csv"
    if error_file.exists():
        print(f"Found existing error-data.csv, will append new errors to it")
    
    # Initialize dictionaries to store header types and corresponding dataframes
    header_types = defaultdict(list)  # Will store file paths for each header type
    header_samples = {}  # Will store a sample of each unique header type
    problem_files = []  # Store files with inconsistent columns
    
    # Counter for progress tracking
    total_files_processed = 0
    total_files_failed = 0
    
    # First pass: Analyze headers
    print("\n=== Phase 1: Analyzing CSV Headers ===")
    
    # Get all subdirectories first
    folders = [f for f in property_infos_dir.iterdir() if f.is_dir()]
    total_folders = len(folders)
    
    print(f"Found {total_folders} folders to process")
    
    for folder_idx, folder in enumerate(folders, 1):
        print(f"\nScanning folder [{folder_idx}/{total_folders}]: {folder.relative_to(property_infos_dir)}")
        
        csv_files = list(folder.glob("*.csv"))
        total_files = len(csv_files)
        
        if total_files == 0:
            print(f"  No CSV files found in {folder.name}")
            continue
        
        for file_idx, csv_file in enumerate(csv_files, 1):
            try:
                print(f"  Reading file [{file_idx}/{total_files}]: {csv_file.name}", end='\r')
                
                # Try to read the file with error handling
                try:
                    # First try with standard reading
                    df = pd.read_csv(csv_file, encoding='utf-8', nrows=0)
                except UnicodeDecodeError:
                    # Try with different encoding
                    df = pd.read_csv(csv_file, encoding='big5', nrows=0)
                except (pd.errors.EmptyDataError, pd.errors.ParserError) as e:
                    if "EOF inside string" in str(e) or "Error tokenizing data" in str(e):
                        print(f"\n  ! Attempting to fix file format: {csv_file.name}")
                        # Try to fix the file format
                        try:
                            fixed_content = fix_csv_file(csv_file, encoding='utf-8')
                            if fixed_content is not None:
                                df = pd.read_csv(fixed_content, dtype=str)
                            else:
                                fixed_content = fix_csv_file(csv_file, encoding='big5')
                                if fixed_content is not None:
                                    df = pd.read_csv(fixed_content, dtype=str)
                                else:
                                    raise Exception("Failed to fix file format")
                        except Exception as fix_error:
                            print(f"  ✗ Error: {csv_file.name} could not be fixed: {fix_error}")
                            total_files_failed += 1
                            continue
                    else:
                        print(f"  ✗ Error: {csv_file.name} is empty or invalid")
                        total_files_failed += 1
                        continue
                
                # Create a tuple of column names for comparison
                headers = tuple(df.columns)
                
                # Store file path under this header type
                header_types[headers].append(csv_file)
                
                # Store a sample of the header if we haven't seen it before
                if headers not in header_samples:
                    header_samples[headers] = csv_file.name
                
                total_files_processed += 1
                
            except Exception as e:
                print(f"  ✗ Error processing {csv_file.name}: {e}")
                total_files_failed += 1
    
    # Report findings
    print("\n\n=== Header Analysis Results ===")
    print(f"Found {len(header_types)} different header types:")
    for idx, (headers, files) in enumerate(header_types.items(), 1):
        print(f"\nType {idx}:")
        print(f"Sample file: {header_samples[headers]}")
        print(f"Headers: {', '.join(headers)}")
        print(f"Number of files: {len(files)}")
    
    if problem_files:
        print("\n=== Files with Inconsistent Columns ===")
        for file, error in problem_files:
            print(f"File: {file.name}")
            print(f"Error: {error}")
    
    # Ask user if they want to proceed with combination
    while True:
        response = input("\nWould you like to combine files with matching headers? (y/n): ").lower()
        if response in ['y', 'n']:
            break
    
    if response == 'y':
        print("\n=== Phase 2: Combining Files ===")
        for idx, (headers, files) in enumerate(header_types.items(), 1):
            print(f"\nProcessing group {idx} ({len(files)} files)...")
            all_dataframes = []
            
            for csv_file in files:
                try:
                    try:
                        df = pd.read_csv(csv_file, encoding='utf-8', 
                                       low_memory=False, 
                                       dtype=str)
                    except (UnicodeDecodeError, pd.errors.ParserError) as e:
                        if "EOF inside string" in str(e) or "Error tokenizing data" in str(e):
                            print(f"  ! Attempting to fix file format: {csv_file.name}")
                            fixed_content = fix_csv_file(csv_file, encoding='utf-8')
                            if fixed_content is not None:
                                df = pd.read_csv(fixed_content, dtype=str)
                            else:
                                fixed_content = fix_csv_file(csv_file, encoding='big5')
                                if fixed_content is not None:
                                    df = pd.read_csv(fixed_content, dtype=str)
                                else:
                                    raise Exception("Failed to fix file format")
                        else:
                            df = pd.read_csv(csv_file, encoding='big5', 
                                           low_memory=False, 
                                           dtype=str)
                    
                    df['source_file'] = str(csv_file.relative_to(property_infos_dir))
                    all_dataframes.append(df)
                    print(f"  ✓ Added: {csv_file.name}")
                except Exception as e:
                    print(f"  ✗ Error processing {csv_file.name}: {e}")
            
            if all_dataframes:
                # Combine all dataframes of this type
                combined_df = pd.concat(all_dataframes, ignore_index=True)
                
                # Create a descriptive filename based on the first file in the group
                sample_name = Path(header_samples[headers]).stem
                output_path = property_infos_dir / f"combined_{sample_name}_group{idx}.csv"
                
                try:
                    combined_df.to_csv(output_path, index=False, encoding='utf-8')
                    print(f"  ✓ Combined CSV saved to: {output_path}")
                    print(f"  ✓ Total rows: {len(combined_df)}")
                except Exception as e:
                    print(f"  ✗ Error saving combined file: {e}")
    
    print("\n=== Process Complete ===")
    print(f"Total files processed: {total_files_processed}")
    print(f"Total files failed: {total_files_failed}")
    if problem_files:
        print(f"Files with inconsistent columns: {len(problem_files)}")

if __name__ == "__main__":
    analyze_and_combine_csv_files()