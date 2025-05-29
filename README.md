# 🚀 HR-Tech AI Dashboard

This project was built as part of an **Internship Selection Challenge** to demonstrate practical HR-Tech capabilities using modern AI tools. It leverages **Google Gemini AI** and **Streamlit** to create an interactive dashboard for **Resume Screening** and **Employee Sentiment Analysis**.

> ⚠️ **Note:**  
> This demo was built in under a day. While the UI is fully functional, design polish may be minimal due to the rapid development timeline.

---

## 🎯 Key Features

### 📄 Resume Screening
- Upload and analyze multiple candidate resumes in PDF format.
- AI-powered extraction of insights based on job description and role fit.
- Scoring and ranking of resumes by relevance.
- Visualizations to compare and interpret match scores.

### 💬 Employee Sentiment Analysis
- Upload employee feedback as a JSON file or enter manually.
- Analyze sentiment (Positive / Neutral / Negative) and attrition risk (High / Medium / Low).
- Get actionable AI-generated suggestions.
- Interactive charts: sentiment distribution & attrition risk histogram.

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/hr-tech-innovation-challenge.git
cd hr-tech-innovation-challenge
2. Create and Activate a Virtual Environment
bash
Copy
Edit
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
3. Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
4. Set Up Environment Variables
Create a .env file in the root directory and add your Google API Key:

ini
Copy
Edit
GOOGLE_API_KEY=your_google_api_key_here
5. Run the App
bash
Copy
Edit
streamlit run hr-tech-innovation-challenge.py
📁 Folder Structure (Optional)
bash
Copy
Edit
.
├── resume_samples/         # Sample PDF resumes
├── feedback_samples/       # Sample employee feedback JSON
├── utils/                  # Helper functions and components
├── .env                    # API keys (not committed)
├── hr-tech-innovation-challenge.py
├── requirements.txt
└── README.md
📝 License
This project is released under the MIT License.

🙌 Acknowledgments
Developed as part of the HR-Tech Innovation Challenge by Flive Consulting (Unstop).

Powered by Google AI Studio and Streamlit.

