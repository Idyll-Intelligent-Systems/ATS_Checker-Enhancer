# Dynamic Portfolio Website Generator

Transform your resume into a stunning, professional portfolio website in seconds! This project combines the power of AI-driven resume analysis with modern web development to automatically generate personalized portfolio websites from uploaded resumes.

## 🌟 New Features Added

### 1. Personal Information Anonymization
- All personal information has been replaced with `xuser-idyll` placeholders
- Safe for sharing and demonstration purposes
- Easy to customize with real information

### 2. Dynamic Website Showcasing Shiva Kumar Veldi's Resume
A comprehensive portfolio website featuring:
- **Resume Section**: Professional experience and achievements
- **About Section**: Personal summary and core competencies
- **Contact Section**: Professional contact information
- **Social Links**: LinkedIn, GitHub, and other professional networks

### 3. Custom Dynamic Website Development Tool
- **Automated Resume Processing**: Supports PDF, DOCX, DOC, and TXT files
- **Multiple Themes**: Modern, Professional, Creative, and Minimal designs
- **Responsive Design**: Works perfectly on all devices
- **SEO Optimized**: Ready for search engine indexing
- **Deployment Ready**: Configured for Netlify, Vercel, and GitHub Pages

## 🚀 Quick Start

### Method 1: Command Line Tool

```bash
# Generate website from resume
python3 dynamic_website_generator.py path/to/resume.pdf --output my-portfolio --theme modern --zip

# Preview the generated website
python3 dynamic_website_generator.py --preview generated_websites/my-portfolio
```

### Method 2: Web API Service

```bash
# Start the API server
python3 website_generator_api.py

# Open web interface
open http://localhost:8080
```

### Method 3: Direct Web Interface

1. Open `website_generator_ui.html` in your browser
2. Upload your resume (PDF, DOCX, DOC, or TXT)
3. Choose a theme (Modern, Professional, Creative, or Minimal)
4. Click "Generate My Portfolio Website"
5. Download and deploy your website!

## 📁 Project Structure

```
ATS_Checker-Enhancer/
├── website/                          # Base website template
│   ├── index.html                   # Main HTML template
│   ├── assets/
│   │   ├── style.css               # Modern CSS with theming
│   │   ├── profile.jpg             # Placeholder profile image
│   │   └── favicon.svg             # Website favicon
│   ├── js/
│   │   ├── app.js                  # Main application logic
│   │   └── animations.js           # Smooth animations and effects
│   └── data/
│       └── profile.json            # Dynamic profile data
├── generated_websites/              # Output directory for generated sites
├── dynamic_website_generator.py     # Command-line generator tool
├── website_generator_api.py         # Web API service
├── website_generator_ui.html        # Web interface
└── README.md                       # This file
```

## 🎨 Available Themes

### Modern (Default)
- Clean, contemporary design with blue accents
- Perfect for tech professionals
- Features gradient backgrounds and smooth animations

### Professional
- Conservative, business-focused layout
- Ideal for corporate environments
- Uses neutral colors and formal typography

### Creative
- Artistic, colorful design for creative professionals
- Great for designers, artists, and creative roles
- Features bold colors and unique layouts

### Minimal
- Simple, clean layout with minimal styling
- Perfect for minimalist aesthetic
- Focuses on content with subtle design elements

## 🔧 Customization Options

### Personal Information
Edit `data/profile.json` to update:
- Personal details (name, title, contact info)
- Professional experience
- Skills and competencies
- Projects and achievements
- Education and certifications
- Social media links

### Styling
Modify `assets/style.css` to:
- Change color schemes
- Update fonts and typography
- Adjust layouts and spacing
- Add custom animations

### Content Sections
The website includes:
- **Hero Section**: Name, title, and call-to-action
- **About Section**: Summary, highlights, and values
- **Skills Section**: Technical, tools, and soft skills
- **Experience Section**: Professional timeline
- **Projects Section**: Featured work and achievements
- **Contact Section**: Contact form and information
- **Footer**: Social links and copyright

## 🌐 Deployment Options

### Netlify (Recommended)
1. Drag the generated website folder to [netlify.com/drop](https://netlify.com/drop)
2. Your site is live instantly with form handling included!

### Vercel
1. Install Vercel CLI: `npm i -g vercel`
2. Run `vercel` in the website directory
3. Follow the prompts for deployment

### GitHub Pages
1. Create a new repository
2. Upload the website files
3. Enable GitHub Pages in repository settings
4. Your site will be available at `https://username.github.io/repository-name`

### Manual Hosting
Upload the files to any web hosting service that supports static files.

## 📊 Features Included

### ✨ Core Features
- **📱 Responsive Design**: Works on all devices and screen sizes
- **🌙 Dark/Light Mode**: Theme toggle for user preference
- **🚀 Performance Optimized**: Fast loading with modern optimization
- **📧 Contact Form**: Ready for form handling services
- **🎨 Smooth Animations**: Professional transitions and effects
- **🔍 SEO Optimized**: Meta tags and structured data

### 🛠 Technical Features
- **Modern CSS**: CSS Grid, Flexbox, Custom Properties
- **Vanilla JavaScript**: No external dependencies required
- **Progressive Enhancement**: Works with JavaScript disabled
- **Accessibility**: ARIA labels and keyboard navigation
- **Print Styles**: Optimized for PDF generation

### 📈 Analytics Ready
- Google Analytics integration (add your tracking ID)
- Performance monitoring setup
- User engagement tracking capabilities

## 🔧 API Documentation

### Generate Website Endpoint

```http
POST /generate
Content-Type: multipart/form-data

file: [resume file]
theme: modern|professional|creative|minimal
output_name: portfolio-name (optional)
```

### Check Status Endpoint

```http
GET /status/{generation_id}
```

### Download Website Endpoint

```http
GET /download/{generation_id}
```

## 📝 Resume Processing

The tool automatically extracts and structures:
- **Contact Information**: Email, phone, location, social links
- **Professional Summary**: Career highlights and objectives
- **Work Experience**: Company, role, dates, responsibilities
- **Skills**: Technical, tools, and soft skills
- **Education**: Degrees, institutions, coursework
- **Projects**: Descriptions, technologies, achievements
- **Certifications**: Professional qualifications

## 🎯 Use Cases

### For Job Seekers
- Create professional online presence
- Showcase skills and experience
- Easy sharing with recruiters
- Mobile-friendly for on-the-go viewing

### For Professionals
- Build personal brand
- Portfolio for freelance work
- Professional networking
- Career advancement tool

### For Students
- Academic project showcase
- Internship applications
- Career fair presentations
- Professional development

## 🤝 Contributing

We welcome contributions! Here's how to get involved:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -m 'Add new feature'`
5. Push to the branch: `git push origin feature/new-feature`
6. Submit a pull request

### Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd ATS_Checker-Enhancer

# Install dependencies (if using the full ATS system)
pip install -r requirements.txt

# Or run standalone
python3 dynamic_website_generator.py --help
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with modern web technologies
- Inspired by professional portfolio designs
- Uses AI-powered resume processing
- Designed for developer and professional communities

## 📞 Support

For support and questions:
- Create an issue in the repository
- Email: xuser@idyll-systems.ai
- Documentation: Check the `/docs` directory

---

**Made with ❤️ by the XUser Idyll Team**

Transform your resume into a stunning portfolio today! 🚀
