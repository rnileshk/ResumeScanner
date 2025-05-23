import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
import re

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="Interview Prep Platform",
    page_icon="./logo.png"
)


# Initialize Google Gemini API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get Gemini response
def get_gemini_response(input_text):
    model = genai.GenerativeModel('models/gemini-1.5-flash-8b')
    response = model.generate_content(input_text)
    return response.text

# Function to extract text from uploaded PDF
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += page.extract_text() or ""  # Handling None or empty extracts
    return text

# Function to clean and normalize the extracted text (to remove unwanted characters)
def clean_text(text):
    # Remove non-alphanumeric characters (excluding spaces) and extra spaces
    text = re.sub(r'[^A-Za-z0-9\s]', '', text)
    text = ' '.join(text.split())  # Remove extra spaces
    return text

# Prompt Template for accurate JD match analysis
input_prompt = """
Act as a highly advanced Applicant Tracking System (ATS) with deep expertise in Software Engineering, Data Science, Big Data, and Frontend/Backend Development. Your goal is to provide a nuanced and accurate assessment of a candidate's resume against a given job description.

You will receive:

A job description (JD) in the format of a text string:
jd: {job_description}

A resume (extracted text from a PDF):
resume: {resume}

Your tasks:

1. **Analyze the Resume against the JD based on the following key criteria:**

   * **Keyword Matching:** Conduct a thorough comparison of both technical (e.g., programming languages, frameworks, tools) and non-technical (e.g., methodologies, soft skills, role-specific verbs) keywords present in both the resume and the job description. Pay close attention to the presence and frequency of essential keywords highlighted in the JD.
   * **Experience Relevance:** Evaluate the alignment of the candidate's work experience with the specific requirements outlined in the job description. Consider the technologies used, methodologies applied, and the nature of the projects and responsibilities in relation to the JD's demands. For example, strong experience with "React.js" is more relevant for a JD explicitly requiring it than general "JavaScript" experience.
   * **JD & Industry Fit:** Assess the overall compatibility of the candidate's background, including domain knowledge, industry experience (if specified), and the general trajectory of their career, with the context and requirements of the job description.

2. **Assign an Accurate JD Match Percentage:**

   * Calculate this percentage based on a weighted evaluation of keyword matches (prioritizing critical technical skills and industry terms), the depth and directness of experience relevance, and the overall industry fit. The percentage should reflect genuine alignment, decreasing significantly for tangential skills or a lack of key requirements.

3. **List Missing Keywords:**

   * Identify keywords present in the job description but absent from the resume. Prioritize listing technical skills, industry-specific terminology, and crucial tools or frameworks that are explicitly mentioned and appear central to the role's responsibilities.

4. **Generate a Concise and Relevant Profile Summary:**

   * Based *solely* on the information presented in the resume, create a brief summary (2-3 sentences maximum) that highlights the candidate's key skills, relevant experience, and strengths that directly align with the requirements and preferences stated in the job description. Avoid introducing any external information or making assumptions.

5. **Handle Invalid Resumes:**

   * If the content of `resume` does not clearly resemble a professional resume (e.g., it's too short, lacks standard resume sections like "Experience" or "Skills," or contains gibberish), return the following error message:

     ```
     Error: The uploaded document does not appear to be a valid resume. Please upload a professional resume in PDF format.
     ```

**Important Notes (Reinforced):**

* The JD Match Percentage must be dynamic and reflect the actual degree of alignment. Avoid static or inflated scores.
* Your analysis should clearly differentiate between direct matches, related skills, and significant mismatches to ensure the accuracy of the match percentage and missing keywords.
Directly Incorporates "Key Points": The prompt now explicitly instructs the ATS to analyze based on the provided "Key Points," ensuring they are central to the evaluation process.
Weighted Evaluation: The instruction to use a "weighted evaluation" for the match percentage emphasizes the importance of prioritizing critical skills and direct experience.
Specificity in Missing Keywords: The prompt clarifies the prioritization of missing keywords, focusing on technical, industry-specific, and crucial terms.
Strict Profile Summary Constraint: The instruction to base the profile summary solely on the resume and to keep it concise prevents the AI from making assumptions or including extraneous details.
Clearer Error Handling: The error message for invalid resumes is more specific about the expected format.
Reinforced Important Notes: The crucial aspects of dynamic percentage and accurate discrepancy analysis are reiterated for emphasis.

**Format your response exactly as below:**

JD Match Percentage: XX%

Missing Keywords:
  - keyword1
  - keyword2


Profile Summary:
  [Summary here]
"""

# Streamlit app layout and functionality
with st.sidebar:
    st.title("Smart ATS for Resumes")
    st.subheader("About")
    st.write("This sophisticated ATS project, developed with Gemini Model (gemini-1.5-flash-8b) and Streamlit, seamlessly incorporates advanced features including resume match percentage, keyword analysis to identify missing criteria, and the generation of comprehensive profile summaries, enhancing the efficiency and precision of the candidate evaluation process for discerning talent acquisition professionals.")
    
    st.markdown("""
    - [Streamlit](https://streamlit.io/)
    - [Gemini (model/gemini-1.5-flash-8b)](https://deepmind.google/technologies/gemini/#introduction)
    - [makersuit API Key](https://makersuite.google.com/)
    """)


# Main content
st.title("Smart Application Tracking System")
st.text("Improve Your Resume ATS")

jd = st.text_area("Paste the Job Description")
uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload the pdf")

submit = st.button("Submit")

if submit:
    if uploaded_file is not None:
        # Extract and clean text from uploaded PDF
        text = input_pdf_text(uploaded_file)
        cleaned_text = clean_text(text)
        
        # Prepare the input prompt for the Gemini model
        formatted_prompt = input_prompt.format(job_description=jd, resume=cleaned_text)
        
        # Get Gemini response
        response = get_gemini_response(formatted_prompt)
        
        # Display the response
        st.subheader("ATS Analysis Result")
        st.write(response)
