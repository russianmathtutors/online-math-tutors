import csv

input_file = "input.csv"  # Change to your actual file name

with open(input_file, mode="r", encoding="utf-8") as infile:
    reader = csv.DictReader(infile)
    print("CSV Column Names:", reader.fieldnames)

