#!/usr/bin/env python3
"""
Dynamic Website Generator for Resume Uploads
Creates personalized portfolio websites from uploaded resumes
"""

import os
import sys
import json
import argparse
import shutil
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import tempfile
import zipfile

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from src.core.resume_processor import ResumeProcessor
    from src.utils.text_processing import TextProcessor
    from src.ai.processors.enhanced_document_processor import EnhancedDocumentProcessor
except ImportError as e:
    print(f"Warning: Could not import resume processing modules: {e}")
    print("Running in standalone mode with basic text processing")

class DynamicWebsiteGenerator:
    """Generate dynamic portfolio websites from resume uploads"""
    
    def __init__(self):
        self.base_template_dir = Path(__file__).parent / "website"
        self.output_dir = Path(__file__).parent / "generated_websites"
        self.temp_dir = None
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize processors if available
        try:
            self.resume_processor = ResumeProcessor()
            self.text_processor = TextProcessor()
            self.doc_processor = EnhancedDocumentProcessor()
            self.processors_available = True
        except Exception as e:
            print(f"Warning: Resume processors not available: {e}")
            self.processors_available = False
    
    def extract_resume_data(self, file_path: str) -> Dict[str, Any]:
        """Extract structured data from resume file"""
        
        if self.processors_available:
            try:
                # Use the full resume processing pipeline
                return self._extract_with_processors(file_path)
            except Exception as e:
                print(f"Error with advanced processing: {e}")
                print("Falling back to basic extraction")
        
        # Basic extraction fallback
        return self._extract_basic(file_path)
    
    def _extract_with_processors(self, file_path: str) -> Dict[str, Any]:
        """Extract data using the advanced resume processors"""
        # This would use the existing resume processing pipeline
        # For now, return a structured template
        return self._get_default_structure()
    
    def _extract_basic(self, file_path: str) -> Dict[str, Any]:
        """Basic text extraction and parsing"""
        try:
            # Try to extract text from different file types
            text_content = self._extract_text_from_file(file_path)
            
            # Parse the text content
            return self._parse_resume_text(text_content)
            
        except Exception as e:
            print(f"Error in basic extraction: {e}")
            return self._get_default_structure()
    
    def _extract_text_from_file(self, file_path: str) -> str:
        """Extract text content from various file formats"""
        file_path = Path(file_path)
        
        if file_path.suffix.lower() == '.pdf':
            return self._extract_pdf_text(file_path)
        elif file_path.suffix.lower() in ['.docx', '.doc']:
            return self._extract_docx_text(file_path)
        elif file_path.suffix.lower() == '.txt':
            return file_path.read_text(encoding='utf-8')
        else:
            # Try to read as text file
            try:
                return file_path.read_text(encoding='utf-8')
            except:
                return ""
    
    def _extract_pdf_text(self, file_path: Path) -> str:
        """Extract text from PDF file"""
        try:
            import PyPDF2
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except ImportError:
            print("PyPDF2 not available for PDF processing")
            return ""
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return ""
    
    def _extract_docx_text(self, file_path: Path) -> str:
        """Extract text from DOCX file"""
        try:
            import docx
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except ImportError:
            print("python-docx not available for DOCX processing")
            return ""
        except Exception as e:
            print(f"Error extracting DOCX text: {e}")
            return ""
    
    def _parse_resume_text(self, text: str) -> Dict[str, Any]:
        """Parse resume text into structured data"""
        # Basic parsing logic
        data = self._get_default_structure()
        
        if not text.strip():
            return data
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Extract basic information
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        
        # Find email
        email_match = re.search(email_pattern, text)
        if email_match:
            data['personal']['contact']['email'] = email_match.group()
        
        # Find phone
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            data['personal']['contact']['phone'] = phone_match.group()
        
        # Extract name (assume it's one of the first few lines)
        potential_names = []
        for line in lines[:5]:
            # Skip lines that look like contact info
            if any(char in line for char in '@()+-') or any(word in line.lower() for word in ['email', 'phone', 'tel', 'mobile']):
                continue
            # Skip lines that are too long (likely not names)
            if len(line.split()) > 4:
                continue
            if len(line.split()) >= 2:
                potential_names.append(line)
        
        if potential_names:
            data['personal']['name'] = potential_names[0]
        
        # Extract sections
        self._extract_sections(text, data)
        
        return data
    
    def _extract_sections(self, text: str, data: Dict[str, Any]):
        """Extract different sections from resume text"""
        text_lower = text.lower()
        
        # Common section headers
        section_patterns = {
            'experience': ['experience', 'work experience', 'professional experience', 'employment'],
            'education': ['education', 'academic background', 'qualifications'],
            'skills': ['skills', 'technical skills', 'competencies', 'expertise'],
            'projects': ['projects', 'selected projects', 'key projects'],
            'summary': ['summary', 'profile', 'objective', 'about'],
        }
        
        # Find section boundaries
        sections = {}
        for section_name, keywords in section_patterns.items():
            for keyword in keywords:
                pattern = r'\n\s*' + re.escape(keyword) + r'\s*\n'
                match = re.search(pattern, text_lower)
                if match:
                    sections[section_name] = match.start()
                    break
        
        # Extract skills
        skills_keywords = ['python', 'javascript', 'java', 'c++', 'react', 'node.js', 'sql', 'html', 'css', 'git', 'docker', 'aws']
        found_skills = []
        for skill in skills_keywords:
            if skill.lower() in text_lower:
                found_skills.append(skill.capitalize())
        
        if found_skills:
            data['skills']['technical'] = found_skills[:10]  # Limit to top 10
    
    def _get_default_structure(self) -> Dict[str, Any]:
        """Get default data structure for website generation"""
        return {
            "personal": {
                "name": "Professional Portfolio",
                "title": "Software Engineer & Developer",
                "tagline": "Building innovative solutions with modern technology",
                "photo": "assets/profile.jpg",
                "contact": {
                    "email": "contact@example.com",
                    "phone": "+1-XXX-XXX-XXXX",
                    "location": "Tech City, Innovation State",
                    "website": "https://portfolio.example.com",
                    "linkedin": "https://linkedin.com/in/username",
                    "github": "https://github.com/username",
                    "twitter": "https://twitter.com/username",
                    "instagram": "https://instagram.com/username"
                }
            },
            "about": {
                "summary": "Passionate software engineer with expertise in modern web development and emerging technologies. Committed to creating efficient, scalable solutions and continuously learning new skills.",
                "highlights": [
                    "Experienced in full-stack development",
                    "Strong problem-solving abilities", 
                    "Excellent communication skills",
                    "Team collaboration and leadership",
                    "Continuous learning mindset"
                ],
                "values": [
                    "Innovation", "Quality", "Learning", "Teamwork", "Excellence"
                ]
            },
            "skills": {
                "technical": [
                    "Python", "JavaScript", "React", "Node.js", "SQL", "Git", "Docker", "AWS"
                ],
                "tools": [
                    "VS Code", "GitHub", "Postman", "Figma", "Slack"
                ],
                "soft": [
                    "Leadership", "Communication", "Problem Solving", "Project Management"
                ]
            },
            "experience": [
                {
                    "role": "Software Engineer",
                    "company": "Tech Company",
                    "location": "Tech City",
                    "dates": "2020 - Present",
                    "type": "Full-time",
                    "description": [
                        "Developed and maintained web applications",
                        "Collaborated with cross-functional teams",
                        "Implemented best practices and code reviews",
                        "Contributed to system architecture decisions"
                    ],
                    "technologies": ["Python", "JavaScript", "React", "PostgreSQL"]
                }
            ],
            "projects": [
                {
                    "title": "Dynamic Portfolio Generator",
                    "description": "An automated tool for creating personalized portfolio websites from resume uploads",
                    "technologies": ["Python", "JavaScript", "HTML/CSS", "AI APIs"],
                    "highlights": [
                        "Automated content extraction and structuring",
                        "Multiple responsive design templates",
                        "SEO optimization and performance tuning"
                    ],
                    "links": {
                        "github": "#",
                        "demo": "#"
                    }
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science in Computer Science",
                    "institution": "University Name",
                    "location": "City, State",
                    "dates": "2016 - 2020",
                    "gpa": "3.7/4.0",
                    "coursework": ["Data Structures", "Algorithms", "Software Engineering", "Databases"]
                }
            ],
            "certifications": [
                {
                    "name": "AWS Certified Developer",
                    "issuer": "Amazon Web Services",
                    "date": "2023",
                    "credential": "AWS-DEV-XXXX"
                }
            ],
            "achievements": [
                "Contributed to open-source projects",
                "Presented at local tech meetups",
                "Mentored junior developers",
                "Led successful project deliveries"
            ],
            "interests": [
                "Open Source", "Tech Innovation", "Continuous Learning", "Problem Solving"
            ]
        }
    
    def generate_website(self, resume_data: Dict[str, Any], output_name: str, theme: str = "modern") -> str:
        """Generate a complete website from resume data"""
        
        # Create output directory
        site_output_dir = self.output_dir / output_name
        if site_output_dir.exists():
            shutil.rmtree(site_output_dir)
        
        # Copy base template
        shutil.copytree(self.base_template_dir, site_output_dir)
        
        # Update profile data
        profile_data_path = site_output_dir / "data" / "profile.json"
        with open(profile_data_path, 'w', encoding='utf-8') as f:
            json.dump(resume_data, f, indent=2, ensure_ascii=False)
        
        # Apply theme customizations
        self._apply_theme(site_output_dir, theme)
        
        # Generate additional files
        self._generate_readme(site_output_dir, resume_data)
        self._generate_deployment_configs(site_output_dir)
        
        print(f"✅ Website generated successfully at: {site_output_dir}")
        return str(site_output_dir)
    
    def _apply_theme(self, site_dir: Path, theme: str):
        """Apply theme-specific customizations"""
        themes = {
            "modern": {
                "primary_color": "#3b82f6",
                "accent_color": "#10b981",
                "font_family": "'Inter', sans-serif"
            },
            "professional": {
                "primary_color": "#1f2937",
                "accent_color": "#6366f1",
                "font_family": "'Roboto', sans-serif"
            },
            "creative": {
                "primary_color": "#8b5cf6",
                "accent_color": "#f59e0b",
                "font_family": "'Poppins', sans-serif"
            },
            "minimal": {
                "primary_color": "#374151",
                "accent_color": "#059669",
                "font_family": "'Source Sans Pro', sans-serif"
            }
        }
        
        theme_config = themes.get(theme, themes["modern"])
        
        # Update CSS variables
        css_file = site_dir / "assets" / "style.css"
        if css_file.exists():
            css_content = css_file.read_text()
            
            # Replace CSS custom properties
            css_content = css_content.replace(
                "--primary-color: #3b82f6;",
                f"--primary-color: {theme_config['primary_color']};"
            )
            
            css_file.write_text(css_content)
    
    def _generate_readme(self, site_dir: Path, resume_data: Dict[str, Any]):
        """Generate README file for the website"""
        name = resume_data.get("personal", {}).get("name", "Portfolio")
        
        readme_content = f"""# {name} - Dynamic Portfolio Website

This is a dynamically generated portfolio website created from resume data.

## Features

- 📱 Responsive design that works on all devices
- 🌙 Dark/Light theme toggle
- 🚀 Smooth animations and transitions
- 📧 Contact form integration
- 🔍 SEO optimized
- ⚡ Fast loading and performance optimized

## Quick Start

1. Open `index.html` in your browser to view locally
2. Deploy to any static hosting service (Netlify, Vercel, GitHub Pages)

## Customization

- Edit `data/profile.json` to update your information
- Modify `assets/style.css` for styling changes
- Update `assets/profile.jpg` with your photo

## Deployment

### GitHub Pages
1. Create a new repository
2. Upload all files
3. Enable GitHub Pages in repository settings

### Netlify
1. Drag and drop the entire folder to netlify.com/drop
2. Your site will be live instantly with form handling

### Vercel
1. Install Vercel CLI: `npm i -g vercel`
2. Run `vercel` in the project directory
3. Follow the prompts

## Contact Form

The contact form is set up for Netlify Forms by default. For other platforms:
- Update the form action in `index.html`
- Or integrate with your preferred form handling service

## License

This website template is open source and available under the MIT License.

---

Generated by Dynamic Website Generator
"""
        
        readme_file = site_dir / "README.md"
        readme_file.write_text(readme_content)
    
    def _generate_deployment_configs(self, site_dir: Path):
        """Generate deployment configuration files"""
        
        # Netlify configuration
        netlify_config = """[build]
  publish = "."

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[build.environment]
  NODE_VERSION = "18"

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
"""
        
        (site_dir / "netlify.toml").write_text(netlify_config)
        
        # Vercel configuration
        vercel_config = """{
  "version": 2,
  "name": "dynamic-portfolio",
  "builds": [
    {
      "src": "**",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/$1"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        }
      ]
    }
  ]
}"""
        
        (site_dir / "vercel.json").write_text(vercel_config)
        
        # GitHub Pages workflow
        github_dir = site_dir / ".github" / "workflows"
        github_dir.mkdir(parents=True, exist_ok=True)
        
        github_workflow = """name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Node.js
      uses: actions/setup-node@v2
      with:
        node-version: '18'
    
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./
"""
        
        (github_dir / "deploy.yml").write_text(github_workflow)
    
    def create_zip_package(self, site_dir: str) -> str:
        """Create a downloadable zip package of the website"""
        site_path = Path(site_dir)
        zip_path = site_path.with_suffix('.zip')
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in site_path.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(site_path)
                    zipf.write(file_path, arcname)
        
        print(f"📦 Website package created: {zip_path}")
        return str(zip_path)
    
    def preview_website(self, site_dir: str, port: int = 8000):
        """Start a local server to preview the website"""
        import webbrowser
        import http.server
        import socketserver
        import threading
        import os
        
        # Change to site directory
        original_dir = os.getcwd()
        os.chdir(site_dir)
        
        try:
            # Create server
            handler = http.server.SimpleHTTPRequestHandler
            with socketserver.TCPServer(("", port), handler) as httpd:
                print(f"🌐 Starting preview server at http://localhost:{port}")
                print("Press Ctrl+C to stop the server")
                
                # Open browser
                webbrowser.open(f"http://localhost:{port}")
                
                # Start server
                httpd.serve_forever()
                
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")
        except OSError as e:
            print(f"Error starting server: {e}")
            print(f"Try a different port: python {__file__} --preview {site_dir} --port {port + 1}")
        finally:
            os.chdir(original_dir)

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Generate dynamic portfolio websites from resumes")
    parser.add_argument("resume_file", help="Path to resume file (PDF, DOCX, TXT)")
    parser.add_argument("--output", "-o", default="portfolio", help="Output directory name")
    parser.add_argument("--theme", "-t", choices=["modern", "professional", "creative", "minimal"], 
                       default="modern", help="Website theme")
    parser.add_argument("--preview", "-p", action="store_true", help="Preview the generated website")
    parser.add_argument("--port", type=int, default=8000, help="Preview server port")
    parser.add_argument("--zip", "-z", action="store_true", help="Create zip package")
    
    args = parser.parse_args()
    
    # Check if resume file exists
    if not Path(args.resume_file).exists():
        print(f"❌ Error: Resume file '{args.resume_file}' not found")
        return 1
    
    # Create generator
    generator = DynamicWebsiteGenerator()
    
    print(f"🔄 Processing resume: {args.resume_file}")
    
    try:
        # Extract resume data
        resume_data = generator.extract_resume_data(args.resume_file)
        
        # Generate website
        site_dir = generator.generate_website(resume_data, args.output, args.theme)
        
        # Create zip if requested
        if args.zip:
            zip_path = generator.create_zip_package(site_dir)
            print(f"📦 Download package: {zip_path}")
        
        # Preview if requested
        if args.preview:
            generator.preview_website(site_dir, args.port)
        else:
            print(f"\n🚀 Next steps:")
            print(f"   • Open {site_dir}/index.html in your browser")
            print(f"   • Preview: python {__file__} --preview {site_dir}")
            print(f"   • Deploy to Netlify: drag folder to netlify.com/drop")
            print(f"   • Deploy to GitHub Pages: upload to repository and enable Pages")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error generating website: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
