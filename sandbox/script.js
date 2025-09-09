// ZeX-ATS-AI Interactive Demo - JavaScript

// Simulate AI Analysis
function analyzeResume() {
    const loading = document.getElementById('loading');
    const result = document.getElementById('analysis-result');
    
    // Show loading state
    if (loading) loading.style.display = 'block';
    if (result) result.style.display = 'none';
    
    // Simulate API processing
    setTimeout(() => {
        if (loading) loading.style.display = 'none';
        if (result) result.style.display = 'block';
        
        // Animate the ATS score
        animateATSScore(85);
        showInsights();
    }, 2500);
}

// Animate ATS Score Circle
function animateATSScore(targetScore) {
    const scoreElement = document.querySelector('.score-text');
    const circle = document.querySelector('.score-circle');
    
    if (!scoreElement || !circle) return;
    
    let currentScore = 0;
    const increment = targetScore / 50;
    
    const animation = setInterval(() => {
        currentScore += increment;
        
        if (currentScore >= targetScore) {
            currentScore = targetScore;
            clearInterval(animation);
        }
        
        scoreElement.textContent = `${Math.round(currentScore)}/100`;
        
        // Update circle gradient
        const percentage = (currentScore / 100) * 360;
        circle.style.background = `conic-gradient(#28a745 0deg ${percentage}deg, #e9ecef ${percentage}deg 360deg)`;
    }, 40);
}

// Show AI-Generated Insights
function showInsights() {
    const insights = [
        "🎯 Added 'Python' and 'Machine Learning' keywords for better ATS matching",
        "📊 Quantified achievements with specific metrics and numbers", 
        "🔧 Optimized section headers for improved ATS parsing",
        "⭐ Enhanced skill descriptions with industry-standard terminology"
    ];
    
    const container = document.getElementById('insights-container');
    if (!container) return;
    
    container.innerHTML = '';
    
    insights.forEach((insight, index) => {
        setTimeout(() => {
            const div = document.createElement('div');
            div.className = 'suggestion-item';
            div.textContent = insight;
            div.style.opacity = '0';
            div.style.transform = 'translateY(20px)';
            
            container.appendChild(div);
            
            // Animate in
            setTimeout(() => {
                div.style.transition = 'all 0.3s ease';
                div.style.opacity = '1';
                div.style.transform = 'translateY(0)';
            }, 100);
        }, index * 200);
    });
}

// Job Matching Demo
function findMatchingJobs() {
    const button = event.target;
    const originalText = button.innerHTML;
    
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> AI Processing...';
    button.disabled = true;
    
    setTimeout(() => {
        showJobResults();
        button.innerHTML = originalText;
        button.disabled = false;
    }, 2000);
}

// Display Job Results
function showJobResults() {
    const jobs = [
        {
            title: "Senior Software Engineer",
            company: "TechCorp Inc.",
            location: "San Francisco, CA",
            salary: "$120k-150k",
            match: 94,
            type: "Full-time"
        },
        {
            title: "Full Stack Developer", 
            company: "StartupXYZ",
            location: "Remote",
            salary: "$100k-130k", 
            match: 89,
            type: "Contract"
        },
        {
            title: "Python Developer",
            company: "DataCorp",
            location: "New York, NY",
            salary: "$110k-140k",
            match: 87,
            type: "Full-time"
        }
    ];
    
    const resultsContainer = document.getElementById('job-results');
    if (!resultsContainer) return;
    
    resultsContainer.innerHTML = '<h4 style="margin-bottom: 15px;">🎯 Top Job Matches:</h4>';
    
    jobs.forEach((job, index) => {
        setTimeout(() => {
            const jobCard = document.createElement('div');
            jobCard.className = 'job-match-card';
            jobCard.innerHTML = `
                <div style="background: rgba(40, 167, 69, 0.1); padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #28a745; opacity: 0; transform: translateX(-20px);">
                    <div style="display: flex; justify-content: between; align-items: start; margin-bottom: 8px;">
                        <div>
                            <strong>${job.title}</strong>
                            <div style="color: #666; font-size: 0.9rem;">${job.company}</div>
                        </div>
                        <div style="background: #28a745; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; margin-left: auto;">
                            ${job.match}% Match
                        </div>
                    </div>
                    <div style="font-size: 0.85rem; color: #666;">
                        📍 ${job.location} | 💰 ${job.salary} | ⏰ ${job.type}
                    </div>
                </div>
            `;
            
            resultsContainer.appendChild(jobCard);
            
            // Animate in
            setTimeout(() => {
                const card = jobCard.querySelector('div');
                card.style.transition = 'all 0.4s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateX(0)';
            }, 100);
        }, index * 300);
    });
    
    resultsContainer.style.display = 'block';
}

// Salary Analysis Demo
function showSalaryAnalysis() {
    const salaryData = {
        average: '$125,000',
        range: '$95k - $160k',
        percentile: '75th',
        growth: '+8.3%'
    };
    
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.8);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    `;
    
    modal.innerHTML = `
        <div style="background: white; padding: 30px; border-radius: 15px; max-width: 500px; width: 90%;">
            <h3 style="margin-bottom: 20px; text-align: center;">📊 Salary Analysis</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
                <div style="text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                    <div style="font-size: 1.5rem; font-weight: 600; color: #28a745;">${salaryData.average}</div>
                    <div style="font-size: 0.9rem; color: #666;">Average Salary</div>
                </div>
                <div style="text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                    <div style="font-size: 1.2rem; font-weight: 600; color: #667eea;">${salaryData.percentile}</div>
                    <div style="font-size: 0.9rem; color: #666;">Percentile</div>
                </div>
            </div>
            <div style="margin-bottom: 20px;">
                <strong>Salary Range:</strong> ${salaryData.range}<br>
                <strong>YoY Growth:</strong> <span style="color: #28a745;">${salaryData.growth}</span>
            </div>
            <button onclick="this.parentElement.parentElement.remove()" 
                    style="width: 100%; padding: 10px; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer;">
                Close
            </button>
        </div>
    `;
    
    document.body.appendChild(modal);
}

// File Upload Simulation
function simulateFileUpload() {
    const uploadArea = document.querySelector('.upload-area');
    if (!uploadArea) return;
    
    uploadArea.innerHTML = `
        <div style="color: #28a745;">
            <i class="fas fa-file-check" style="font-size: 3rem; margin-bottom: 15px;"></i>
            <div style="font-size: 1.1rem; margin-bottom: 10px;">Resume_JohnDoe.pdf</div>
            <div style="font-size: 0.9rem; color: #666;">Ready for AI analysis</div>
        </div>
    `;
}

// API Demo Popup
function showAPIDemo() {
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.8);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
        padding: 20px;
    `;
    
    modal.innerHTML = `
        <div style="background: white; padding: 30px; border-radius: 15px; max-width: 600px; width: 100%; max-height: 80vh; overflow-y: auto;">
            <h3 style="margin-bottom: 20px; text-align: center;">🚀 Live API Demo</h3>
            
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px; font-family: 'Courier New', monospace; font-size: 0.9rem;">
                <strong style="color: #667eea;">POST</strong> /api/v1/analyze/resume<br><br>
                
                <strong>Headers:</strong><br>
                Authorization: Bearer eyJ0eXAiOiJKV1Q...<br>
                Content-Type: multipart/form-data<br><br>
                
                <strong>Response:</strong><br>
                {<br>
                &nbsp;&nbsp;"ats_score": 85,<br>
                &nbsp;&nbsp;"processing_time": "1.2s",<br>
                &nbsp;&nbsp;"suggestions": [<br>
                &nbsp;&nbsp;&nbsp;&nbsp;"Add technical keywords",<br>
                &nbsp;&nbsp;&nbsp;&nbsp;"Quantify achievements"<br>
                &nbsp;&nbsp;],<br>
                &nbsp;&nbsp;"job_matches": 23,<br>
                &nbsp;&nbsp;"salary_estimate": "$125,000"<br>
                }
            </div>
            
            <div style="display: flex; gap: 10px;">
                <button onclick="window.open('/docs', '_blank')" 
                        style="flex: 1; padding: 12px; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer;">
                    📚 Full Documentation
                </button>
                <button onclick="this.parentElement.parentElement.parentElement.remove()" 
                        style="flex: 1; padding: 12px; background: #6c757d; color: white; border: none; border-radius: 8px; cursor: pointer;">
                    Close
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

// Initialize Demo
document.addEventListener('DOMContentLoaded', function() {
    // Add smooth animations for stats
    const stats = document.querySelectorAll('.stat-number');
    
    // Intersection Observer for animations
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateNumber(entry.target);
            }
        });
    });
    
    stats.forEach(stat => observer.observe(stat));
    
    // Add typing effect to tagline
    const tagline = document.querySelector('.tagline');
    if (tagline) {
        const text = tagline.textContent;
        tagline.textContent = '';
        
        let i = 0;
        const typeWriter = () => {
            if (i < text.length) {
                tagline.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 30);
            }
        };
        
        setTimeout(typeWriter, 1000);
    }
});

// Animate numbers
function animateNumber(element) {
    const target = element.textContent;
    const isNumber = !isNaN(target.replace(/[^0-9]/g, ''));
    
    if (isNumber) {
        const finalValue = parseInt(target.replace(/[^0-9]/g, ''));
        const suffix = target.replace(/[0-9]/g, '');
        let current = 0;
        const increment = finalValue / 40;
        
        const counter = setInterval(() => {
            current += increment;
            if (current >= finalValue) {
                current = finalValue;
                clearInterval(counter);
            }
            element.textContent = Math.round(current) + suffix;
        }, 50);
    }
}

// Export functions for global access
window.analyzeResume = analyzeResume;
window.findMatchingJobs = findMatchingJobs;
window.showSalaryAnalysis = showSalaryAnalysis;
window.simulateFileUpload = simulateFileUpload;
window.showAPIDemo = showAPIDemo;
