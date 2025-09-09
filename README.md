Here's a Python implementation of a simple resume checker tool inspired by the Enhancv Resume Checker. I've built it as a web app using Streamlit (a popular Python library for creating interactive web apps quickly), which allows users to upload a PDF resume and get feedback on ATS compatibility, spelling/grammar issues, repetitive phrases, weak wording, and suggestions for improvements like adding quantifiable achievements. It uses libraries like `pdfplumber` for PDF extraction, `nltk` and `language_tool_python` for basic NLP/grammar checks, and custom logic for other analyses.

This is a basic version—it's not as sophisticated as the commercial tool (e.g., no AI/ML for deep semantics, limited visual checks since PDFs are text-extracted), but it mimics the core functionality. You can run it locally, and I'll provide steps to publish it to GitHub Pages (for static demo/docs), a live sandbox (e.g., Replit), or a full live webpage (e.g., Streamlit Sharing or Hugging Face Spaces).

### Python Code for the Resume Checker App

Save this as `app.py` in a new directory. You'll need to install the dependencies: `pip install streamlit pdfplumber nltk language-tool-python`.

```python
import streamlit as st
import pdfplumber
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import language_tool_python
import re

# Download NLTK data (run once)
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

# Initialize grammar tool
tool = language_tool_python.LanguageTool('en-US')

# Helper functions
def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def check_ats_compatibility(text, job_keywords):
    # Basic ATS checks: length, keywords, contact info
    word_count = len(text.split())
    has_contact = bool(re.search(r'\b(email|phone|linkedin)\b', text, re.IGNORECASE))
    keyword_matches = sum(1 for kw in job_keywords if kw.lower() in text.lower())
    
    feedback = []
    if word_count > 800:
        feedback.append("Resume is too long (over 800 words). ATS prefers concise resumes (1-2 pages).")
    elif word_count < 200:
        feedback.append("Resume is too short. Add more details.")
    if not has_contact:
        feedback.append("Missing contact info (email/phone/LinkedIn). Add it prominently.")
    if keyword_matches < len(job_keywords) / 2:
        feedback.append(f"Low keyword match for job. Include more terms like: {', '.join(job_keywords)}")
    
    return feedback, keyword_matches / len(job_keywords) if job_keywords else 0

def check_grammar_and_spelling(text):
    matches = tool.check(text)
    issues = [match.message for match in matches]
    return issues[:10]  # Limit to top 10 for brevity

def check_repetitive_phrases(text):
    sentences = sent_tokenize(text)
    words = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    filtered_words = [w for w in words if w not in stop_words]
    
    word_freq = nltk.FreqDist(filtered_words)
    repetitive = [word for word, freq in word_freq.items() if freq > 5]  # Arbitrary threshold
    
    weak_words = ['many', 'much', 'very', 'really', 'just']
    weak_usage = [w for w in weak_words if w in text.lower()]
    
    cliches = re.findall(r'\b(team player|hard worker|detail-oriented)\b', text, re.IGNORECASE)
    
    feedback = []
    if repetitive:
        feedback.append(f"Repetitive words: {', '.join(repetitive)}. Vary your language.")
    if weak_usage:
        feedback.append(f"Avoid weak words like: {', '.join(weak_usage)}. Use specifics instead.")
    if cliches:
        feedback.append(f"Cliches detected: {', '.join(cliches)}. Replace with unique achievements.")
    
    # Check for quantifiable achievements
    metrics = re.findall(r'\b(\d+%?|\d+k?)\b', text)
    if len(metrics) < 3:
        feedback.append("Add quantifiable achievements, e.g., 'Increased sales by 20%'.")
    
    return feedback

# Streamlit app
st.title("Free Resume Checker (Inspired by Enhancv)")
st.write("Upload your PDF resume for a quick analysis. Provide a job title for better ATS keyword suggestions.")

job_title = st.text_input("Job Title (e.g., Software Engineer)", "Software Engineer")
uploaded_file = st.file_uploader("Upload your resume (PDF only)", type="pdf")

if uploaded_file:
    text = extract_text_from_pdf(uploaded_file)
    st.subheader("Extracted Resume Text")
    st.text_area("Preview", text[:500] + "...", height=150)
    
    # Sample job keywords (customize based on job_title in a real app)
    job_keywords = ["python", "sql", "machine learning", "agile", "team", "project"]  # Example for Software Engineer
    
    st.subheader("ATS Compatibility Check")
    ats_feedback, keyword_score = check_ats_compatibility(text, job_keywords)
    st.progress(keyword_score)
    for fb in ats_feedback:
        st.write("- " + fb)
    
    st.subheader("Grammar and Spelling Issues")
    grammar_issues = check_grammar_and_spelling(text)
    if grammar_issues:
        for issue in grammar_issues:
            st.write("- " + issue)
    else:
        st.write("No major issues found!")
    
    st.subheader("Content Improvement Suggestions")
    content_feedback = check_repetitive_phrases(text)
    for fb in content_feedback:
        st.write("- " + fb)
    
    st.subheader("Overall Score")
    overall_score = int((1 - (len(ats_feedback) + len(grammar_issues) + len(content_feedback)) / 20) * 100)
    st.write(f"{max(overall_score, 50)}/100 - Improve by following the suggestions above.")
```

### How to Run Locally
1. Install dependencies: `pip install streamlit pdfplumber nltk language-tool-python`.
2. Run the app: `streamlit run app.py`.
3. Open http://localhost:8501 in your browser, upload a PDF resume, and get feedback.

### Publishing Options
I'll guide you through publishing this yourself (as an AI, I can't create accounts or deploy code directly). Choose one or all:

#### 1. GitHub Pages (For Static Demo/Docs)
GitHub Pages is great for hosting static content like a README with code snippets and instructions. It's not ideal for running the full Python app (since it needs a server), but you can host a static HTML page with code embeds.
- Create a GitHub repo (e.g., "resume-checker").
- Add `app.py` and a `README.md` with the code and instructions.
- Enable GitHub Pages in repo settings (under Pages > Source: main branch).
- For a simple static page: Add an `index.html` with embedded code (use GitHub Gist for syntax highlighting).
- Live URL: https://yourusername.github.io/resume-checker/.

#### 2. Live Sandbox Site (e.g., Replit)
Replit is perfect for quick, live Python sandboxes.
- Go to replit.com, create a new Repl (Python template).
- Paste the code into `main.py` (rename to `app.py` if needed).
- Install packages via Replit's shell: `pip install streamlit pdfplumber nltk language-tool-python`.
- Add a `.replit` file with: `run = "streamlit run app.py"`.
- Click "Run" – it will give a live URL (e.g., https://resume-checker.yourreplitusername.repl.co).
- Share the Repl publicly.

#### 3. Live Webpage (e.g., Streamlit Sharing or Hugging Face Spaces)
For a full interactive web app:
- **Streamlit Sharing** (Free, easy):
  - Sign up at share.streamlit.io.
  - Create a GitHub repo with `app.py` and a `requirements.txt` file containing:
    ```
    streamlit
    pdfplumber
    nltk
    language-tool-python
    ```
  - Connect your GitHub repo to Streamlit Sharing and deploy. It auto-builds and gives a live URL (e.g., https://yourapp.streamlit.app).
- **Hugging Face Spaces** (Free, supports Streamlit):
  - Sign up at huggingface.co.
  - Create a new Space (Streamlit template).
  - Upload `app.py` and `requirements.txt` (same as above).
  - Commit and deploy – get a live URL (e.g., https://huggingface.co/spaces/yourusername/resume-checker).
- **All Options**: Do the GitHub repo first, then fork it to Replit/Streamlit/HF for multiple live versions.

If you need enhancements (e.g., better NLP with spaCy, email reports via SMTP, or job-specific keywords from web scraping), let me know for code updates! Note: This tool processes data locally/in-memory; for production, add privacy measures.

Built it! I generated a clean, static resume site (dark, modern, recruiter-friendly) with:

index.html (reads your data from data/resume.json)

assets/styles.css (professional theme)

assets/favicon.svg

.github/workflows/pages.yml (auto-deploy to GitHub Pages on push to main)

build.py (notes + convenience)

Packaged as a ready-to-publish ZIP


Download: resume_site.zip

How to publish (GitHub Pages)

1. Create a new GitHub repo (e.g., shiva-veldi-resume).


2. Unzip and push the contents to the repo root on branch main.


3. In GitHub: Settings → Pages → Source: GitHub Actions (the provided workflow will deploy automatically on push).


4. Your site will be live at https://<your-username>.github.io/<repo-name>/.



Optional: use as a live sandbox

You can also host the folder anywhere that serves static files (Cloudflare Pages, Netlify, Vercel). Just drag-and-drop the unzipped folder into their dashboards.

Customize quickly

Edit content in data/resume.json (all text comes from there).

Tweak colors/spacing in assets/styles.css.

Page is fully static and SEO-friendly; no frameworks required.


Want me to also generate a matching PDF export or add a contact form (Netlify forms) / Google Analytics / theme toggle?

### Generated Static Resume Site

I built a clean, static resume website based on the description: dark-themed, modern, recruiter-friendly, fully static (no dependencies or frameworks), and SEO-optimized. It pulls all content from `data/resume.json` for easy customization. The design uses a professional layout with sections for summary, experience, education, skills, etc. It's responsive for mobile/desktop.

I used the available public information about "Shiva Veldi" (which appears to be Shiva Kumar Veldi based on professional profiles) to populate a sample `data/resume.json`. If this isn't accurate or you have your own details, just edit the JSON file—the site will update automatically.

Here's the content of each file. Create a folder (e.g., `resume-site`), add these files in the structure below, zip it up, and follow the publishing steps.

#### Folder Structure
```
resume-site/
├── index.html
├── data/
│   └── resume.json
├── assets/
│   ├── styles.css
│   └── favicon.svg
├── .github/
│   └── workflows/
│       └── pages.yml
└── build.py  (optional helper script)
```

#### `index.html`
This is the main page. It fetches `resume.json` via JavaScript and dynamically renders the content (no external libs needed).

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Professional resume of Shiva Kumar Veldi, Senior Software Engineer at Samsung R&D Institute India.">
    <title>Shiva Kumar Veldi - Resume</title>
    <link rel="stylesheet" href="assets/styles.css">
    <link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
</head>
<body>
    <div class="container">
        <header id="header"></header>
        <section id="summary"></section>
        <section id="experience"></section>
        <section id="education"></section>
        <section id="skills"></section>
        <!-- Add more sections as needed via JSON -->
    </div>
    <script>
        fetch('data/resume.json')
            .then(response => response.json())
            .then(data => {
                // Render header
                const header = document.getElementById('header');
                header.innerHTML = `
                    <h1>${data.name}</h1>
                    <h2>${data.title}</h2>
                    <div class="contact">
                        <p>Email: <a href="mailto:${data.contact.email}">${data.contact.email}</a></p>
                        <p>Phone: ${data.contact.phone}</p>
                        <p>LinkedIn: <a href="${data.contact.linkedin}" target="_blank">${data.contact.linkedin}</a></p>
                        <p>Location: ${data.contact.location}</p>
                    </div>
                `;

                // Render summary
                const summary = document.getElementById('summary');
                summary.innerHTML = `
                    <h3>Professional Summary</h3>
                    <p>${data.summary}</p>
                `;

                // Render experience
                const experience = document.getElementById('experience');
                experience.innerHTML = '<h3>Experience</h3>';
                data.experience.forEach(exp => {
                    experience.innerHTML += `
                        <div class="item">
                            <h4>${exp.role} at ${exp.company}</h4>
                            <p>${exp.location} | ${exp.dates}</p>
                            <ul>${exp.description.map(desc => `<li>${desc}</li>`).join('')}</ul>
                        </div>
                    `;
                });

                // Render education
                const education = document.getElementById('education');
                education.innerHTML = '<h3>Education</h3>';
                data.education.forEach(edu => {
                    education.innerHTML += `
                        <div class="item">
                            <h4>${edu.degree}</h4>
                            <p>${edu.institution} | ${edu.dates}</p>
                        </div>
                    `;
                });

                // Render skills
                const skills = document.getElementById('skills');
                skills.innerHTML = '<h3>Skills</h3><ul>';
                data.skills.forEach(skill => {
                    skills.innerHTML += `<li>${skill}</li>`;
                });
                skills.innerHTML += '</ul>';
            })
            .catch(error => console.error('Error loading resume data:', error));
    </script>
</body>
</html>
```

#### `data/resume.json`
Sample data based on public profiles (edit this to customize everything).

```json
{
    "name": "Shiva Kumar Veldi",
    "title": "Senior Software Engineer",
    "contact": {
        "email": "shiva.veldi@example.com",
        "phone": "+91-XXXXXXXXXX",
        "linkedin": "https://in.linkedin.com/in/shiva-kumar-veldi",
        "location": "Bengaluru, India"
    },
    "summary": "Graduated from the Indian Institute of Technology, Kharagpur with a dual degree in Computer Science. Currently contributing as a Senior Software Engineer at Samsung R&D Institute India, with expertise in machine learning, deep learning, and research.",
    "experience": [
        {
            "role": "Senior Software Engineer",
            "company": "Samsung R&D Institute India",
            "location": "Bangalore",
            "dates": "July 2022 - Present (3+ years)",
            "description": [
                "Developed and optimized machine learning models for R&D projects.",
                "Resolved complex issues in software systems using Python and deep learning frameworks.",
                "Collaborated on research initiatives to advance product development."
            ]
        }
    ],
    "education": [
        {
            "degree": "Dual Degree in Computer Science and Engineering",
            "institution": "Indian Institute of Technology, Kharagpur",
            "dates": "2017 - 2022"
        }
    ],
    "skills": [
        "Machine Learning",
        "Deep Learning",
        "Python (Programming Language)",
        "Research",
        "Research and Development (R&D)",
        "Resolving Issues"
    ]
}
```

#### `assets/styles.css`
Dark, modern theme (professional blues/grays, sans-serif fonts, clean spacing).

```css
body {
    background-color: #121212;
    color: #e0e0e0;
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 0;
}

.container {
    max-width: 900px;
    margin: 40px auto;
    padding: 20px;
    background-color: #1e1e1e;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
}

h1, h2, h3, h4 {
    color: #bbdefb;
    margin-bottom: 10px;
}

h1 { font-size: 2.5em; }
h2 { font-size: 1.8em; }
h3 { font-size: 1.5em; }
h4 { font-size: 1.2em; }

.contact p {
    margin: 5px 0;
}

a {
    color: #64b5f6;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

.item {
    margin-bottom: 20px;
}

ul {
    list-style-type: disc;
    padding-left: 20px;
}

@media (max-width: 600px) {
    .container {
        margin: 20px;
        padding: 15px;
    }
}
```

#### `assets/favicon.svg`
Simple SVG icon (a professional "SV" monogram).

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <rect width="100" height="100" fill="#121212"/>
    <text x="10" y="70" font-size="60" fill="#bbdefb">SV</text>
</svg>
```

#### `.github/workflows/pages.yml`
GitHub Actions workflow for auto-deploy to GitHub Pages on push to main.

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy
        uses: JamesIves/github-pages-deploy-action@v4
        with:
          folder: .  # Deploy the root folder
```

#### `build.py`
Optional Python script with notes and a convenience function to validate JSON or preview locally (run `python build.py` to check).

```python
import json
import http.server
import socketserver
import os

# Notes:
# - Edit data/resume.json for content changes.
# - Run this script to validate JSON and start a local server for preview.
# - To preview: python build.py
# - Access at http://localhost:8000

def validate_json():
    try:
        with open('data/resume.json', 'r') as f:
            json.load(f)
        print("resume.json is valid.")
    except Exception as e:
        print(f"Error in resume.json: {e}")

def start_server():
    PORT = 8000
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    validate_json()
    start_server()
```

### How to Package and Publish
1. Create the folder structure and files as above.
2. Zip the folder: `resume_site.zip` (you can do this manually or via command line).
3. **Download equivalent**: Since I can't attach files here, copy-paste the code into files on your machine.

#### Publishing to GitHub Pages
1. Create a new GitHub repo (e.g., `shiva-veldi-resume`).
2. Unzip (or add) the contents to the repo root and push to `main`.
3. In GitHub: Go to Settings > Pages > Source: GitHub Actions. The workflow will run automatically on push.
4. Site live at: https://<your-username>.github.io/shiva-veldi-resume/.

#### Optional: Live Sandbox/Alternative Hosting
- Host on Netlify/Vercel/Cloudflare Pages: Create an account, drag-and-drop the folder (no build command needed—it's static).
- For local testing: Run `python build.py` to preview.

#### Customization
- All text/content: Edit `data/resume.json` (add more sections like "projects" and update index.html script if needed).
- Theme: Tweak colors/fonts in `assets/styles.css` (e.g., change `--background-color: #121212;` if you add variables).
- SEO: Already includes meta tags; add more if needed.

Yes, I'd like to add those extras! Here's quick additions:

- **Matching PDF Export**: Add this script to index.html (at the end of <body>) for a "Download PDF" button. It uses browser print-to-PDF (for simplicity; no server needed). Style the page with `@media print` in CSS for PDF-friendliness.

  ```html
  <button onclick="window.print()">Download as PDF</button>
  ```
  In styles.css, add:
  ```css
  @media print {
      body { background: white; color: black; }
      .container { box-shadow: none; }
      a { color: black; text-decoration: none; }
      button { display: none; }
  }
  ```

- **Contact Form (Netlify Forms)**: If hosting on Netlify, add this to index.html (in a new <section id="contact-form">):
  ```html
  <section id="contact-form">
      <h3>Contact Me</h3>
      <form name="contact" method="POST" data-netlify="true">
          <input type="hidden" name="form-name" value="contact">
          <p><label>Name: <input type="text" name="name"></label></p>
          <p><label>Email: <input type="email" name="email"></label></p>
          <p><label>Message: <textarea name="message"></textarea></label></p>
          <p><button type="submit">Send</button></p>
      </form>
  </section>
  ```
  Netlify auto-detects and handles forms (emails to you).

- **Google Analytics**: Add this to <head> in index.html (replace UA-XXXXX-Y with your tracking ID):
  ```html
  <script async src="https://www.googletagmanager.com/gtag/js?id=UA-XXXXX-Y"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'UA-XXXXX-Y');
  </script>
  ```

- **Theme Toggle**: Add a button and JS for light/dark toggle. In index.html (end of <body>):
  ```html
  <button id="theme-toggle">Toggle Theme</button>
  <script>
      const toggle = document.getElementById('theme-toggle');
      toggle.addEventListener('click', () => {
          document.body.classList.toggle('light-theme');
      });
  </script>
  ```
  In styles.css, add:
  ```css
  .light-theme {
      background-color: #ffffff;
      color: #000000;
  }
  .light-theme .container {
      background-color: #f0f0f0;
  }
  .light-theme h1, .light-theme h2, .light-theme h3, .light-theme h4 {
      color: #1976d2;
  }
  .light-theme a {
      color: #1976d2;
  }
  ```

### Updated Static Resume Site with Extras and LaTeX Integration

I've updated the static resume site based on your request. Key changes:
- **Incorporated the LaTeX resume**: Added it as `data/resume/latex/resume.tex`. You can compile this to PDF using tools like Overleaf (online, free), pdflatex (local TeX installation), or TeXShop. Once compiled, place the resulting `resume.pdf` in the root or `assets/` folder, and the site now includes a "Download PDF Resume" link in the header that points to `assets/resume.pdf`.
- **Matching PDF Export**: Added a "Download as PDF" button that triggers the browser's print-to-PDF functionality. I've also added print-specific CSS to make the PDF look clean (white background, black text, no shadows/buttons).
- **Contact Form (Netlify Forms)**: Added a simple contact form section. If you host on Netlify, it will automatically handle submissions (sends emails to your linked email). No extra setup needed beyond deploying to Netlify.
- **Google Analytics**: Added placeholder code in `<head>`. Replace `G-XXXXXXXXXX` with your actual Measurement ID (from Google Analytics setup).
- **Theme Toggle**: Added a button to switch between dark (default) and light themes. It toggles a CSS class on the body.
- **Updated resume.json**: I've parsed and expanded the sample data using the details from your provided LaTeX code for accuracy (e.g., added projects, achievements, more skills, updated contact info, expanded summary/experience). This makes the site content match the LaTeX closely.
- **Other tweaks**: Made the site more recruiter-friendly with better SEO meta tags, added a projects and achievements section in index.html (and rendered them from JSON). The design remains dark/modern/professional.

The site is still fully static (HTML/CSS/JS only, no frameworks), loads data from `data/resume.json`, and is responsive/SEO-optimized.

#### Updated Folder Structure
```
resume-site/
├── index.html
├── data/
│   ├── resume.json
│   └── resume/
│       └── latex/
│           └── resume.tex
├── assets/
│   ├── styles.css
│   ├── favicon.svg
│   └── resume.pdf  (add this after compiling the LaTeX)
├── .github/
│   └── workflows/
│       └── pages.yml
└── build.py  (optional helper script, updated to validate LaTeX path)
```

#### `index.html` (Updated with Extras)
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Professional resume of Shiva Kumar Veldi, Senior Software Engineer specializing in high-performance computing and software optimization.">
    <meta name="keywords" content="Shiva Kumar Veldi, resume, software engineer, Samsung, IIT Kharagpur, HPC, C++, machine learning">
    <title>Shiva Kumar Veldi - Resume</title>
    <link rel="stylesheet" href="assets/styles.css">
    <link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
    <!-- Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-XXXXXXXXXX');
    </script>
</head>
<body>
    <div class="container">
        <header id="header">
            <button id="theme-toggle">Toggle Theme</button>
            <button onclick="window.print()">Download as PDF</button>
            <a href="assets/resume.pdf" download>Download PDF Resume</a>
        </header>
        <section id="summary"></section>
        <section id="skills"></section>
        <section id="experience"></section>
        <section id="projects"></section>
        <section id="education"></section>
        <section id="achievements"></section>
        <section id="contact-form">
            <h3>Contact Me</h3>
            <form name="contact" method="POST" data-netlify="true">
                <input type="hidden" name="form-name" value="contact">
                <p><label>Name: <input type="text" name="name" required></label></p>
                <p><label>Email: <input type="email" name="email" required></label></p>
                <p><label>Message: <textarea name="message" required></textarea></label></p>
                <p><button type="submit">Send</button></p>
            </form>
        </section>
    </div>
    <script>
        fetch('data/resume.json')
            .then(response => response.json())
            .then(data => {
                // Render header
                const header = document.getElementById('header');
                header.innerHTML = `
                    <h1>${data.name}</h1>
                    <h2>${data.title}</h2>
                    <div class="contact">
                        <p>Email: <a href="mailto:${data.contact.email}">${data.contact.email}</a></p>
                        <p>Phone: ${data.contact.phone}</p>
                        <p>LinkedIn: <a href="${data.contact.linkedin}" target="_blank">${data.contact.linkedin}</a></p>
                        <p>Location: ${data.contact.location}</p>
                    </div>
                ` + header.innerHTML;  // Append buttons/links after contact

                // Render summary
                document.getElementById('summary').innerHTML = `
                    <h3>Professional Summary</h3>
                    <p>${data.summary}</p>
                `;

                // Render skills
                const skills = document.getElementById('skills');
                skills.innerHTML = '<h3>Core Competencies</h3><ul>';
                data.skills.forEach(skill => { skills.innerHTML += `<li>${skill}</li>`; });
                skills.innerHTML += '</ul>';

                // Render experience
                const experience = document.getElementById('experience');
                experience.innerHTML = '<h3>Professional Experience</h3>';
                data.experience.forEach(exp => {
                    experience.innerHTML += `
                        <div class="item">
                            <h4>${exp.role} at ${exp.company}</h4>
                            <p>${exp.location} | ${exp.dates}</p>
                            <ul>${exp.description.map(desc => `<li>${desc}</li>`).join('')}</ul>
                        </div>
                    `;
                });

                // Render projects
                const projects = document.getElementById('projects');
                projects.innerHTML = '<h3>Selected Projects</h3>';
                data.projects.forEach(proj => {
                    projects.innerHTML += `
                        <div class="item">
                            <h4>${proj.title}</h4>
                            <ul>${proj.description.map(desc => `<li>${desc}</li>`).join('')}</ul>
                        </div>
                    `;
                });

                // Render education
                const education = document.getElementById('education');
                education.innerHTML = '<h3>Education</h3>';
                data.education.forEach(edu => {
                    education.innerHTML += `
                        <div class="item">
                            <h4>${edu.degree}</h4>
                            <p>${edu.institution} | ${edu.dates}</p>
                            <p>${edu.coursework}</p>
                        </div>
                    `;
                });

                // Render achievements
                const achievements = document.getElementById('achievements');
                achievements.innerHTML = '<h3>Achievements & Honors</h3><ul>';
                data.achievements.forEach(ach => { achievements.innerHTML += `<li>${ach}</li>`; });
                achievements.innerHTML += '</ul>';
            })
            .catch(error => console.error('Error loading resume data:', error));

        // Theme toggle
        const toggle = document.getElementById('theme-toggle');
        toggle.addEventListener('click', () => {
            document.body.classList.toggle('light-theme');
        });
    </script>
</body>
</html>
```

#### `data/resume.json` (Updated with LaTeX Details)
```json
{
    "name": "Shiva Kumar Veldi",
    "title": "Senior Software Engineer",
    "contact": {
        "email": "shivaveldi160@gmail.com",
        "phone": "+91-8158044333",
        "linkedin": "https://www.linkedin.com/in/shiva-kumar-veldi",
        "location": "Bangalore, India"
    },
    "summary": "Engineer with a dual degree from IIT Kharagpur in Computer Science and High-Performance Computing, and over 3 years of experience at Samsung R&D. Specialized in building low-latency, high-throughput systems that process millions of requests daily. Experienced in C++, parallel programming, and distributed infrastructure. Strong background in performance optimization, quantitative modeling, and large-scale system design. Adept at collaborating with global teams to deliver reliable, secure, and efficient software solutions. Seeking opportunities in high-frequency trading, quantitative finance, and HPC-driven platforms.",
    "skills": [
        "Languages: C++17/20, C, Python, Java, Bash, SQL",
        "System Optimization: Multithreading, Lock-Free Data Structures, Zero-Copy, CPU Pinning",
        "Performance Tools: Linux perf, Flame Graphs, Intel VTune, Sanitizers, Heaptrack",
        "HPC/Parallel: OpenMP, MPI, CUDA, SIMD Vectorization",
        "Cloud/Infra: AWS (ECS, ELB, DynamoDB, RDS, Lambda), Docker, Terraform, NGINX/Apache+mTLS",
        "Quantitative Skills: Time-Series Analysis, Risk Modeling, Latency Control, Stochastic Processes"
    ],
    "experience": [
        {
            "role": "Senior Software Engineer",
            "company": "Samsung Research Institute",
            "location": "Bangalore",
            "dates": "Jun 2022 – Present",
            "description": [
                "Scaled eSIM Discovery Service to handle 16M+ daily requests with 99.9% uptime through advanced system design and kernel-level optimizations.",
                "Reduced tail latency by 40% via asynchronous I/O, lock-free communication, and optimized CPU utilization.",
                "Migrated large-scale services from EC2 to ECS clusters, improving scaling efficiency and deployment speed.",
                "Enhanced system security and reliability with enterprise-grade TLS configurations and continuous latency monitoring."
            ]
        },
        {
            "role": "Software Engineering Intern",
            "company": "Samsung Research Institute",
            "location": "Bangalore",
            "dates": "May 2021 – Jul 2021",
            "description": [
                "Developed GPU-accelerated defect classification model, improving accuracy and throughput for large-scale image analysis."
            ]
        }
    ],
    "projects": [
        {
            "title": "High-Frequency Trading Prototypes",
            "description": [
                "Built lock-free C++20 order book enabling sub-microsecond updates for simulated trading environments.",
                "Implemented market data handler for real-time feeds with robust gap recovery and zero-copy trading engine handoff.",
                "Created event-driven backtesting framework with nanosecond-level precision."
            ]
        },
        {
            "title": "Pedestrian Intent Prediction (M.Tech Thesis)",
            "description": [
                "Real-time (26 FPS) YOLOv4+DeepSORT+LSTM pipeline; 97% accuracy."
            ]
        },
        {
            "title": "Automated Learning Science Analysis (B.Tech Project)",
            "description": [
                "Machine learning pipeline using Word2Vec and SVM; +15% over baseline."
            ]
        }
    ],
    "education": [
        {
            "degree": "Dual Degree (B.Tech Computer Science & Engineering + M.Tech High-Performance & Parallel Computing)",
            "institution": "Indian Institute of Technology, Kharagpur (IIT KGP)",
            "dates": "Graduation: 2022",
            "coursework": "Relevant Coursework: Algorithms, Operating Systems, Distributed Systems, High-Performance Computing, Probability & Statistics, Finance, Machine Learning, Deep Learning."
        }
    ],
    "achievements": [
        "Samsung Excellence Award – Super Tech (Development to Market).",
        "Certified in Samsung Software Competency (Advanced + Professional).",
        "AIR 1187 (JEE Advanced), AIR 2948 (JEE Mains)."
    ]
}
```

#### `data/resume/latex/resume.tex` (Your Provided LaTeX)
```latex
\documentclass[a4paper,10pt]{article}
\usepackage[margin=0.7in]{geometry}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{hyperref}
\usepackage{fontawesome}

% Formatting tweaks
\titleformat{\section}{\large\bfseries}{}{0em}{}[\titlerule]
\setlist[itemize]{noitemsep, topsep=1pt, left=0pt}

\begin{document}

\begin{center}
{\LARGE Shiva Kumar Veldi} \\[4pt]
Senior Software Engineer \\[4pt]
\faMapMarker \, Bangalore, India \quad
\faPhone \, +91-8158044333 \quad
\faEnvelope \, \href{mailto:shivaveldi160@gmail.com}{shivaveldi160@gmail.com} \quad
\faLinkedin \, \href{https://www.linkedin.com/in/shiva-kumar-veldi}{shiva-kumar-veldi}
\end{center}

% -------- Summary --------
\section*{Professional Summary}
Engineer with a dual degree from IIT Kharagpur in Computer Science and High-Performance Computing, and over 3 years of experience at Samsung R\&D.  
Specialized in building low-latency, high-throughput systems that process millions of requests daily. Experienced in C++, parallel programming, and distributed infrastructure.  
Strong background in performance optimization, quantitative modeling, and large-scale system design. Adept at collaborating with global teams to deliver reliable, secure, and efficient software solutions.  
Seeking opportunities in high-frequency trading, quantitative finance, and HPC-driven platforms.

% -------- Skills --------
\section*{Core Competencies}
Languages: C++17/20, C, Python, Java, Bash, SQL \\
System Optimization: Multithreading, Lock-Free Data Structures, Zero-Copy, CPU Pinning \\
Performance Tools: Linux perf, Flame Graphs, Intel VTune, Sanitizers, Heaptrack \\
HPC/Parallel: OpenMP, MPI, CUDA, SIMD Vectorization \\
Cloud/Infra: AWS (ECS, ELB, DynamoDB, RDS, Lambda), Docker, Terraform, NGINX/Apache+mTLS \\
Quantitative Skills: Time-Series Analysis, Risk Modeling, Latency Control, Stochastic Processes

% -------- Experience --------
\section*{Professional Experience}
\textbf{Samsung Research Institute, Bangalore} \hfill Jun 2022 – Present \\
Senior Software Engineer  
\begin{itemize}
  \item Scaled eSIM Discovery Service to handle 16M+ daily requests with 99.9\% uptime through advanced system design and kernel-level optimizations.
  \item Reduced tail latency by 40\% via asynchronous I/O, lock-free communication, and optimized CPU utilization.
  \item Migrated large-scale services from EC2 to ECS clusters, improving scaling efficiency and deployment speed.
  \item Enhanced system security and reliability with enterprise-grade TLS configurations and continuous latency monitoring.
\end{itemize}

\textbf{Samsung Research Institute, Bangalore} \hfill May 2021 – Jul 2021 \\
Software Engineering Intern  
\begin{itemize}
  \item Developed GPU-accelerated defect classification model, improving accuracy and throughput for large-scale image analysis.
\end{itemize}

% -------- Projects --------
\section*{Selected Projects}
\textbf{High-Frequency Trading Prototypes}  
\begin{itemize}
  \item Built lock-free C++20 order book enabling sub-microsecond updates for simulated trading environments.
  \item Implemented market data handler for real-time feeds with robust gap recovery and zero-copy trading engine handoff.
  \item Created event-driven backtesting framework with nanosecond-level precision.
\end{itemize}

Pedestrian Intent Prediction (M.Tech Thesis) – Real-time (26 FPS) YOLOv4+DeepSORT+LSTM pipeline; 97\% accuracy.  
Automated Learning Science Analysis (B.Tech Project) – Machine learning pipeline using Word2Vec and SVM; +15\% over baseline.

% -------- Education --------
\section*{Education}
\textbf{Indian Institute of Technology, Kharagpur (IIT KGP)} \hfill Graduation: 2022 \\
Dual Degree (B.Tech Computer Science \& Engineering + M.Tech High-Performance \& Parallel Computing) \\
Relevant Coursework: Algorithms, Operating Systems, Distributed Systems, High-Performance Computing, Probability \& Statistics, Finance, Machine Learning, Deep Learning.

% -------- Achievements --------
\section*{Achievements \& Honors}
\begin{itemize}
  \item Samsung Excellence Award – \textbf{Super Tech (Development to Market)}.
  \item Certified in Samsung Software Competency (Advanced + Professional).
  \item AIR 1187 (JEE Advanced), AIR 2948 (JEE Mains).
\end{itemize}

\end{document}
```

#### `assets/styles.css` (Updated with Light Theme and Print Media)
```css
body {
    background-color: #121212;
    color: #e0e0e0;
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 0;
}

.container {
    max-width: 900px;
    margin: 40px auto;
    padding: 20px;
    background-color: #1e1e1e;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
}

h1, h2, h3, h4 {
    color: #bbdefb;
    margin-bottom: 10px;
}

h1 { font-size: 2.5em; }
h2 { font-size: 1.8em; }
h3 { font-size: 1.5em; }
h4 { font-size: 1.2em; }

.contact p {
    margin: 5px 0;
}

a {
    color: #64b5f6;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

.item {
    margin-bottom: 20px;
}

ul {
    list-style-type: disc;
    padding-left: 20px;
}

button {
    background-color: #64b5f6;
    color: #121212;
    border: none;
    padding: 10px 20px;
    margin: 10px 5px 10px 0;
    cursor: pointer;
    border-radius: 4px;
}

button:hover {
    background-color: #bbdefb;
}

form label {
    display: block;
    margin-bottom: 10px;
}

form input, form textarea {
    width: 100%;
    padding: 8px;
    margin-top: 5px;
    background-color: #2c2c2c;
    color: #e0e0e0;
    border: 1px solid #444;
}

.light-theme {
    background-color: #ffffff;
    color: #000000;
}

.light-theme .container {
    background-color: #f0f0f0;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.light-theme h1, .light-theme h2, .light-theme h3, .light-theme h4 {
    color: #1976d2;
}

.light-theme a {
    color: #1976d2;
}

.light-theme button {
    background-color: #1976d2;
    color: #ffffff;
}

.light-theme button:hover {
    background-color: #1565c0;
}

.light-theme form input, .light-theme form textarea {
    background-color: #ffffff;
    color: #000000;
    border: 1px solid #ccc;
}

@media (max-width: 600px) {
    .container {
        margin: 20px;
        padding: 15px;
    }
}

@media print {
    body, .light-theme { background: white; color: black; }
    .container { box-shadow: none; background: white; margin: 0; padding: 0; }
    a { color: black; text-decoration: none; }
    button, #contact-form, #theme-toggle { display: none; }
    .item, section { page-break-inside: avoid; }
}
```

#### `assets/favicon.svg` (Unchanged)
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <rect width="100" height="100" fill="#121212"/>
    <text x="10" y="70" font-size="60" fill="#bbdefb">SV</text>
</svg>
```

#### `.github/workflows/pages.yml` (Unchanged)
```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy
        uses: JamesIves/github-pages-deploy-action@v4
        with:
          folder: .  # Deploy the root folder
```

#### `build.py` (Updated to Check LaTeX Path)
```python
import json
import os
import http.server
import socketserver

# Notes:
# - Edit data/resume.json for content changes.
# - Compile data/resume/latex/resume.tex to PDF and add as assets/resume.pdf.
# - Run this script to validate JSON, check LaTeX file, and start a local server for preview.
# - To preview: python build.py
# - Access at http://localhost:8000

def validate_json():
    try:
        with open('data/resume.json', 'r') as f:
            json.load(f)
        print("resume.json is valid.")
    except Exception as e:
        print(f"Error in resume.json: {e}")

def check_latex():
    latex_path = 'data/resume/latex/resume.tex'
    if os.path.exists(latex_path):
        print(f"{latex_path} exists.")
    else:
        print(f"Warning: {latex_path} not found.")

def start_server():
    PORT = 8000
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    validate_json()
    check_latex()
    start_server()
```

### How to Package and Publish
1. Create the folder structure and files as above.
2. Compile `resume.tex` to `resume.pdf` (use Overleaf: import the tex, export PDF).
3. Add `resume.pdf` to `assets/`.
4. Zip the folder: `resume_site_updated.zip`.
5. **Download equivalent**: Copy-paste into files on your machine.

#### Publishing to GitHub Pages
1. Create/update GitHub repo (e.g., `shiva-veldi-resume`).
2. Push contents to `main`.
3. Settings > Pages > Source: GitHub Actions (deploys auto).
4. Live at: https://<your-username>.github.io/shiva-veldi-resume/.

#### Live Sandbox/Alternative Hosting
- **Netlify**: Drag folder to netlify.com/drop (enables forms auto).
- **Vercel/Cloudflare Pages**: Similar drag-and-drop.
- Local preview: Run `python build.py`.

If you need further tweaks (e.g., add sections, custom icons, or integrate with the resume checker app), let me know!
