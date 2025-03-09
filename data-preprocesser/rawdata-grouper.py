import os
import shutil
from pathlib import Path

def create_transaction_folders(base_path):
    """Create folders for different transaction types"""
    folders = {
        'a': 'property-sales',
        'b': 'pre-construction-sales',
        'c': 'property-rentals'
    }
    
    print("\n=== Creating Transaction Folders ===")
    for code, folder in folders.items():
        folder_path = os.path.join(base_path, folder)
        Path(folder_path).mkdir(parents=True, exist_ok=True)
        print(f"Created/Verified folder for {code}: {folder}")
    
    return folders

def get_transaction_type(filename):
    """Extract transaction type (a/b/c) from filename
    Example: a_lvr_land_a_park.csv -> 'a' (second 'a' is transaction type)
    Example: a_lvr_land_a.csv -> 'a' (second 'a' is transaction type)
    """
    parts = filename.split('_')
    if len(parts) >= 4:  # Ensure we have enough parts
        # Transaction type is the 4th part (index 3)
        trans_type = parts[3].split('.')[0]  # Remove .csv if it's the last part
        if trans_type in ['a', 'b', 'c']:
            print(f"  └─ Transaction type found: {trans_type} in {filename}")
            return trans_type
    print(f"  └─ No valid transaction type found in {filename}")
    return None

def organize_files(source_dir):
    """Organize files into appropriate folders based on transaction type"""
    print("\n=== Starting File Organization ===")
    print(f"Source directory: {source_dir}")
    
    # Create destination folders
    folders = create_transaction_folders(source_dir)
    
    # Lists to store skipped and unprocessed files
    skipped_files = []
    unprocessed_files = []
    
    # Counter for statistics
    stats = {'processed': 0, 'moved': 0, 'skipped': 0, 'unprocessed': 0}
    
    # Get all CSV files
    print("\n=== Processing Files ===")
    for root, _, files in os.walk(source_dir):
        quarter_folder = os.path.basename(root)
        if not quarter_folder.startswith('rawdata-'):
            continue
            
        for file in files:
            stats['processed'] += 1
            if file.endswith('.csv') and 'lvr_land' in file:                
                print(f"\nProcessing: {file}")
                # Get transaction type
                trans_type = get_transaction_type(file)
                if trans_type:
                    # Create new filename with quarter info
                    filename_without_ext = os.path.splitext(file)[0]
                    quarter_suffix = quarter_folder.replace('rawdata-', '')
                    new_filename = f"{filename_without_ext}-{quarter_suffix}.csv"
                    
                    # Source and destination paths
                    source_path = os.path.join(root, file)
                    dest_folder = folders.get(trans_type)
                    if dest_folder:
                        dest_path = os.path.join(source_dir, dest_folder, new_filename)
                        
                        # Skip if file already exists
                        if os.path.exists(dest_path):
                            print(f"  └─ Skipping: File already exists at destination")
                            skipped_files.append(f"Duplicate file: {file} in {quarter_folder}")
                            stats['skipped'] += 1
                            continue
                            
                        print(f"  └─ Moving {file} to: {dest_path}")
                        shutil.copy2(source_path, dest_path)
                        stats['moved'] += 1
                else:
                    skipped_files.append(f"No transaction type: {file} in {quarter_folder}")
                    stats['skipped'] += 1
            else:
                unprocessed_files.append(f"Not a target file: {file} in {quarter_folder}")
                stats['unprocessed'] += 1
    
    # Print summary
    print("\n=== Processing Summary ===")
    print(f"Total files processed: {stats['processed']}")
    print(f"Files moved: {stats['moved']}")
    print(f"Files skipped: {stats['skipped']}")
    print(f"Files unprocessed: {stats['unprocessed']}")
    
    # Print skipped files list
    if skipped_files:
        print("\n=== Skipped Files ===")
        for file in skipped_files:
            print(f"- {file}")
            
    # Print unprocessed files list
    if unprocessed_files:
        print("\n=== Unprocessed Files ===")
        for file in unprocessed_files:
            print(f"- {file}")

if __name__ == "__main__":
    base_dir = "/Users/dd/Jack/code-projects/xinyi-estate/estate-lvr-data/data/rawdata-estate-actual-price-registration"
    organize_files(base_dir)
