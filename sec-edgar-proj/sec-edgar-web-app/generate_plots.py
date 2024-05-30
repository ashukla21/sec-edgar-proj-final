import os
import json
import openai
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def create_json_files_list(base_folder):
    """
    Creates a list of JSON file paths along with their corresponding year and company name.

    Args:
    - base_folder (str): Path to the base folder containing the JSON files.

    Returns:
    - list: A list of tuples, each containing the JSON file path, year, and company name.
    """
    json_files = []
    for root, _, files in os.walk(base_folder):
        company_name = os.path.basename(root)
        year = 2023
        for file in files:
            if file.endswith('.json'):
                json_files.append((os.path.join(root, file), year, company_name))
                year -= 1
    return json_files

def get_summarized_metrics(data):
    """
    Uses OpenAI's GPT-3.5-turbo-instruct model to summarize total revenue and net income from JSON data.

    Args:
    - data (dict): The JSON data containing financial information.

    Returns:
    - str: The summarized metrics as a text string.
    """
    prompt = f"Analyze the following JSON data and summarize the total revenue and net income:\n\n{json.dumps(data, indent=2)}\n\n"
    prompt += "Provide the total revenue, total net income, effective tax rate, and foreign income percentage in the format:\nRevenue: [value]\nNet Income: [value]\nEffective Tax Rate: [value]\nForeign Income Percentage: [value]"

    response = openai.Completion.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=150
    )
    
    return response.choices[0].text.strip()

def extract_metrics(summary_text):
    """
    Extracts financial metrics from the summarized text.

    Args:
    - summary_text (str): The summarized text containing financial metrics.

    Returns:
    - tuple: A tuple containing revenue, net income, tax rate, and foreign income percentage.
    """
    lines = summary_text.split('\n')
    revenue = None
    net_income = None
    tax_rate = None
    foreign_income = None
    
    for line in lines:
        if 'Revenue' in line:
            value = line.split(':', 1)[1].strip().replace('$', '').replace(' million', '').replace(' billion', '').strip()
            try:
                revenue = float(value)
            except ValueError:
                continue
        elif 'Net Income' in line:
            value = line.split(':', 1)[1].strip().replace('$', '').replace(' million', '').replace(' billion', '').strip()
            try:
                net_income = float(value)
            except ValueError:
                continue
        elif 'Effective Tax Rate' in line:
            value = line.split(':', 1)[1].strip().replace('%', '').strip()
            try:
                tax_rate = float(value)
            except ValueError:
                continue
        elif 'Foreign Income Percentage' in line:
            value = line.split(':', 1)[1].strip().replace('%', '').strip()
            try:
                foreign_income = float(value)
            except ValueError:
                continue

    return revenue, net_income, tax_rate, foreign_income

def analyze_json_file(json_file_path, year):
    """
    Analyzes a JSON file to extract and summarize financial metrics.

    Args:
    - json_file_path (str): Path to the JSON file.
    - year (int): The year corresponding to the JSON file.

    Returns:
    - dict: A dictionary containing the extracted metrics.
    """
    print(f"Processing {json_file_path}")  # Debug statement
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    summary_text = get_summarized_metrics(data)
    revenue, net_income, tax_rate, foreign_income = extract_metrics(summary_text)
    
    print(f"Extracted - Year: {year}, Revenue: {revenue}, Net Income: {net_income}, Tax Rate: {tax_rate}, Foreign Income: {foreign_income}")  # Debug statement

    if revenue is not None and net_income is not None:
        return {
            'Year': year,
            'Revenue': revenue,
            'Net Income': net_income,
            'Effective Tax Rate': tax_rate,
            'Foreign Income Percentage': foreign_income
        }
    else:
        return None

def plot_metrics(metrics, company_name):
    """
    Plots the financial metrics over the years for a given company.

    Args:
    - metrics (list): A list of dictionaries containing financial metrics.
    - company_name (str): Name of the company.

    Returns:
    - None
    """
    # Example metrics processing and plotting
    years = [metric['Year'] for metric in metrics]
    revenues = [metric['Revenue'] for metric in metrics]
    net_incomes = [metric['Net Income'] for metric in metrics]
    tax_rates = [metric['Effective Tax Rate'] for metric in metrics]
    foreign_incomes = [metric['Foreign Income Percentage'] for metric in metrics]
    
    # Create plots
    plt.figure()
    plt.plot(years, revenues, label='Revenue')
    plt.plot(years, net_incomes, label='Net Income')
    plt.legend()
    plt.title(f'Revenue and Net Income for {company_name}')
    revenue_net_income_path = f'static/images/{company_name}_revenue_net_income_over_years.png'
    plt.savefig(revenue_net_income_path)
    
    plt.figure()
    plt.plot(years, tax_rates, label='Effective Tax Rate')
    plt.legend()
    plt.title(f'Effective Tax Rate for {company_name}')
    tax_rate_path = f'static/images/{company_name}_effective_tax_rate_over_years.png'
    plt.savefig(tax_rate_path)
    
    plt.figure()
    plt.plot(years, foreign_incomes, label='Foreign Income Percentage')
    plt.legend()
    plt.title(f'Foreign Income Percentage for {company_name}')
    foreign_income_path = f'static/images/{company_name}_foreign_income_percentage_over_years.png'
    plt.savefig(foreign_income_path)

def create_plots(ticker):
    """
    Creates and saves plots for a given company's financial metrics.

    Args:
    - ticker (str): Ticker symbol of the company.

    Returns:
    - None
    """
    base_folder = '/Users/adi_shukla/Documents/sec-edgar-proj/insights'
    company_folder = os.path.join(base_folder, ticker)
    json_files_list = create_json_files_list(company_folder)
    
    metrics = []
    for json_file, year, company_name in json_files_list:
        if company_name == ticker:
            metric = analyze_json_file(json_file, year)
            if metric:
                metrics.append(metric)
    if metrics:
        plot_metrics(metrics, ticker)
    else:
        print(f"No metrics to plot for {ticker}.")