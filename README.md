# 🧾 Tender Clause Analyzer (GPT-powered Legal Risk Review)

### 🚀 Overview
**Tender Clause Analyzer** is an AI-powered tool that analyzes government or corporate tender documents (PDF/DOCX) and produces a **clause-by-clause legal risk summary** — in clear, professional language.

It is designed for **contractors, legal teams, and tender managers** to quickly understand critical contract risks, without needing to read through hundreds of pages.

---

### ✨ Key Features
✅ **Clause-based AI Review:** Automatically analyzes standard clauses such as:
- Scope of Work (SOW)
- Defect Liability Period (DLP)
- Payment Terms
- Liquidated Damages
- Termination
- Indemnity and Insurance
- Governing Law and Dispute Resolution
- Intellectual Property Rights

✅ **Formal, Plain-English Summaries:** GPT-4.1-mini provides concise and clear explanations suitable for non-lawyers.

✅ **Reviewer Comments Section:** Users can add remarks before exporting.

✅ **Branded PDF Reports:** Generates professional reports with:
- Company logo
- Executive summary
- Highlighted clause sections
- Custom fonts and layout

✅ **Streamlit-based Interface:** Easy to use, responsive web UI with upload and download options.

---

### 🖥️ Tech Stack
- **Frontend / App Framework:** Streamlit  
- **AI Model:** OpenAI GPT-4.1-mini  
- **Document Handling:** PyPDF2, python-docx  
- **PDF Reports:** ReportLab  
- **Data Processing:** Pandas  

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Add Your OpenAI API Key

Create a file named .env in the root folder:

OPENAI_API_KEY=sk-your-key-here


(Your .env file is automatically ignored by Git for security.)

5️⃣ Run the App
streamlit run app.py

📄 Example Output

AI-generated clause-wise tender summary

Executive summary with overall risk rating

Reviewer comments included in final PDF

Professionally formatted PDF report

🧠 Future Enhancements

Multi-language support (Hindi, English)

Automated contract comparison

Cloud storage integration (Google Drive / SharePoint)

Custom clause detection using NLP

🏢 Author

Vedant Jaiswar
Progility Technologies Pvt. Ltd.
📧 Vedant.Jaiswar@progilitytech.com
    