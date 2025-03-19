import csv
import openai
import sys
import os

# Ensure command-line arguments are provided
if len(sys.argv) != 3:
    print("Usage: python script.py <input_file.csv> <output_file.csv>")
    sys.exit(1)

# Get file names from command-line arguments
input_file = sys.argv[1]
output_file = sys.argv[2]

# Set OpenAI API Key (Use environment variable for security)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Error: OpenAI API key not found. Set OPENAI_API_KEY as an environment variable.")
    sys.exit(1)

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def generate_first_line(linkedin, address):
    """Generates a personalized first line using GPT-4o Mini."""
    
    details = []
    if linkedin:
        details.append(f"LinkedIn: {linkedin}")
    if address:
        details.append(f"Address: {address}")

    source_text = ", ".join(details) if details else "No available information"

    prompt = (
        f"Act like a cold email first-line writer. Visit the provided information: {source_text} and follow ALL rules:\n\n"
        "Rule 1: Write a casual, not too enthusiastic compliment about their personal qualifications/achievements as a math tutor.\n"
        "Rule 2: Prioritize their qualifications as a math tutor, not other achievements.\n"
        "Rule 3: Be specific. Mention something that applies only to this individual.\n"
        "Rule 4: Don't cringe. Use a professional but conversational tone.\n"
        "Rule 5: Keep it under 13 words.\n"
        "Rule 6: Only write one sentence.\n"
        "Rule 7: Always prioritize information found on LinkedIn, over address.\n"
        "Rule 8: If using LinkedIn, check for personal updates, experience, partnerships, team achievements, or leadership insights.\n"
        "Rule 9: If using the address, mention something relevant about the business location (e.g., its city, industry hub, or unique positioning).\n\n"
        f"Sources: {source_text}\n\n"
        "Personalized first line:\n"
    )

    # Use OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}]
    )

    return response.choices[0].message.content.strip()

# Read input CSV and write output CSV with personalized first lines
with open(input_file, mode="r", encoding="utf-8") as infile, open(output_file, mode="w", encoding="utf-8", newline="") as outfile:
    reader = csv.DictReader(infile)

    # Ensure correct field names
    fieldnames = reader.fieldnames
    if not fieldnames:
        print("Error: The input CSV file is empty or incorrectly formatted.")
        sys.exit(1)

    # Identify actual column names dynamically
    column_mappings = {
        "Company": "Company",  # Correct mapping for company name
        "Website": "Website",  # Matches 'Website'
        "Company Linkedin Url": "Company Linkedin Url",  # Matches 'Company Linkedin Url'
        "Company Address": "Company Address",  # Matches 'Company Address'
        "Person Linkedin Url": "Person Linkedin Url"  # Add this line to fix the error
    }

    # Ensure at least Company column is found
    if not column_mappings["Company"]:
        print("Error: Could not detect 'Company' column. Check your CSV headers.")
        sys.exit(1)

    # Add output column
    output_fieldnames = fieldnames + ["First Line"]
    writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
    
    writer.writeheader()

    for row in reader:
        linkedin = row.get(column_mappings["Person Linkedin Url"], "").strip() if column_mappings["Person Linkedin Url"] in row else ""
        address = row.get(column_mappings["Company Address"], "").strip() if column_mappings["Company Address"] in row else ""

        if not linkedin and not address:
            print(f"Skipping row: No useful data found.")
            row["First Line"] = "No valid company data available."
        else:
            row["First Line"] = generate_first_line(linkedin, address)

        writer.writerow(row)

print(f"Personalized lines added to {output_file}!")