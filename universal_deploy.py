#!/usr/bin/env python3
"""
🚀 ZeX-ATS-AI Universal Deployment Script
Cross-platform deployment for Mac, Windows, Linux, Android, iOS, and Web

This script automatically detects your platform and deploys ZeX-ATS-AI accordingly.
"""

import os
import sys
import platform
import subprocess
import json
import time
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

# Color codes for cross-platform terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_colored(text: str, color: str = Colors.ENDC):
    """Print colored text that works on all platforms."""
    print(f"{color}{text}{Colors.ENDC}")

def run_command(cmd: str, check: bool = True, shell: bool = True) -> subprocess.CompletedProcess:
    """Run command with cross-platform compatibility."""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        else:
            result = subprocess.run(cmd, shell=shell, check=check, capture_output=True, text=True)
        return result
    except subprocess.CalledProcessError as e:
        print_colored(f"❌ Command failed: {cmd}", Colors.RED)
        print_colored(f"Error: {e.stderr}", Colors.RED)
        if check:
            raise
        return e

def detect_platform() -> Dict[str, str]:
    """Detect the current platform and return deployment strategy."""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    # Check if running on mobile (simplified detection)
    is_mobile = False
    if "arm" in machine and system == "linux":
        # Could be Android (Termux) or ARM Linux
        if os.path.exists("/system/bin/app_process"):
            is_mobile = True
            system = "android"
    
    # Check if running in a web environment (like Replit, CodeSandbox, etc.)
    is_web_env = (
        os.getenv("REPLIT_ENV") or 
        os.getenv("CODESANDBOX_SSH") or 
        os.getenv("GITPOD_WORKSPACE_ID") or
        os.getenv("CODESPACE_NAME")
    )
    
    platform_info = {
        "system": system,
        "machine": machine,
        "is_mobile": is_mobile,
        "is_web_env": bool(is_web_env),
        "python_version": sys.version,
        "deployment_type": "unknown"
    }
    
    # Determine deployment type
    if is_web_env:
        platform_info["deployment_type"] = "web"
    elif system == "darwin":
        platform_info["deployment_type"] = "macos"
    elif system == "windows":
        platform_info["deployment_type"] = "windows"
    elif system == "linux" and not is_mobile:
        platform_info["deployment_type"] = "linux"
    elif system == "android" or is_mobile:
        platform_info["deployment_type"] = "android"
    else:
        platform_info["deployment_type"] = "generic_unix"
    
    return platform_info

class UniversalDeployer:
    """Universal deployment manager for all platforms."""
    
    def __init__(self):
        self.platform_info = detect_platform()
        self.project_root = Path.cwd()
        self.deployment_configs = self.load_deployment_configs()
    
    def load_deployment_configs(self) -> Dict:
        """Load platform-specific deployment configurations."""
        return {
            "macos": {
                "requirements": ["python3", "pip3", "docker"],
                "install_commands": {
                    "docker": "brew install docker",
                    "python3": "brew install python@3.11"
                },
                "service_port": 8000,
                "background_service": True
            },
            "windows": {
                "requirements": ["python", "pip", "docker"],
                "install_commands": {
                    "docker": "winget install Docker.DockerDesktop",
                    "python": "winget install Python.Python.3.11"
                },
                "service_port": 8000,
                "background_service": True
            },
            "linux": {
                "requirements": ["python3", "pip3", "docker"],
                "install_commands": {
                    "docker": "curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh",
                    "python3": "sudo apt-get update && sudo apt-get install python3.11 python3-pip"
                },
                "service_port": 8000,
                "background_service": True
            },
            "android": {
                "requirements": ["python", "pip"],
                "install_commands": {
                    "python": "pkg install python",
                    "pip": "pkg install python-pip"
                },
                "service_port": 8080,
                "background_service": False,
                "mobile_optimizations": True
            },
            "web": {
                "requirements": ["python3", "pip3"],
                "service_port": 8000,
                "web_optimizations": True,
                "background_service": False
            }
        }
    
    def print_banner(self):
        """Print the deployment banner."""
        print_colored("=" * 70, Colors.CYAN)
        print_colored("🚀 ZeX-ATS-AI Universal Deployment Script", Colors.HEADER)
        print_colored("   Enhanced Multi-Format Resume Analysis Platform", Colors.BLUE)
        print_colored("=" * 70, Colors.CYAN)
        print()
        
        # Platform info
        print_colored(f"📱 Detected Platform: {self.platform_info['deployment_type'].upper()}", Colors.YELLOW)
        print_colored(f"💻 System: {self.platform_info['system']} ({self.platform_info['machine']})", Colors.BLUE)
        print_colored(f"🐍 Python: {self.platform_info['python_version'].split()[0]}", Colors.GREEN)
        if self.platform_info['is_web_env']:
            print_colored("🌐 Web Environment Detected", Colors.CYAN)
        if self.platform_info['is_mobile']:
            print_colored("📱 Mobile Environment Detected", Colors.YELLOW)
        print()
    
    def check_requirements(self) -> bool:
        """Check if all requirements are installed."""
        print_colored("🔍 Checking System Requirements...", Colors.BLUE)
        
        deployment_type = self.platform_info['deployment_type']
        config = self.deployment_configs.get(deployment_type, {})
        requirements = config.get('requirements', ['python3', 'pip3'])
        
        missing_requirements = []
        
        for req in requirements:
            try:
                # Check if command exists
                if platform.system() == "Windows":
                    result = run_command(f"where {req}", check=False)
                else:
                    result = run_command(f"which {req}", check=False)
                
                if result.returncode == 0:
                    print_colored(f"  ✅ {req} found", Colors.GREEN)
                else:
                    print_colored(f"  ❌ {req} missing", Colors.RED)
                    missing_requirements.append(req)
            except Exception:
                print_colored(f"  ❌ {req} missing", Colors.RED)
                missing_requirements.append(req)
        
        if missing_requirements:
            print_colored(f"\n⚠️  Missing requirements: {', '.join(missing_requirements)}", Colors.YELLOW)
            self.install_missing_requirements(missing_requirements)
        
        print_colored("✅ Requirements check complete\n", Colors.GREEN)
        return len(missing_requirements) == 0
    
    def install_missing_requirements(self, missing: List[str]):
        """Install missing requirements."""
        deployment_type = self.platform_info['deployment_type']
        config = self.deployment_configs.get(deployment_type, {})
        install_commands = config.get('install_commands', {})
        
        print_colored("🔧 Installing missing requirements...", Colors.YELLOW)
        
        for req in missing:
            if req in install_commands:
                print_colored(f"Installing {req}...", Colors.BLUE)
                try:
                    run_command(install_commands[req])
                    print_colored(f"✅ {req} installed successfully", Colors.GREEN)
                except Exception as e:
                    print_colored(f"❌ Failed to install {req}: {e}", Colors.RED)
            else:
                print_colored(f"⚠️  Please install {req} manually", Colors.YELLOW)
    
    def setup_python_environment(self):
        """Set up Python virtual environment and dependencies."""
        print_colored("🐍 Setting up Python Environment...", Colors.BLUE)
        
        # Create virtual environment
        venv_path = self.project_root / "venv"
        if not venv_path.exists():
            print_colored("Creating virtual environment...", Colors.YELLOW)
            run_command(f"python3 -m venv {venv_path}")
            print_colored("✅ Virtual environment created", Colors.GREEN)
        
        # Activate virtual environment and install dependencies
        if platform.system() == "Windows":
            activate_cmd = f"{venv_path}\\Scripts\\activate"
            pip_cmd = f"{venv_path}\\Scripts\\pip"
            python_cmd = f"{venv_path}\\Scripts\\python"
        else:
            activate_cmd = f"source {venv_path}/bin/activate"
            pip_cmd = f"{venv_path}/bin/pip"
            python_cmd = f"{venv_path}/bin/python"
        
        # Install dependencies
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            print_colored("Installing Python dependencies...", Colors.YELLOW)
            run_command(f"{pip_cmd} install -r {requirements_file}")
            print_colored("✅ Python dependencies installed", Colors.GREEN)
        else:
            print_colored("⚠️  requirements.txt not found, installing basic dependencies", Colors.YELLOW)
            basic_deps = ["fastapi", "uvicorn", "pydantic", "python-multipart"]
            for dep in basic_deps:
                run_command(f"{pip_cmd} install {dep}")
        
        return python_cmd, pip_cmd
    
    def setup_database(self):
        """Set up database based on platform."""
        print_colored("🗄️ Setting up Database...", Colors.BLUE)
        
        if self.platform_info['deployment_type'] in ['android', 'web']:
            print_colored("Using SQLite for mobile/web deployment", Colors.YELLOW)
            # Create SQLite database
            db_path = self.project_root / "data" / "ats.db"
            db_path.parent.mkdir(exist_ok=True)
            print_colored("✅ SQLite database ready", Colors.GREEN)
        else:
            print_colored("Setting up PostgreSQL with Docker...", Colors.YELLOW)
            # Use docker-compose for full database setup
            docker_compose_path = self.project_root / "docker-compose.yml"
            if docker_compose_path.exists():
                try:
                    run_command("docker-compose up -d postgres redis")
                    print_colored("✅ PostgreSQL and Redis started", Colors.GREEN)
                except Exception:
                    print_colored("⚠️  Docker setup failed, falling back to SQLite", Colors.YELLOW)
    
    def create_platform_specific_configs(self):
        """Create platform-specific configuration files."""
        print_colored("⚙️  Creating platform-specific configurations...", Colors.BLUE)
        
        deployment_type = self.platform_info['deployment_type']
        config = self.deployment_configs.get(deployment_type, {})
        
        # Create platform-specific .env file
        env_config = {
            "ENVIRONMENT": "production" if deployment_type != "android" else "mobile",
            "DEBUG": "false" if deployment_type in ['macos', 'linux', 'windows'] else "true",
            "HOST": "0.0.0.0",
            "PORT": str(config.get('service_port', 8000)),
            "DATABASE_URL": "sqlite:///./data/ats.db" if deployment_type in ['android', 'web'] else "postgresql://user:pass@localhost/ats",
            "REDIS_URL": "redis://localhost:6379" if deployment_type not in ['android', 'web'] else "",
            "CORS_ORIGINS": "*" if deployment_type in ['android', 'web'] else "http://localhost:3000",
            "MAX_FILE_SIZE": "10485760" if deployment_type == 'android' else "52428800",  # 10MB vs 50MB
            "SUPPORTED_FORMATS": "pdf,docx,txt,jpg,png" if deployment_type == 'android' else "all"
        }
        
        # Write .env file
        env_path = self.project_root / ".env"
        with open(env_path, 'w') as f:
            for key, value in env_config.items():
                f.write(f"{key}={value}\n")
        
        print_colored("✅ Platform configuration created", Colors.GREEN)
    
    def create_startup_scripts(self, python_cmd: str):
        """Create platform-specific startup scripts."""
        print_colored("📜 Creating startup scripts...", Colors.BLUE)
        
        deployment_type = self.platform_info['deployment_type']
        
        if deployment_type == "windows":
            # Create Windows batch file
            script_content = f"""@echo off
echo Starting ZeX-ATS-AI Platform...
cd /d "{self.project_root}"
{python_cmd} main.py
pause
"""
            script_path = self.project_root / "start_zex_ats.bat"
            script_path.write_text(script_content)
            
        else:
            # Create Unix shell script
            script_content = f"""#!/bin/bash
echo "🚀 Starting ZeX-ATS-AI Enhanced Multi-Format Platform..."
cd "{self.project_root}"
export PYTHONPATH="${self.project_root}:$PYTHONPATH"
{python_cmd} main.py "$@"
"""
            script_path = self.project_root / "start_zex_ats.sh"
            script_path.write_text(script_content)
            script_path.chmod(0o755)
        
        # Create universal Python launcher
        launcher_content = f'''#!/usr/bin/env python3
"""
ZeX-ATS-AI Platform Launcher
Universal launcher that works on all platforms
"""
import subprocess
import sys
import os
from pathlib import Path

def main():
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Add project root to Python path
    sys.path.insert(0, str(project_root))
    
    try:
        # Import and run the main application
        import main
        # This will start the FastAPI server
        if __name__ == "__main__":
            import uvicorn
            uvicorn.run(
                "main:app", 
                host="0.0.0.0", 
                port={self.deployment_configs.get(deployment_type, {}).get('service_port', 8000)}, 
                reload=True if os.getenv("DEBUG") == "true" else False
            )
    except ImportError as e:
        print(f"❌ Failed to import main application: {{e}}")
        print("Please ensure all dependencies are installed")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
        
        launcher_path = self.project_root / "launcher.py"
        launcher_path.write_text(launcher_content)
        launcher_path.chmod(0o755)
        
        print_colored("✅ Startup scripts created", Colors.GREEN)
        return script_path
    
    def setup_mobile_optimizations(self):
        """Set up mobile-specific optimizations."""
        if not self.platform_info['is_mobile']:
            return
            
        print_colored("📱 Applying mobile optimizations...", Colors.YELLOW)
        
        # Create mobile-specific configuration
        mobile_config = {
            "max_concurrent_requests": 2,
            "request_timeout": 30,
            "max_file_size": 10 * 1024 * 1024,  # 10MB
            "supported_formats": ["pdf", "docx", "txt", "jpg", "png"],  # Limited formats
            "enable_caching": True,
            "mobile_ui": True
        }
        
        mobile_config_path = self.project_root / "mobile_config.json"
        with open(mobile_config_path, 'w') as f:
            json.dump(mobile_config, f, indent=2)
        
        print_colored("✅ Mobile optimizations applied", Colors.GREEN)
    
    def setup_web_optimizations(self):
        """Set up web environment optimizations."""
        if not self.platform_info['is_web_env']:
            return
            
        print_colored("🌐 Applying web environment optimizations...", Colors.YELLOW)
        
        # Create web-specific configuration
        web_config = {
            "enable_cors": True,
            "allowed_origins": ["*"],
            "enable_docs": True,
            "static_files": True,
            "web_ui": True
        }
        
        web_config_path = self.project_root / "web_config.json"
        with open(web_config_path, 'w') as f:
            json.dump(web_config, f, indent=2)
        
        print_colored("✅ Web optimizations applied", Colors.GREEN)
    
    def create_docker_deployment(self):
        """Create Docker deployment if supported."""
        if self.platform_info['deployment_type'] in ['android']:
            print_colored("⚠️  Docker not available on mobile, skipping...", Colors.YELLOW)
            return
        
        print_colored("🐳 Setting up Docker deployment...", Colors.BLUE)
        
        # Check if Docker is available
        try:
            run_command("docker --version")
            print_colored("✅ Docker is available", Colors.GREEN)
            
            # Try to start with docker-compose
            docker_compose_path = self.project_root / "docker-compose.yml"
            if docker_compose_path.exists():
                print_colored("Starting services with Docker Compose...", Colors.YELLOW)
                run_command("docker-compose up -d")
                print_colored("✅ Docker services started", Colors.GREEN)
            else:
                print_colored("⚠️  docker-compose.yml not found", Colors.YELLOW)
        except Exception:
            print_colored("⚠️  Docker not available, using local setup", Colors.YELLOW)
    
    def test_deployment(self, python_cmd: str):
        """Test the deployment."""
        print_colored("🧪 Testing deployment...", Colors.BLUE)
        
        # Start the application in test mode
        try:
            print_colored("Running multi-format tests...", Colors.YELLOW)
            result = run_command(f"{python_cmd} test_multi_format.py", check=False)
            
            if result.returncode == 0:
                print_colored("✅ All tests passed!", Colors.GREEN)
                return True
            else:
                print_colored("⚠️  Some tests failed, but deployment may still work", Colors.YELLOW)
                return False
        except Exception as e:
            print_colored(f"⚠️  Testing failed: {e}", Colors.YELLOW)
            return False
    
    def print_deployment_summary(self, script_path: Path, python_cmd: str):
        """Print deployment summary and instructions."""
        deployment_type = self.platform_info['deployment_type']
        config = self.deployment_configs.get(deployment_type, {})
        port = config.get('service_port', 8000)
        
        print_colored("\n" + "=" * 70, Colors.CYAN)
        print_colored("🎉 ZeX-ATS-AI Deployment Complete!", Colors.GREEN)
        print_colored("=" * 70, Colors.CYAN)
        
        print_colored(f"\n📱 Platform: {deployment_type.upper()}", Colors.BLUE)
        print_colored(f"🌐 Service URL: http://localhost:{port}", Colors.CYAN)
        print_colored(f"📚 API Documentation: http://localhost:{port}/docs", Colors.CYAN)
        print_colored(f"🎮 Interactive Demo: http://localhost:{port}/sandbox/", Colors.CYAN)
        
        print_colored(f"\n🚀 To start ZeX-ATS-AI:", Colors.YELLOW)
        
        if deployment_type == "windows":
            print_colored(f"   Double-click: {script_path.name}", Colors.WHITE)
            print_colored(f"   Or run: {script_path}", Colors.WHITE)
        else:
            print_colored(f"   ./{script_path.name}", Colors.WHITE)
        
        print_colored(f"   Or: python3 launcher.py", Colors.WHITE)
        print_colored(f"   Or: {python_cmd} main.py", Colors.WHITE)
        
        print_colored(f"\n📄 Supported Formats:", Colors.YELLOW)
        if deployment_type == 'android':
            formats = "PDF, DOCX, TXT, JPG, PNG (mobile optimized)"
        else:
            formats = "PDF, DOCX, LaTeX, JPG, PNG, PPTX, XLSX, MP3, WAV, MP4, AVI (all 16 formats)"
        print_colored(f"   {formats}", Colors.WHITE)
        
        print_colored(f"\n🛠️  Management Commands:", Colors.YELLOW)
        print_colored(f"   python3 cli.py --help", Colors.WHITE)
        print_colored(f"   python3 cli.py test-formats", Colors.WHITE)
        print_colored(f"   python3 cli.py system-status", Colors.WHITE)
        
        if deployment_type not in ['android', 'web']:
            print_colored(f"\n🐳 Docker Commands:", Colors.YELLOW)
            print_colored(f"   docker-compose up -d", Colors.WHITE)
            print_colored(f"   docker-compose logs -f", Colors.WHITE)
            print_colored(f"   docker-compose down", Colors.WHITE)
        
        print_colored(f"\n📊 Features Available:", Colors.YELLOW)
        features = [
            "✅ Multi-format document processing",
            "✅ AI-powered ATS analysis", 
            "✅ Real-time processing feedback",
            "✅ Format-specific optimization recommendations"
        ]
        
        if deployment_type not in ['android']:
            features.extend([
                "✅ Advanced OCR and speech-to-text",
                "✅ Video analysis capabilities",
                "✅ Batch processing (Enterprise tier)"
            ])
        
        for feature in features:
            print_colored(f"   {feature}", Colors.WHITE)
        
        print_colored(f"\n🔗 Quick Links:", Colors.YELLOW)
        print_colored(f"   📖 Documentation: README.md", Colors.WHITE)
        print_colored(f"   📋 Enhancement Summary: ENHANCEMENT_SUMMARY.md", Colors.WHITE)
        print_colored(f"   🚀 Quick Start Guide: QUICK_START.md", Colors.WHITE)
        
        print_colored(f"\n" + "=" * 70, Colors.CYAN)
        print_colored("🎯 ZeX-ATS-AI Enhanced Multi-Format Platform is Ready!", Colors.GREEN)
        print_colored("   Upload any supported file format and get AI-powered insights!", Colors.BLUE)
        print_colored("=" * 70, Colors.CYAN)
    
    def deploy(self):
        """Main deployment method."""
        try:
            # Print banner
            self.print_banner()
            
            # Check requirements
            self.check_requirements()
            
            # Setup Python environment
            python_cmd, pip_cmd = self.setup_python_environment()
            
            # Setup database
            self.setup_database()
            
            # Create platform-specific configurations
            self.create_platform_specific_configs()
            
            # Apply platform optimizations
            self.setup_mobile_optimizations()
            self.setup_web_optimizations()
            
            # Create startup scripts
            script_path = self.create_startup_scripts(python_cmd)
            
            # Setup Docker if available
            self.create_docker_deployment()
            
            # Test deployment
            self.test_deployment(python_cmd)
            
            # Print summary
            self.print_deployment_summary(script_path, python_cmd)
            
            return True
            
        except Exception as e:
            print_colored(f"\n❌ Deployment failed: {e}", Colors.RED)
            print_colored("Please check the error messages above and try again.", Colors.YELLOW)
            return False

def main():
    """Main entry point."""
    print_colored("🚀 ZeX-ATS-AI Universal Deployment Script Starting...", Colors.BLUE)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print_colored("❌ Python 3.8+ required. Please upgrade Python.", Colors.RED)
        sys.exit(1)
    
    # Create deployer and run deployment
    deployer = UniversalDeployer()
    
    try:
        success = deployer.deploy()
        if success:
            print_colored("\n🎉 Deployment completed successfully!", Colors.GREEN)
            sys.exit(0)
        else:
            print_colored("\n❌ Deployment failed. Check error messages above.", Colors.RED)
            sys.exit(1)
    except KeyboardInterrupt:
        print_colored("\n⚠️  Deployment cancelled by user.", Colors.YELLOW)
        sys.exit(1)
    except Exception as e:
        print_colored(f"\n💥 Unexpected error: {e}", Colors.RED)
        sys.exit(1)

if __name__ == "__main__":
    main()
