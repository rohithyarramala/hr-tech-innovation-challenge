import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
import pandas as pd
import plotly.express as px
import json
import re
import os
from dotenv import load_dotenv
load_dotenv()

# Configure Google AIfrom dotenv import load_dotenv

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash-lite-001")

def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def analyze_resume(resume_text, job_role, job_desc, metrics):
    prompt = f"""
You are an expert HR recruiter AI assistant specializing in technical hiring.

Job Role: {job_role}
Job Description: {job_desc}
Key Metrics to focus on: {metrics}

Carefully analyze the following resume text:

{resume_text}

Provide a JSON output ONLY with the following fields:

- relevance_score: An integer from 0 to 100 indicating how well the candidate matches the job role.
- matched_skills: A list of specific skills, experiences, or qualifications from the resume that align with the job description and key metrics.
- missing_skills: A list of important skills or qualifications mentioned in the job description or metrics that are absent or insufficiently demonstrated in the resume.
- summary: A concise, professional summary highlighting the candidate’s strengths, relevant experience, potential gaps, and suitability for the role.

Do not include any extra explanation, quotes, or text outside the JSON format.
"""
    response = model.generate_content(prompt)
    # Try to parse JSON from response text, fallback to raw text
    try:
        import ast
        result = ast.literal_eval(response.text)
        print(result)  # Debugging line to see the output
        return result
    except Exception:
        return {"raw_output": response.text}

def analyze_feedback(feedback_text, purpose):
    prompt = f"""
You are an AI analyzing employee feedback.

Purpose: {purpose}
Feedback text: "{feedback_text}"

Return JSON with:
- sentiment ("Positive", "Neutral", "Negative")
- attrition_risk ("High", "Medium", "Low")
- suggestion (brief explanation and recommended action)
"""
    response = model.generate_content(prompt)
    try:
        import ast
        result = ast.literal_eval(response.text)
        return result
    except Exception:
        return {"raw_output": response.text}

st.set_page_config(page_title="HR-Tech AI Dashboard", layout="wide")
st.title("🤖 HR-Tech AI Dashboard")

tab1, tab2 = st.tabs(["📄 Resume Screening", "💬 Employee Sentiment Analysis"])

### --- Resume Screening ---
with tab1:
    st.header("Resume Screening System")
    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded_files = st.file_uploader("Upload one or more resumes (PDF)", type=["pdf"], accept_multiple_files=True)
    with col2:
        job_role = st.text_input("Job Role", placeholder="e.g., Software Engineer")
        job_desc = st.text_area("Job Description", height=150, placeholder="Enter the job description here...")
        metrics = st.text_input("Key Metrics to Focus On (comma separated)", placeholder="e.g., Python, Leadership, 3+ years experience")

    analyze_btn = st.button("Analyze Resumes")

    if analyze_btn and uploaded_files and job_role and job_desc:
        st.info("Starting analysis...")
        results = []
        for f in uploaded_files:
            try:
                text = extract_text_from_pdf(f)
                result = analyze_resume(text, job_role, job_desc, metrics)
                if "raw_output" in result:
                    st.warning(f"AI returned unstructured output for {f.name}")
    
                    # Clean raw_output: extract content between ```json and ```
                    raw_output_str = result.get("raw_output", "")
                    try:
                        # Extract the JSON inside triple backticks
                        cleaned_json_str = re.search(r"```json\s*(\{.*?\})\s*```", raw_output_str, re.DOTALL).group(1)
                        parsed_json = json.loads(cleaned_json_str)
                    except Exception as e:
                        parsed_json = {}
                        st.error(f"Failed to parse raw_output for {f.name}: {e}")
                else:
                    parsed_json = result  # Already structured

                # Build display entry
                results.append({
                    "Resume Name": f.name,
                    "Relevance Score": parsed_json.get("relevance_score", "N/A"),
                    "Matched Skills": ", ".join(parsed_json.get("matched_skills", [])) if isinstance(parsed_json.get("matched_skills"), list) else parsed_json.get("matched_skills", "N/A"),
                    "Missing Skills": ", ".join(parsed_json.get("missing_skills", [])) if isinstance(parsed_json.get("missing_skills"), list) else parsed_json.get("missing_skills", "N/A"),
                    "Summary": parsed_json.get("summary", "No summary available")
                })
            except Exception as e:
                st.error(f"Error processing {f.name}: {str(e)}")

        if results:
            df = pd.DataFrame(results)
            st.success("Analysis Complete!")

            # Clean and convert 'Relevance Score' column to numeric
            df["Relevance Score"] = pd.to_numeric(df["Relevance Score"], errors='coerce')  # Invalid entries become NaN

            # Sort by descending relevance score
            df_sorted = df.sort_values(by="Relevance Score", ascending=False)

            # Display sorted data
            st.dataframe(df_sorted)

            # Plot bar chart
            if df_sorted["Relevance Score"].notna().any():
                fig_bar = px.bar(df_sorted, x="Resume Name", y="Relevance Score",
                                title="Resume Relevance Scores (Descending Order)",
                                labels={"Resume Name": "Resume", "Relevance Score": "Score"})
                st.plotly_chart(fig_bar, use_container_width=True)

                # Add acceptance level categories
                def categorize(score):
                    if score >= 80:
                        return "Highly Suitable"
                    elif score >= 60:
                        return "Moderately Suitable"
                    else:
                        return "Less Suitable"

                df_sorted["Acceptance Level"] = df_sorted["Relevance Score"].apply(categorize)

                # Pie chart of acceptance levels
                pie_fig = px.pie(df_sorted, names="Acceptance Level",
                                title="Resume Acceptance Likelihood Distribution",
                                hole=0.4)
                st.plotly_chart(pie_fig, use_container_width=True)
            else:
                st.info("Relevance scores not available for plotting.")


### --- Employee Sentiment Analysis ---
with tab2:
    st.header("Employee Sentiment Analysis")

    # Initialize session state to persist feedback entries
    if "feedback_list" not in st.session_state:
        st.session_state.feedback_list = []

    feedback_json = st.file_uploader(
        "Upload employee feedback JSON (list of objects with emp_id and feedback)", type=["json"]
    )
    manual_entry = st.checkbox("Add feedback manually")

    # Load feedback from JSON
    if feedback_json:
        try:
            data = json.load(feedback_json)
            st.success(f"Loaded {len(data)} feedback entries from file.")
            st.session_state.feedback_list.extend(data)
        except Exception as e:
            st.error(f"Error loading JSON: {str(e)}")

    # Add manual feedbacks (in bulk JSON format)
    if manual_entry:
        st.subheader("Add Multiple Feedbacks Manually")

        default_json = '''[
    {"emp_id": "E101", "purpose": "Exit Interview", "feedback": "I felt undervalued and overworked."},
    {"emp_id": "E102", "purpose": "Survey", "feedback": "The new benefits are great!"}
]'''
        manual_feedbacks = st.text_area("Enter feedback in JSON list format", default_json, height=200)

        if st.button("Add Manual Feedbacks"):
            try:
                entries = json.loads(manual_feedbacks)
                if isinstance(entries, list):
                    st.session_state.feedback_list.extend(entries)
                    st.success(f"Added {len(entries)} manual feedback entries.")
                else:
                    st.warning("Please input a valid list of feedback objects.")
            except Exception as e:
                st.error(f"Invalid JSON format: {str(e)}")

    if st.session_state.feedback_list:
        st.markdown("### Feedback Entries to Analyze")
        df_feedback = pd.DataFrame(st.session_state.feedback_list)
        st.dataframe(df_feedback)

        if st.button("Analyze Feedback Sentiment"):
            st.info("Analyzing feedback with AI...")

            analyzed = []
            for entry in st.session_state.feedback_list:
                try:
                    res = analyze_feedback(entry["feedback"], entry.get("purpose", "General"))

                    if "raw_output" in res:
        
                        # Clean raw_output: extract content between ```json and ```
                        raw_output_str = res.get("raw_output", "")
                        try:
                            # Extract the JSON inside triple backticks
                            cleaned_json_str = re.search(r"```json\s*(\{.*?\})\s*```", raw_output_str, re.DOTALL).group(1)
                            parsed_json = json.loads(cleaned_json_str)
                        except Exception as e:
                            st.error(f"Failed to parse raw_output: {e}")
                            st.warning(f"AI returned unstructured output for {entry.get('emp_id')} {cleaned_json_str}")
                            parsed_json = {}
                    else:
                        parsed_json = result  # Already structured

                    analyzed.append({
                        "Employee ID": entry.get("emp_id"),
                        "Purpose": entry.get("purpose"),
                        "Feedback": entry.get("feedback"),
                        "Sentiment": parsed_json.get("sentiment", "N/A"),
                        "Attrition Risk": parsed_json.get("attrition_risk", "N/A"),
                        "Suggestion": parsed_json.get("suggestion", res.get("raw_output", "N/A")),
                    })
                except Exception as e:
                    st.error(f"Error analyzing feedback for {entry.get('emp_id')}: {str(e)}")

            if analyzed:
                df_analyzed = pd.DataFrame(analyzed)
                st.success("Sentiment Analysis Complete!")
                st.dataframe(df_analyzed)

                # Pie chart: Sentiment Distribution
                fig1 = px.pie(df_analyzed, names="Sentiment", title="Sentiment Distribution")
                st.plotly_chart(fig1, use_container_width=True)

                # Bar chart: Attrition Risk
                risk_order = ["Low", "Medium", "High"]
                df_analyzed["Attrition Risk"] = pd.Categorical(
                    df_analyzed["Attrition Risk"], categories=risk_order, ordered=True
                )
                fig2 = px.histogram(
                    df_analyzed, x="Attrition Risk",
                    title="Attrition Risk Levels",
                    category_orders={"Attrition Risk": risk_order}
                )
                st.plotly_chart(fig2, use_container_width=True)



