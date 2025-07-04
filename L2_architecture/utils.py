# here are our helper functions 
# imports here 
import json
import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import csv
from typing import List, Dict
import pandas as pd
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np

from L2_architecture.crew import *

import pandas as pd
from fpdf import FPDF
import ast

# imports for vector encoding
from sentence_transformers import SentenceTransformer
import numpy as np
from numpy.linalg import norm

import re
from sentence_transformers import SentenceTransformer, util



load_dotenv()

# Real time api fetching 
def get_board_features(
    board_name: str,
    max_results: int = 100
) -> Dict:
    id_dict = {
        "DEF2": 34,
        "DEF1": 2,
        "DEF3": 35
    }

    board_id = id_dict[board_name]
    email = os.getenv('JIRA_EMAIL')
    api_token = os.getenv('JIRA_API_TOKEN')
    print(email, api_token)

    base_url = f"https://wellsfargo-jira-test.atlassian.net/rest/agile/1.0/board/{board_id}/issue"
    headers = {"Accept": "application/json"}
    auth = HTTPBasicAuth(email, api_token)
    
    all_issues = []
    start_at = 0
    total = None

    while True:
        params = {
            "startAt": start_at,
            "maxResults": max_results,
            "jql": "issuetype = Feature"
        }

        response = requests.get(
            url=base_url,
            headers=headers,
            auth=auth,
            params=params
        )

        if response.status_code != 200:
            raise Exception(f"API request failed: {response.status_code} - {response.text}")

        data = response.json()
        all_issues.extend(data.get("issues", []))
        
        # Get total number of issues from first response
        if total is None:
            total = data.get('total', 0)
        
        # Calculate if we've fetched all issues
        if len(data.get('issues', [])) < max_results or start_at + max_results >= total:
            break
            
        start_at += max_results

    with open('L2_architecture/data/result.json', 'w') as f:
        json.dump({"features": all_issues}, f, indent=2)

    return {"features": all_issues}


# converting response to csv file 
def json_to_csv() -> None:
    """
    Convert Jira features JSON to CSV with specified fields
    
    Args:
        json_file: Path to input JSON file
        csv_file: Path to output CSV file
    """
    json_file="L2_architecture/data/result.json"	

    # Define CSV field headers
    field_names = [
        "key",
        "parent_id",
        "summary",
        "description",
        "Acceptance_crieteria",
        "labels",
        "components",
        "parent_key",
        "Requested_by",
        "timeestimate",
        "Due_date",
        "status",
        "value_statement"
    ]

    # Read JSON data
    with open(json_file, 'r',encoding='utf-8') as f:
        data = json.load(f)
    
    # Prepare CSV rows
    rows = []
    for feature in data.get('features', []):
        fields = feature.get('fields', {})
        requested_by=fields.get('customfield_10043', '')
        if "RTB" in requested_by:
            requested_by="RTB"
        elif "CTB" in requested_by:
            requested_by="CTB"
        else:
            requested_by=""

        # Handle nested fields and potential missing data
        row = {
            "key": feature.get('key', ''),
            "parent_id": fields.get('parent', {}).get('id', ''),
            "summary": fields.get('summary', ''),
            "description": fields.get('description', ''),
            "Acceptance_crieteria": fields.get('customfield_10042', ''),
            "labels": ', '.join(fields.get('labels', [])),
            "components": ', '.join([c.get('name', '') for c in fields.get('components', [])]),
            "parent_key": fields.get('parent', {}).get('key', ''),
            "Requested_by": requested_by,
            "timeestimate": fields.get('timeestimate', ''),
            "Due_date": fields.get('customfield_10040', ''),
            "status": fields.get('statusCategory', {}).get('name', ''),
            "value_statement": fields.get('customfield_10058','')
        }
        rows.append(row)

    # Write to CSV
    with open("L2_architecture/data/API.csv", 'w', newline='', encoding='utf-8') as f:	
        writer = csv.DictWriter(f, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(rows)


# returns a dict of value with column name and no of values missing
def count_empty_values(csv_file: str) -> dict:
    """
    Count the number of empty (NaN or empty string) values in each column of the CSV file.

    Args:
        csv_file: Path to the CSV file

    Returns:
        Dictionary with column names as keys and count of empty values as values
    """
    df = pd.read_csv(csv_file)
    
    # Replace empty strings with NaN to count them as empty
    df.replace('', pd.NA, inplace=True)
    
    # Count NaN values per column
    empty_counts = df.isna().sum().to_dict()
    empty_counts["Overall_issues"]=len(df)
    
    return empty_counts

import pandas as pd


# 
def filter_rows_with_missing_values_or_low_quality_data() -> None:
    """
    Reads a CSV file, filters rows with at least one missing value in any column,
    and saves those rows to a new CSV file.

    Args:
        csv_input: Path to the original CSV file
        csv_output: Path to save the filtered CSV file
    """
    csv_input="L2_architecture/data/Final_API.csv"
    csv_output="L2_architecture/data/Not-Good-issues.csv"
    df = pd.read_csv(csv_input)
    
    # Condition for missing values in any column
    missing_any = df.isna().any(axis=1)
    
    # Condition for Acceptance_result is 'Not Well Documented'
    acceptance_condition = df['Acceptance_result'].fillna('').str.strip() == 'Not Well Documented'
    
    # Condition for summary_result is 'Needs Improvement'
    summary_condition = df['summary_result'].fillna('').str.strip() == 'Needs Improvement'

    # need to add rows with overdue condition....
    # Convert Due_date to datetime
    df['Due_date'] = pd.to_datetime(df['Due_date'], errors='coerce')
    current_date = datetime.now()

    # Separate the conditions for clarity and correct operation
    overdue_condition = (
        (df['status'].fillna('').str.strip() != 'Done') & 
        (df['Due_date'] < current_date) & 
        (df['Due_date'].notna())
    )
    
    # Combine conditions: missing_any OR acceptance_condition OR summary_condition OR overdue_condition
    combined_condition = missing_any | acceptance_condition | summary_condition | overdue_condition
    
    # Filter rows
    filtered_df = df[combined_condition]

    
    # Save filtered rows to new CSV
    filtered_df.to_csv(csv_output, index=False)


# This function will be used when user asks abt some missing column
def save_rows_with_empty_column_and_low_quality_data(column_name: str) -> None:
    """
    Save rows to a new CSV where the specified column is empty or null.

    Args:
        csv_input: Path to the input CSV file.
        column_name: Column name to check for empty/null values.
        csv_output: Path to save the filtered CSV file.
    """
    csv_input="L2_architecture/data/Final_API.csv"
    csv_output="L2_architecture/data/user_specific_need.csv"

    df = pd.read_csv(csv_input)

    if(column_name=="Acceptance_result"):
        acceptance_issue = df['Acceptance_result'].isna() | (df['Acceptance_result'] == 'Not Well Documented')
        new_df=df[acceptance_issue]
        new_df.to_csv(csv_output, index=False)

    elif(column_name=="summary_result"):
        summary_issue = df['summary_result'] == 'Needs Improvement'
        new_df=df[summary_issue]
        new_df.to_csv(csv_output, index=False)

    elif(column_name=="Over Due Features"):
        df2 = pd.read_csv("L2_architecture/data/overdue.csv")
        df2.to_csv(csv_output, index=False)
    else:
        # Treat empty strings as NaN for the specified column
        df[column_name].replace('', pd.NA, inplace=True)
        
        # Filter rows where the column is NaN (empty or null)
        filtered_df = df[df[column_name].isna()]
        
        # Save filtered rows to the output CSV
        filtered_df.to_csv(csv_output, index=False)



def save_overdue_tasks() -> int:
    """
    Extracts rows from CSV where due date is in the past and status is not 'Done'.
    
    Args:
        csv_input: Path to the input CSV file
        csv_output: Path to save the filtered CSV file
        
    Returns:
        Number of overdue tasks found
    """
    csv_input="L2_architecture/data/Final_API.csv"
    csv_output="L2_architecture/data/overdue.csv"
    # Read the CSV file
    df = pd.read_csv(csv_input)
    
    # Convert Due_date to datetime format (handling empty strings and invalid formats)
    df['Due_date'] = pd.to_datetime(df['Due_date'], errors='coerce')
    
    # Get current date
    current_date = datetime.now()
    
    # Filter rows where:
    # 1. Due_date is in the past (earlier than current date)
    # 2. Due_date is not empty/invalid
    # 3. Status is anything except "Done"
    filtered_df = df.loc[
        (df['Due_date'] < current_date) & 
        (df['Due_date'].notna()) & 
        (df['status'] != 'Done')
    ]
    
    # Save filtered rows to new CSV file
    filtered_df.to_csv(csv_output, index=False)
    
    return len(filtered_df)  # Return count of overdue items


def process_evaluations():
    """
    Process each row in the CSV file to evaluate acceptance criteria and summaries.
    
    Args:
        csv_file: Path to the input CSV file
        output_csv: Path to save the output CSV file
    """
    csv_file="L2_architecture/data/API.csv"
    output_csv="L2_architecture/data/Final_API.csv"
    # Load the CSV file with proper error handling
    try:
        df = pd.read_csv(csv_file)
        print(f"Successfully loaded CSV with {len(df)} rows")
    except FileNotFoundError:
        print(f"Error: File '{csv_file}' not found. Please check the file path.")
        return
    except Exception as e:
        print(f"Error loading CSV: {str(e)}")
        return
    
    # Create empty result columns
    df["Acceptance_result"] = ""
    df["Acceptance_improvement"] = None
    df["summary_result"] = ""
    df["summary_suggestion"] = ""

    
    # Process each row
    total_rows = len(df)
    for index, row in df.iterrows():
        try:
            # Progress indicator
            if index % 10 == 0:
                print(f"Processing row {index}/{total_rows}...")
            
            # Skip if required columns are missing
            if pd.isna(row.get('Acceptance_crieteria', None)) and pd.isna(row.get('summary', None)):
                continue
                
            # Evaluate acceptance criteria if present
            if not pd.isna(row.get('Acceptance_crieteria', None)):
                acceptance_result = evaluate_acceptance_criteria(row['Acceptance_crieteria'])
                df.at[index, "Acceptance_result"] = acceptance_result.get("classification", "")
                df.at[index, "Acceptance_improvement"] = {
                    'strengths': acceptance_result.get('strengths', []),
                    'improvement_areas': acceptance_result.get('improvement_areas', []),
                    'revised_version': acceptance_result.get('revised_version', '')
                }
            
            # Evaluate summary and description if both present
            if not pd.isna(row.get('summary', None)) and not pd.isna(row.get('description', None)):
                summary_result = evaluate_summary(row['summary'], row['description'])
                df.at[index, "summary_result"] = summary_result.get("classification", "")
                df.at[index, "summary_suggestion"] = summary_result.get("improved_version", "")
                
        except Exception as e:
            print(f"Error processing row {index}: {str(e)}")
    
    # Save to new CSV
    try:
        df.to_csv(output_csv, index=False)
        print(f"Successfully saved results to {output_csv}")
        return output_csv
    except Exception as e:
        print(f"Error saving CSV: {str(e)}")
        return None

def count_separate_issues() -> dict:
    """
    Counts rows with issues in Acceptance_result and summary_result separately.
    
    Args:
        csv_file: Path to the CSV file
        
    Returns:
        Dictionary with separate counts for acceptance and summary issues.
    """
    csv_file="L2_architecture/data/Final_API.csv"
    df = pd.read_csv(csv_file)
    
    # Treat empty strings as NaN for accurate missing detection
    df['Acceptance_result'].replace('', np.nan, inplace=True)
    df['summary_result'].replace('', np.nan, inplace=True)
    
    # Count: Acceptance_result is NaN or 'Not Well Documented'
    acceptance_issue = df['Acceptance_result'].isna() | (df['Acceptance_result'] == 'Not Well Documented')
    acceptance_issue_count = acceptance_issue.sum()
    
    # Count: summary_result is 'Needs Improvement'
    summary_issue = df['summary_result'] == 'Needs Improvement'
    summary_issue_count = summary_issue.sum()
    
    return {
        'poor_acceptance_crieteria': int(acceptance_issue_count),
        'poor_summaries': int(summary_issue_count),
        'Overall_issues':len(df)
    }



# Dashboard for missing value data 
def create_missing_values_dashboard(missing_counts: dict, output_file: str = 'L2_architecture/Report/missing_values_dashboard.png'):
    """
    Creates a professional dashboard visualizing missing values percentages
    
    Args:
        missing_counts: Dictionary with columns and their missing value counts
        output_file: Path to save the output image
        
    Returns:
        Path to the saved dashboard image
    """
    # Extract keys and values
    keys = list(missing_counts.keys())
    values = list(missing_counts.values())
    
    # Calculate total rows from Overall_issues
    total_rows = missing_counts.get('Overall_issues', 10)
    
    # Remove Overall_issues from keys and values for plotting
    if 'Overall_issues' in keys:
        idx = keys.index('Overall_issues')
        keys.pop(idx)
        values.pop(idx)
    
    # Calculate percentages
    percentages = [(v / total_rows) * 100 for v in values]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor('#f0f0f0')
    
    # Bar chart
    bars = ax.barh(keys, percentages, color='#4c72b0')
    
    # Add text labels
    for bar, pct, count in zip(bars, percentages, values):
        width = bar.get_width()
        ax.text(width + 1, bar.get_y() + bar.get_height()/2, 
                f'{pct:.1f}% ({count})',
                va='center', fontsize=12, color='#333333')
    
    # Title and labels
    ax.set_title('Missing Values Percentage per Column', fontsize=18, 
                 fontweight='bold', color='#222222')
    ax.set_xlabel('Percentage (%)', fontsize=14)
    ax.set_xlim(0, max(percentages) + 10)
    
    # Remove spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    # Grid
    ax.xaxis.grid(True, linestyle='--', alpha=0.7)
    ax.yaxis.grid(False)
    
    # Invert y-axis for better readability
    ax.invert_yaxis()
    
    # Save figure
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close(fig)
    
    return output_file




# Dashboard for low quality data
def create_Bad_values_dashboard(missing_counts: dict, output_file: str = 'L2_architecture/Report/Bad_values_dashboard.png'):
    """
    Creates a professional dashboard visualizing missing values percentages
    
    Args:
        missing_counts: Dictionary with columns and their missing value counts
        output_file: Path to save the output image
        
    Returns:
        Path to the saved dashboard image
    """
    # Extract keys and values
    keys = list(missing_counts.keys())
    values = list(missing_counts.values())
    
    # Calculate total rows from Overall_issues
    total_rows = missing_counts.get('Overall_issues', 10)
    
    # Remove Overall_issues from keys and values for plotting
    if 'Overall_issues' in keys:
        idx = keys.index('Overall_issues')
        keys.pop(idx)
        values.pop(idx)
    
    # Calculate percentages
    percentages = [(v / total_rows) * 100 for v in values]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor('#f0f0f0')
    
    # Bar chart
    bars = ax.barh(keys, percentages, color='#4c72b0')
    
    # Add text labels
    for bar, pct, count in zip(bars, percentages, values):
        width = bar.get_width()
        ax.text(width + 1, bar.get_y() + bar.get_height()/2, 
                f'{pct:.1f}% ({count})',
                va='center', fontsize=12, color='#333333')
    
    # Title and labels
    ax.set_title('Poor Qulaity values Percentage per Column', fontsize=18, 
                 fontweight='bold', color='#222222')
    ax.set_xlabel('Percentage (%)', fontsize=14)
    ax.set_xlim(0, max(percentages) + 10)
    
    # Remove spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    # Grid
    ax.xaxis.grid(True, linestyle='--', alpha=0.7)
    ax.yaxis.grid(False)
    
    # Invert y-axis for better readability
    ax.invert_yaxis()
    
    # Save figure
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close(fig)
    
    return output_file



def clean_latin1(text):
    if not isinstance(text, str):
        return ''
    replacements = {
        '\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"',
        '\u2013': '-', '\u2014': '-', '\u2026': '...',
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode('latin-1', 'replace').decode('latin-1')

class PDFReport(FPDF):
    def __init__(self, orientation='L'):  # Add this constructor
        super().__init__(orientation=orientation)  # Pass orientation to parent

    def header(self):
        # 1. Red "WELLS FARGO" strip at the very top
        self.set_y(0)
        self.set_fill_color(206, 17, 38)  # Wells Fargo red
        self.rect(0, 0, self.w, 18, 'F')  # Red strip: height 18 units

        self.set_font('helvetica', 'B', 16)
        self.set_text_color(255, 255, 255)  # White text
        self.set_xy(0, 3)
        self.cell(self.w, 12, "WELLS FARGO", border=0, ln=1, align='C')

        # 2. Thin yellow strip immediately below
        self.set_y(18)
        self.set_fill_color(255, 205, 0)  # Yellow
        self.rect(0, 18, self.w, 3, 'F')  # Yellow strip: height 3 units

        self.ln(3)
        self.set_font('helvetica', 'B', 15)
        self.set_text_color(0, 0, 0)
        self.cell(0, 12, "Summary Report", ln=1, align='C')
        self.ln(10)

        self.set_y(40)  # This just ensures the content starts below the strips
    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

# summary report PDF
def create_summary_report(csv_file="L2_architecture/data/Final_API.csv", pdf_file="L2_architecture/Report/summary_report.pdf"):
    df = pd.read_csv(csv_file)

    pdf = PDFReport1(orientation='L')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font('helvetica', '', 11)

    for idx, row in df.iterrows():
        pdf.set_font('helvetica', 'B', 12)
        pdf.cell(0, 10, clean_latin1(f"Feature Key: {row.get('key', '')}"), ln=True)
        pdf.set_font('helvetica', '', 11)
        pdf.multi_cell(0, 8, clean_latin1(f"Summary: {row.get('summary', '')}"))
        pdf.ln(1)
        pdf.set_font('helvetica', 'B', 11)
        pdf.cell(0, 10, clean_latin1('Summary Evaluation Result:'), ln=True)
        pdf.set_font('helvetica', '', 11)
        pdf.multi_cell(0, 8, clean_latin1(str(row.get('summary_result', ''))))
        pdf.ln(2)
        pdf.set_font('helvetica', 'B', 11)
        pdf.cell(0, 10, clean_latin1('Suggested Improved Summary:'), ln=True)
        pdf.set_font('helvetica', '', 11)
        suggestion = row.get('summary_suggestion', '')
        if suggestion and str(suggestion).strip():
            pdf.multi_cell(0, 8, clean_latin1(str(suggestion)))
        else:
            pdf.cell(0, 8, 'None', ln=True)
        pdf.ln(10)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(10)

    pdf.output(pdf_file)

class PDFReport1(FPDF):
    def __init__(self, orientation='L'):  # Add this constructor
        super().__init__(orientation=orientation)  # Pass orientation to parent

    def header(self):
        # 1. Red "WELLS FARGO" strip at the very top
        self.set_y(0)
        self.set_fill_color(206, 17, 38)  # Wells Fargo red
        self.rect(0, 0, self.w, 18, 'F')  # Red strip: height 18 units

        self.set_font('helvetica', 'B', 16)
        self.set_text_color(255, 255, 255)  # White text
        self.set_xy(0, 3)
        self.cell(self.w, 12, "WELLS FARGO", border=0, ln=1, align='C')

        # 2. Thin yellow strip immediately below
        self.set_y(18)
        self.set_fill_color(255, 205, 0)  # Yellow
        self.rect(0, 18, self.w, 3, 'F')  # Yellow strip: height 3 units

        self.ln(3)
        self.set_font('helvetica', 'B', 15)
        self.set_text_color(0, 0, 0)
        self.cell(0, 12, "Acceptance Criteria Report", ln=1, align='C')
        self.ln(10)

        self.set_y(40)  # This just ensures the content starts below the strips
    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

# acceptance criteria report PDF
def create_acceptance_improvement_report(csv_file="L2_architecture/data/Final_API.csv", pdf_file="L2_architecture/Report/acceptance_report.pdf"):
    df = pd.read_csv(csv_file)

    pdf = PDFReport1(orientation='L')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font('helvetica', '', 11)  # Use built-in font

    for idx, row in df.iterrows():
        pdf.set_font('helvetica', 'B', 12)
        pdf.cell(0, 10, clean_latin1(f"Feature Key: {row.get('key', '')}"), ln=True)
        pdf.set_font('helvetica', '', 11)

        pdf.multi_cell(0, 8, clean_latin1(f"Summary: {row.get('summary', '')}"))
        pdf.ln(1)
        pdf.multi_cell(0, 8, clean_latin1(f"Description: {row.get('description', '')}"))
        pdf.ln(1)
        pdf.multi_cell(0, 8, clean_latin1(f"Acceptance Criteria: {row.get('Acceptance_crieteria', '')}"))
        pdf.ln(5)

        improvement_str = row.get('Acceptance_improvement', '{}')
        try:
            improvement_dict = ast.literal_eval(improvement_str) if isinstance(improvement_str, str) else {}
        except Exception:
            improvement_dict = {}

        strengths = improvement_dict.get('strengths', [])
        improvement_areas = improvement_dict.get('improvement_areas', [])
        revised_version = improvement_dict.get('revised_version', '')

        pdf.set_font('helvetica', 'B', 11)
        pdf.cell(0, 10, clean_latin1('Strengths:'), ln=True)
        pdf.set_font('helvetica', '', 11)
        if strengths:
            for s in strengths:
                pdf.multi_cell(0, 8, clean_latin1(f"- {s}"))
        else:
            pdf.cell(0, 8, 'None', ln=True)

        pdf.ln(2)
        pdf.set_font('helvetica', 'B', 11)
        pdf.cell(0, 10, clean_latin1('Improvement Areas:'), ln=True)
        pdf.set_font('helvetica', '', 11)
        if improvement_areas:
            for imp in improvement_areas:
                pdf.multi_cell(0, 8, clean_latin1(f"- {imp}"))
        else:
            pdf.cell(0, 8, 'None', ln=True)

        pdf.ln(2)
        pdf.set_font('helvetica', 'B', 11)
        pdf.cell(0, 10, clean_latin1('Revised Version:'), ln=True)
        pdf.set_font('helvetica', '', 11)
        if revised_version:
            pdf.multi_cell(0, 8, clean_latin1(revised_version))
        else:
            pdf.cell(0, 8, 'None', ln=True)

        pdf.ln(10)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(10)

    pdf.output(pdf_file)


# checking for OKR value resembelence -- vector encoding
def check_similarity(input_text, threshold=0.5):
    """
    Check if input_text is similar to at least one of the reference sentences.
    
    Args:
        input_text (str): Input paragraph to check
        threshold (float): Similarity threshold to consider as similar
        
    Returns:
        bool: True if similar to at least one reference sentence, else False
        dict: similarity scores for each reference sentence
    """
    # The 3 reference sentences
    reference_sentences = [
        "value:Mitigate SME Risk and ensure sustainable system function expertise",
        "value:Optimize System Stability, Reliability, and Processes, Increase the percentage of Transaction processing Products migrating to more efficient platform and efficiency enhancements",
        "value:Streamline Customer Interaction and Digital adoption by Increasing the adoption of self-serve digital capabilities (mobile and desktop)"
    ]
    
    # Initialize the model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Encode the reference sentences
    reference_embeddings = model.encode(reference_sentences)
    
    # Encode the input text
    input_embedding = model.encode([input_text])[0]
    
    # Calculate cosine similarity between input and each reference
    similarities = {}
    for i, ref_sentence in enumerate(reference_sentences):
        sim = np.dot(input_embedding, reference_embeddings[i]) / (norm(input_embedding) * norm(reference_embeddings[i]))
        similarities[ref_sentence] = float(sim)
    
    # Check if similar to at least one reference sentence
    is_similar = any(sim >= threshold for sim in similarities.values())
    
    print(input_text)
    print(is_similar)
    print(similarities)
    return is_similar, similarities

# function for extarcting the value 
def extract_value_sentence(text):
    # This regex finds 'value:' followed by any characters up to the first dot
    match = re.search(r'(value:[^.]*)\.', text)
    if match:
        return match.group(1).strip()
    return None

# now function for iterating through all rows of CSV file and taking value sentence from description and evaluating its similarity
def process_csv_and_check_okr() -> None:
    """
    Process CSV to check OKR alignment for each row's description.
    
    Args:
        csv_input: Path to input CSV file
        csv_output: Path to save processed CSV file
        
    Returns:
        Processed DataFrame
    """

    csv_input="L2_architecture/data/Final_API.csv"
    csv_output="L2_architecture/data/Final_API.csv"
    # Read CSV file
    df = pd.read_csv(csv_input)
    
    # Initialize OKR column with False
    df['OKR'] ="Not Good"
    
    # Process each row
    for idx, row in df.iterrows():
        description = row.get('description')
            
        # Extract value from description
        extracted_text = extract_value_sentence(description)
        print(extracted_text)
        
        # Check similarity if extraction succeeded
        if extracted_text:
            is_similar, _ = check_similarity(extracted_text)
            if is_similar:
                df.at[idx, 'OKR'] = "Good"
            else:
                df.at[idx, 'OKR'] = "Not Good"
    
    # Save processed DataFrame
    df.to_csv(csv_output, index=False)
    return None



def count_requested_by_percentage(query):
    csv_path='L2_architecture/data/API.csv'
    output_file='L2_architecture/Report/output.txt'
    df = pd.read_csv(csv_path)
    total_count = len(df)
    counts = df['Requested_by'].value_counts()
    percentages = df['Requested_by'].value_counts(normalize=True).mul(100).round(2)
    
    rtb_count = counts.get('RTB', 0)
    ctb_count = counts.get('CTB', 0)
    rtb_percent = percentages.get('RTB', 0.0)
    ctb_percent = percentages.get('CTB', 0.0)
    
    with open(output_file, 'w') as f:
        f.write(query + '\n')
        f.write('RTB Count: ' + str(rtb_count) + '\n')
        f.write('CTB Count: ' + str(ctb_count) + '\n')
        f.write('RTB Percentage: ' + str(rtb_percent) + '%\n')
        f.write('CTB Percentage: ' + str(ctb_percent) + '%\n')
        f.write('Total Issues: ' + str(total_count) + '\n')
        f.write('\n')
        f.write('----------------------------------------\n')
        f.write('\n')

    
    return 'Report saved to ' + output_file

# function for embdding and finding which query is similar to the user query
def embed_query(user_query):
    # This function will take the query and embed it using the LLM model
    # For now, we will just return the query as is
    queries = [
        "RTB/CTB classification of issues in x board",
        "Feature readiness of x board"
    ]
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    query_embeddings = model.encode(queries, convert_to_tensor=True)
    input_embedding = model.encode(user_query, convert_to_tensor=True)
    scores = util.cos_sim(input_embedding, query_embeddings)
    best_match_idx = scores.argmax()
    value = best_match_idx.item()

    return queries[best_match_idx], scores[0][best_match_idx].item(),value+1




def process_csv_and_add_missing_columns():
    # Read the CSV file into a DataFrame
    csv_path="L2_architecture/data/Final_API.csv"
    df = pd.read_csv(csv_path)
    
    # Get today's date for Due_date comparison
    today = datetime.now().date()
    
    # Columns to check for missing values or specific conditions
    columns_to_check = [
        'key', 'parent_id', 'summary', 'description', 'Acceptance_crieteria',
        'labels', 'components', 'parent_key', 'Requested_by', 'timeestimate',
        'Due_date', 'status', 'Acceptance_result', 'Acceptance_improvement',
        'summary_result', 'summary_suggestion', 'OKR', 'value_statement'
    ]
    
    def check_row(row):
        missing_cols = []
        
        # Check for missing values (NaN or empty strings)
        for col in columns_to_check:
            value = row[col]
            if pd.isna(value) or (isinstance(value, str) and value.strip() == ''):
                missing_cols.append(col)
        
        # Check specific conditions for certain columns
        if row['OKR'] == 'Not Good':
            missing_cols.append('OKR')
        if row['Acceptance_result'] == 'Not Well Documented':
            missing_cols.append('Acceptance_result')
        if row['summary_result'] == 'Needs Improvement':
            missing_cols.append('summary_result')
        
        # Check Due_date validity and if it's in the past
        due_date_str = row['Due_date']
        if isinstance(due_date_str, str) and due_date_str.strip() != '':
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
                if due_date < today:
                    missing_cols.append('Due_date')
            except ValueError:
                # Handle invalid date format
                missing_cols.append('Due_date')
        else:
            # Handle empty or non-string Due_date
            missing_cols.append('Due_date')
        
        return ', '.join(missing_cols) if missing_cols else 'No issues'
    
    # Apply the check_row function to each row
    df['Missing_Columns'] = df.apply(check_row, axis=1)
    df.to_csv(csv_path)
