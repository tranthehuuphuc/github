import os
import pandas as pd
import shutil
import re

CSV_FILE = './data/student_list.csv'
INPUT_FOLDER = './data/raw_certs'
OUTPUT_FOLDER = './data/certs'

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Read CSV file
df = pd.read_csv(CSV_FILE, encoding='utf-8')
cert_list = df['Số GCN'].tolist()
name_list = df['Họ và tên'].tolist()

# Sanitize filename to remove unwanted characters
def sanitize_filename(name):
    return re.sub(r'[^\w\-_. ]', '', name).strip().replace(' ', '_')

# Extract order number from filename
def extract_order_number(filename):
    match = re.search(r'-(\d+)', filename)
    return int(match.group(1)) if match else float('inf')

# Get and sort file list by order number
files = sorted(
    [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith('.pdf')],
    key=extract_order_number
)

# Check if the number of files matches the number of certificates
if len(files) != len(cert_list):
    print(f"❌ Số lượng file ({len(files)}) không khớp với số lượng GCN ({len(cert_list)}).")
    exit(1)

# Rename and copy files
for file, cert, name in zip(files, cert_list, name_list):
    safe_name = sanitize_filename(name)
    old_path = os.path.join(INPUT_FOLDER, file)
    new_filename = f'GCN_{cert}_{safe_name}.pdf'
    new_path = os.path.join(OUTPUT_FOLDER, new_filename)

    shutil.copy2(old_path, new_path)
    print(f'✅ {file} → {new_filename}')
