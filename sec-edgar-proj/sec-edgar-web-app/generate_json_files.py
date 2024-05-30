import os
import openai
import json

openai.api_key = 'API_KEY_HERE'

def analyze_company(company_folder, year_folder):
    """
    Read and analyze the 10-K filings of a company for a given year, extracting relevant financial information.

    Args:
    - company_folder (str): Path to the folder containing the company's 10-K filings.
    - year_folder (str): Folder corresponding to a specific year's 10-K filings.

    Returns:
    - tuple: A tuple containing the company name (str), the year (str), and the extracted insights (dict).
    """
    report_text = ""
    year_folder_path = os.path.join(company_folder, year_folder)
    for submission_folder in os.listdir(year_folder_path):
        submission_folder_path = os.path.join(year_folder_path, submission_folder)
        if os.path.isdir(submission_folder_path):
            submission_file_path = os.path.join(submission_folder_path, 'submission.txt')
            if os.path.exists(submission_file_path):
                with open(submission_file_path, 'r') as file:
                    submission_text = file.read()
                    report_text += submission_text + "\n"
                    print(f"Read report from: {submission_file_path}\n{submission_text}")  # Debug statement

    company_name = os.path.basename(os.path.dirname(company_folder))

    # JSON extraction prompt
    json_prompt = f"""
    From the 10-K filing information that is passed in to you, extract the following information: Revenue (product wise if applicable), Net Income (product wise if applicable), Effective Tax Rate, Deferred Tax Assets, Deferred Tax Liabilities, Foreign Income Percentage, and any other relevant financial information.
    Answer in proper JSON format. Make sure the format is correct so it doesn't face the JSONDecodeError: Expecting ',' delimiter issue. Note: Only return the JSON, no additional text.
    Example JSON (sub-fields may not match completely and change but the units should be the same (billions), convert if needed)
    {{
        "2022": {{
            "Revenue": {{"Compute & Networking": "$26.938 billion", "Graphics": "$11.718 billion"}},
            "Net Income": {{"Compute & Networking": "$7.634 billion", "Graphics": "$2.462 billion"}},
            "Effective Tax Rate": "9.9%",
            "Deferred Tax Assets": "$5.05 billion",
            "Deferred Tax Liabilities": "$339 million",
            "Foreign Income Percentage": "85%"
        }},
        "2021": {{
            ...
        }}
    }}

    Note: main fields ("Revenue", "Net Income", "Effective Tax Rate", "Deferred Tax Assets", "Deferred Tax Liabilities", "Foreign Income Percentage") should be present in the JSON. However, sub-fields may vary; for example, for Revenue, the source of revenue may differ for different companies or for the same company in different years. You should mention the source of revenue in the sub-fields.
    Also mention profit or loss with a positive or negative sign in front of the number.
    Make sure the JSON format is parseable and correct and doesn't face issues like "Expecting property name enclosed in double quotes", "Expecting ',' delimiter", etc.
    Here are the reports:
    {report_text}
    """

    try:
        response_json = openai.Completion.create(
            model="gpt-3.5-turbo-instruct",
            prompt=json_prompt,
            max_tokens=1500,
            n=1,
            stop=None,
            temperature=0.7,
        )
        json_data = response_json['choices'][0]['text'].strip()
        print(f"Extracted JSON data for {company_name} - {year_folder}: {json_data}")  # Debug statement
        json_insights = json.loads(json_data)
    except Exception as e:
        print(f"Error extracting JSON insights for {company_name} - {year_folder}: {e}")  # Debug statement
        print(f"json_data: {json_data}")  # Debug statement
        json_insights = {}

    return company_name, year_folder, json_insights

def save_insights_to_json(company_name, year_folder, insights):
    """
    Save extracted insights to a JSON file.

    Args:
    - company_name (str): Name of the company.
    - year_folder (str): Folder corresponding to a specific year's 10-K filings.
    - insights (dict): Extracted insights to be saved.

    Returns:
    - None
    """
    os.makedirs('insights', exist_ok=True)
    company_folder = os.path.join('insights', company_name)
    os.makedirs(company_folder, exist_ok=True)
    insights_path = os.path.join(company_folder, f"{year_folder}_insights.json")
    with open(insights_path, 'w') as insights_file:
        json.dump(insights, insights_file)
    print(f"Saved insights for {company_name} - {year_folder} to {insights_path}")

def process_filings(ticker):
    """
    Process all 10-K filings for a given company ticker, extracting and saving insights.

    Args:
    - ticker (str): Ticker symbol of the company.

    Returns:
    - None
    """
    base_folder = '/Users/adi_shukla/Documents/sec-edgar-proj/sec-edgar-filings'
    company_folder = os.path.join(base_folder, ticker, '10-K')
    
    if not os.path.exists(company_folder):
        print(f"Company folder for {ticker} not found.")
        return
    
    year_folders = sorted(os.listdir(company_folder), reverse=True)
    for year_folder in year_folders:
        if os.path.isdir(os.path.join(company_folder, year_folder)):
            company_name, year, insights = analyze_company(company_folder, year_folder)
            save_insights_to_json(company_name, year, insights)