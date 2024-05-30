from flask import Flask, render_template, request, redirect, url_for
import openai
import os
import json
import matplotlib.pyplot as plt

# Import your custom scripts
import sec_edgar_downloader_script
import generate_json_files
import generate_plots
import generate_summaries

app = Flask(__name__)

# Set OpenAI API key
openai.api_key = 'API_KEY_HERE'

@app.route('/', methods=['GET', 'POST'])
def home():
    """
    Handles the home route of the web application. If the request method is POST, 
    it processes the form input to generate insights and plots for the given ticker symbol.

    Returns:
    - str: Rendered HTML template for home or insights page.
    """
    if request.method == 'POST':
        ticker = request.form['ticker']
        verbal_insights = generate_summaries.generate_insights(ticker)
        generate_plots.create_plots(ticker)
        return render_template('insights.html', ticker=ticker, insights=verbal_insights)
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)