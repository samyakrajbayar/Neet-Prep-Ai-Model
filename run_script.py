# Main Runner Script for NEET AI Preparation System
import os
import sys
import subprocess
import threading
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def print_banner():
    """Print system banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║            🎓 NEET AI PREPARATION SYSTEM 🎓                  ║
    ║                                                              ║
    ║     Your AI-Powered Companion for NEET Success              ║
    ║                                                              ║
    ║  Features:                                                   ║
    ║  • Previous Year Questions (PYQs)                            ║
    ║  • AI Question Generation                                    ║
    ║  • Discord Bot Integration                                   ║
    ║  • Progress Tracking                                         ║
    ║  • Smart Analytics                                           ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_requirements():
    """Check if all requirements are satisfied"""
    print("🔍 Checking system requirements...")
    
    required_packages = [
        'discord.py', 'openai', 'requests', 'beautifulsoup4', 
        'python-dotenv', 'sqlite3'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'sqlite3':
                import sqlite3
            else:
                __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n🚨 Missing packages: {', '.join(missing_packages)}")
        print("📦 Installing missing packages...")
        
        for package in missing_packages:
            if package != 'sqlite3':  # sqlite3 is built-in
                try:
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                    print(f"✅ Installed {package}")
                except subprocess.CalledProcessError as e:
                    print(f"❌ Failed to install {package}: {e}")
                    return False
    
    return True

def check_environment():
    """Check environment variables"""
    print("\n🔧 Checking environment configuration...")
    
    discord_token = os.getenv('DISCORD_TOKEN')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not discord_token or discord_token == 'your_discord_bot_token_here':
        print("⚠️  Discord token not configured")
        print("   Discord bot features will be disabled")
        print("   Set DISCORD_TOKEN in .env file to enable")
    else:
        print("✅ Discord token configured")
    
    if not openai_key or openai_key == 'your_openai_api_key_here':
        print("⚠️  OpenAI API key not configured")
        print("   AI question generation will be disabled")
        print("   Set OPENAI_API_KEY in .env file to enable")
    else:
        print("✅ OpenAI API key configured")
    
    # Check database
    db_path = os.getenv('DATABASE_PATH', 'neet_prep.db')
    if os.path.exists(db_path):
        print("✅ Database file exists")
    else:
        print("⚠️  Database will be created on first run")
    
    return True

def setup_database():
    """Initialize database if needed"""
    print("\n📊 Setting up database...")
    
    try:
        from main import NEETDatabase
        db = NEETDatabase('neet_prep.db')
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def run_console_mode():
    """Run console application"""
    try:
        from main import NEETConsoleApp
        app = NEETConsoleApp()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye! Good luck with your NEET preparation!")
    except Exception as e:
        print(f"❌ Console mode error: {e}")

def run_discord_bot():
    """Run Discord bot"""
    discord_token = os.getenv('DISCORD_TOKEN')
    
    if not discord_token or discord_token == 'your_discord_bot_token_here':
        print("❌ Discord token not configured!")
        print("Please set DISCORD_TOKEN in your .env file")
        return
    
    try:
        from main import bot
        print("🤖 Starting Discord bot...")
        print("Bot will be available in your Discord server")
        print("Press Ctrl+C to stop the bot")
        bot.run(discord_token)
    except KeyboardInterrupt:
        print("\n🤖 Discord bot stopped")
    except Exception as e:
        print(f"❌ Discord bot error: {e}")

def run_web_interface():
    """Run web interface for Replit"""
    try:
        from web_interface import app
        print("🌐 Starting web interface...")
        print("Web interface will be available at your Replit URL")
        app.run(host='0.0.0.0', port=8080, debug=False)
    except Exception as e:
        print(f"❌ Web interface error: {e}")

def run_both_modes():
    """Run both console and Discord bot in parallel"""
    print("🚀 Starting both console and Discord bot modes...")
    
    # Start Discord bot in a separate thread
    discord_thread = threading.Thread(target=run_discord_bot, daemon=True)
    discord_thread.start()
    
    # Give Discord bot time to start
    time.sleep(2)
    
    # Run console in main thread
    run_console_mode()

def show_help():
    """Show help information"""
    help_text = """
🆘 HELP - NEET AI Preparation System

📚 SYSTEM OVERVIEW:
This system provides comprehensive NEET preparation tools including:
- Practice with previous year questions (PYQs)
- AI-generated questions in NEET style
- Progress tracking and analytics
- Discord bot for group study
- Complete NEET syllabus reference

🎮 USAGE MODES:

1. CONSOLE APPLICATION
   - Interactive command-line interface
   - Practice quizzes with immediate feedback
   - Add custom questions
   - View detailed progress reports
   - Browse complete syllabus

2. DISCORD BOT
   - Multi-user quiz sessions
   - Reaction-based question answering
   - Real-time progress tracking
   - AI question generation on demand
   - Group study features

3. WEB INTERFACE (Replit only)
   - Visual dashboard
   - System status monitoring
   - Quick statistics overview
   - Easy configuration management

🤖 DISCORD BOT COMMANDS:
- !start - Get started with the bot
- !quiz [subject] - Start a practice quiz
- !generate [subject] [topic] - Generate AI questions
- !syllabus [subject] - View syllabus
- !progress - Check your progress

⚙️ CONFIGURATION:
1. Copy .env.example to .env
2. Add your Discord bot token
3. Add your OpenAI API key
4. Run the application

🔗 GETTING API KEYS:
Discord: https://discord.com/developers/applications
OpenAI: https://platform.openai.com/api-keys

📈 PROGRESS TRACKING:
- Subject-wise accuracy tracking
- Topic-wise strength/weakness analysis
- Study streak monitoring
- Personalized recommendations

🆘 TROUBLESHOOTING:
- Ensure all dependencies are installed
- Check your API keys in .env file
- Verify Discord bot permissions
- Check internet connection for AI features

💡 TIPS:
- Start with easier topics to build confidence
- Use AI generation for additional practice
- Review explanations for wrong answers
- Track your progress regularly
- Join study groups via Discord bot

📞 SUPPORT:
- Check README.md for detailed documentation
- Create issues on GitHub for bugs
- Join community Discord for help

Good luck with your NEET preparation! 🎯
"""
    print(help_text)

def main():
    """Main application entry point"""
    print_banner()
    
    # System checks
    if not check_requirements():
        print("❌ System requirements not met. Please install missing packages.")
        return
    
    if not check_environment():
        print("❌ Environment configuration issues detected.")
    
    if not setup_database():
        print("❌ Database setup failed.")
        return
    
    print("\n" + "="*60)
    print("🚀 NEET AI PREPARATION SYSTEM - READY TO LAUNCH!")
    print("="*60)
    
    while True:
        print("\n📋 SELECT MODE:")
        print("1. 💻 Console Application (Interactive CLI)")
        print("2. 🤖 Discord Bot (Multi-user)")
        print("3. 🌐 Web Interface (Replit Dashboard)")
        print("4. 🔄 Both Console + Discord Bot")
        print("5. 🔧 System Configuration")
        print("6. 📚 Run PYQ Scraper")
        print("7. 🆘 Help & Documentation")
        print("8. 🚪 Exit")
        
        choice = input("\n👆 Enter your choice (1-8): ").strip()
        
        if choice == '1':
            print("\n🎯 Starting Console Application...")
            run_console_mode()
        
        elif choice == '2':
            print("\n🤖 Starting Discord Bot...")
            run_discord_bot()
        
        elif choice == '3':
            if os.getenv('REPLIT_ENV'):
                print("\n🌐 Starting Web Interface...")
                run_web_interface()
            else:
                print("❌ Web interface is only available on Replit")
                print("💡 Try running on Replit for web interface access")
        
        elif choice == '4':
            run_both_modes()
        
        elif choice == '5':
            print("\n🔧 System Configuration:")
            check_environment()
            print("\n💡 Edit .env file to update configuration")
        
        elif choice == '6':
            print("\n📚 Starting PYQ Scraper...")
            try:
                from pyq_scraper import main as scraper_main
                scraper_main()
            except ImportError:
                print("❌ PYQ scraper not available")
            except Exception as e:
                print(f"❌ Scraper error: {e}")
        
        elif choice == '7':
            show_help()
        
        elif choice == '8':
            print("\n👋 Thank you for using NEET AI Preparation System!")
            print("🎯 Best of luck with your NEET preparation!")
            break
        
        else:
            print("❌ Invalid choice! Please select 1-8")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Keep preparing for NEET success! 🎯")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("🆘 Please check your configuration and try again")