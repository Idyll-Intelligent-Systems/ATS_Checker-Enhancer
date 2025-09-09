#!/bin/bash

# Quick Start Script for Dynamic Portfolio Website Generator
# Run this script to quickly generate a portfolio website

echo "🌟 Dynamic Portfolio Website Generator - Quick Start"
echo "===================================================="
echo

# Check if a resume file is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <resume_file> [theme] [output_name]"
    echo ""
    echo "Examples:"
    echo "  $0 resume.pdf"
    echo "  $0 resume.pdf modern my-awesome-portfolio"
    echo "  $0 resume.docx professional"
    echo ""
    echo "Available themes: modern, professional, creative, minimal"
    echo ""
    exit 1
fi

RESUME_FILE="$1"
THEME="${2:-modern}"
OUTPUT_NAME="${3:-portfolio}"

# Check if resume file exists
if [ ! -f "$RESUME_FILE" ]; then
    echo "❌ Error: Resume file '$RESUME_FILE' not found!"
    exit 1
fi

echo "📄 Resume file: $RESUME_FILE"
echo "🎨 Theme: $THEME"
echo "📂 Output name: $OUTPUT_NAME"
echo ""

# Generate the website
echo "🔄 Generating your portfolio website..."
if python3 dynamic_website_generator.py "$RESUME_FILE" --output "$OUTPUT_NAME" --theme "$THEME" --zip; then
    echo ""
    echo "🎉 Success! Your portfolio website has been generated!"
    echo ""
    echo "📁 Website location: generated_websites/$OUTPUT_NAME/"
    echo "📦 Download package: generated_websites/$OUTPUT_NAME.zip"
    echo ""
    echo "🚀 Next steps:"
    echo "1. Preview: python3 dynamic_website_generator.py --preview generated_websites/$OUTPUT_NAME"
    echo "2. Deploy to Netlify: Drag the zip file to netlify.com/drop"
    echo "3. Upload to GitHub: Create a repo and enable GitHub Pages"
    echo ""
    
    # Ask if user wants to preview
    read -p "🌐 Would you like to preview the website now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Starting preview server..."
        python3 dynamic_website_generator.py --preview "generated_websites/$OUTPUT_NAME"
    fi
else
    echo ""
    echo "❌ Failed to generate website. Please check the error messages above."
    exit 1
fi
