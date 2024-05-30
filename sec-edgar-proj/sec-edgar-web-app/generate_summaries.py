import os
import openai

# Set the OpenAI API key
openai.api_key = 'API_KEY_HERE'

def create_written_insights(company_folder):
    """
    Extract insights from the 10-K filings of a company.

    Args:
    - company_folder (str): Path to the folder containing the company's 10-K filings.

    Returns:
    - tuple: A tuple containing the company name (str) and the concatenated text of all 10-K filings (str).
    """
    report_text = ""
    for submission_folder in os.listdir(company_folder):
        submission_folder_path = os.path.join(company_folder, submission_folder)
        if os.path.isdir(submission_folder_path):
            submission_file_path = os.path.join(submission_folder_path, 'submission.txt')
            if os.path.exists(submission_file_path):
                with open(submission_file_path, 'r') as file:
                    submission_text = file.read()
                    report_text += submission_text + "\n"
                    print(f"Read report from: {submission_file_path}\n{submission_text}")  # Debug statement

    company_name = os.path.basename(company_folder)
    return company_name, report_text

def summarize_company_findings(company_folder):
    """
    Analyze a company's 10-K filings to extract insights using OpenAI's API.

    Args:
    - company_folder (str): Path to the folder containing the company's 10-K filings.

    Returns:
    - tuple: A tuple containing the company name (str) and the extracted insights (str).
    """
    company_name, report_text = create_written_insights(company_folder)
    
    prompt = f"""
    You are an analyst examining {company_name}'s 10-K filings. Extract the following insights:
    1. Revenue and Net Income trends/growth percentage.
    2. Total Debt.
    3. Gross Margin and Percentage.
    4. Capital Expenditure.
    5. Effective Tax Rate and Deferred Tax Assets/Liabilities.
    6. Number of Shares Outstanding.
    7. Foreign Income Percentage.
    8. Share Buy-Back.
    And then give two more custom insights which you deem as important.
    
    Make sure that the insights are for the specific company. Refer to the company as "the company" when giving insights.
    
    Here are the reports:
    {report_text}
    
    Provide the insights in a structured format.
    """
    
    try:
        response = openai.Completion.create(
            model="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=1500,
            n=1,
            stop=None,
            temperature=0.7,
        )
        return company_name, response['choices'][0]['text'].strip()
    except Exception as e:
        print(f"Error extracting insights: {e}")  # Debug statement
        return company_name, ""

def generate_insights(ticker):
    """
    Generate insights for a given company's 10-K filings.

    Args:
    - ticker (str): Ticker symbol of the company.

    Returns:
    - dict: A dictionary containing the extracted insights.
    """
    sub_folder = '/Users/adi_shukla/Documents/sec-edgar-proj/sec-edgar-filings'
    company_folder = os.path.join(sub_folder, ticker, '10-K')
    company_name, insights = summarize_company_findings(company_folder)
    if insights:
        return {
            "Insights": insights
        }
    else:
        return {
            "Insights": "No insights found."
        }