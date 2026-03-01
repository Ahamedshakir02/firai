import subprocess

print("Step 1: Extracting text...")
subprocess.run(["python", "src/extract_text.py"])

print("Step 2: Cleaning text...")
subprocess.run(["python", "src/clean_text.py"])

print("Step 3: Structuring data...")
subprocess.run(["python", "src/structure_data.py"])

print("Pipeline completed.")