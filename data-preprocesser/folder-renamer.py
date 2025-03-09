import os
import re

def convert_year(chinese_year):
    # Convert Chinese year to Western year (add 1911)
    return str(int(chinese_year) + 1911)

def convert_quarter(quarter_text):
    # Convert Chinese quarter to Q format
    quarter_map = {
        "第1季": "Q1",
        "第2季": "Q2",
        "第3季": "Q3",
        "第4季": "Q4"
    }
    return quarter_map.get(quarter_text, "")

# Get current directory
directory = "."

# Loop through directories
for folder in os.listdir(directory):
    if folder.startswith("property_data_"):
        # Extract year and quarter using regex
        year_match = re.search(r'(\d+)年', folder)
        quarter_match = re.search(r'(第[1-4]季)', folder)
        
        if year_match and quarter_match:
            chinese_year = year_match.group(1)
            quarter = quarter_match.group(1)
            
            # Convert to new format
            western_year = convert_year(chinese_year)
            q_format = convert_quarter(quarter)
            
            # Handle special case for 114年
            if "現有資料只到0228" in folder:
                new_name = f"rawdata-114Q1-partial"
            else:
                new_name = f"rawdata-{western_year}{q_format}"
            
            # Rename folder
            old_path = os.path.join(directory, folder)
            new_path = os.path.join(directory, new_name)
            os.rename(old_path, new_path)
            print(f"Renamed: {folder} -> {new_name}")