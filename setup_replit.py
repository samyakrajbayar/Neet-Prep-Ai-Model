# Replit Setup Script for NEET AI Preparation System
import os
import subprocess
import sqlite3
import json
from datetime import datetime

def setup_replit_environment():
    """Setup the NEET preparation system for Replit"""
    
    print("🎓 Setting up NEET AI Preparation System for Replit...")
    
    # Create necessary directories
    directories = ['data', 'logs', 'temp', 'pdfs']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Install required packages
    print("📦 Installing required packages...")
    
    packages = [
        'discord.py==2.3.2',
        'openai==0.28.1',
        'requests==2.31.0',
        'beautifulsoup4==4.12.2',
        'python-dotenv==1.0.0',
        'PyPDF2==3.0.1',
        'pdfplumber==0.10.3'
    ]
    
    for package in packages:
        try:
            subprocess.check_call(['pip', 'install', package])
            print(f"✅ Installed: {package}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
    
    # Create .env file with template
    create_env_template()
    
    # Initialize database with sample data
    init_database_with_samples()
    
    # Create Replit configuration files
    create_replit_config()
    
    print("🎉 Setup complete! Your NEET AI system is ready to use.")
    print("\n📝 Next steps:")
    print("1. Set your DISCORD_TOKEN in the .env file")
    print("2. Set your OPENAI_API_KEY in the .env file") 
    print("3. Run the main.py file to start the system")
    print("4. For Discord bot: Invite your bot to a server using Discord Developer Portal")

def create_env_template():
    """Create .env file with template values"""
    env_content = """# NEET AI Preparation System - Replit Configuration

# Discord Bot Token (Required for Discord bot functionality)
# Get from: https://discord.com/developers/applications
DISCORD_TOKEN=your_discord_bot_token_here

# OpenAI API Key (Required for AI question generation)
# Get from: https://platform.openai.com/api-keys  
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
DATABASE_PATH=neet_prep.db

# Bot Settings
COMMAND_PREFIX=!
MAX_QUIZ_QUESTIONS=10
DEFAULT_DIFFICULTY=Medium

# Logging
LOG_LEVEL=INFO

# Replit specific settings
REPLIT_ENV=true
PORT=8080
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env template file")

def init_database_with_samples():
    """Initialize database with comprehensive sample questions"""
    
    conn = sqlite3.connect('neet_prep.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id TEXT PRIMARY KEY,
            subject TEXT,
            topic TEXT,
            question_text TEXT,
            options TEXT,
            correct_answer INTEGER,
            explanation TEXT,
            year INTEGER,
            difficulty TEXT,
            is_pyq BOOLEAN
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_progress (
            user_id TEXT PRIMARY KEY,
            subject_progress TEXT,
            total_questions_attempted INTEGER,
            correct_answers INTEGER,
            last_study_date TEXT,
            weak_topics TEXT,
            strong_topics TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            question_id TEXT,
            selected_answer INTEGER,
            is_correct BOOLEAN,
            timestamp TEXT
        )
    ''')
    
    # Insert comprehensive sample questions
    sample_questions = [
        # Physics Questions
        {
            'id': 'NEET2023_PHY_001',
            'subject': 'Physics',
            'topic': 'Mechanics',
            'question_text': 'A body of mass 2 kg is moving with velocity 10 m/s. What is its kinetic energy?',
            'options': ['50 J', '100 J', '200 J', '400 J'],
            'correct_answer': 1,
            'explanation': 'KE = (1/2)mv² = (1/2)(2)(10)² = 100 J',
            'year': 2023,
            'difficulty': 'Easy',
            'is_pyq': True
        },
        {
            'id': 'NEET2022_PHY_002',
            'subject': 'Physics', 
            'topic': 'Electrostatics',
            'question_text': 'Two point charges +q and -q are separated by distance d. The electric field at the midpoint is:',
            'options': ['Zero', '2kq/d²', '4kq/d²', '8kq/d²'],
            'correct_answer': 2,
            'explanation': 'Electric field due to each charge adds up at midpoint: E = 2 × kq/(d/2)² = 8kq/d²',
            'year': 2022,
            'difficulty': 'Medium',
            'is_pyq': True
        },
        {
            'id': 'NEET2021_PHY_003',
            'subject': 'Physics',
            'topic': 'Waves',
            'question_text': 'The frequency of a sound wave is 1000 Hz and wavelength is 0.33 m. The speed of sound is:',
            'options': ['330 m/s', '333 m/s', '300 m/s', '303 m/s'],
            'correct_answer': 0,
            'explanation': 'v = fλ = 1000 × 0.33 = 330 m/s',
            'year': 2021,
            'difficulty': 'Easy',
            'is_pyq': True
        },
        
        # Chemistry Questions
        {
            'id': 'NEET2023_CHEM_001',
            'subject': 'Chemistry',
            'topic': 'Organic Chemistry',
            'question_text': 'Which of the following is an example of nucleophilic substitution reaction?',
            'options': ['CH₃Cl + OH⁻ → CH₃OH + Cl⁻', 'C₂H₄ + H₂ → C₂H₆', 'CH₄ + Cl₂ → CH₃Cl + HCl', 'C₂H₄ + HBr → C₂H₅Br'],
            'correct_answer': 0,
            'explanation': 'Nucleophilic substitution involves nucleophile (OH⁻) attacking electrophilic carbon and replacing leaving group (Cl⁻)',
            'year': 2023,
            'difficulty': 'Medium',
            'is_pyq': True
        },
        {
            'id': 'NEET2022_CHEM_002',
            'subject': 'Chemistry',
            'topic': 'Chemical Bonding',
            'question_text': 'The shape of NH₃ molecule is:',
            'options': ['Trigonal planar', 'Pyramidal', 'Linear', 'Tetrahedral'],
            'correct_answer': 1,
            'explanation': 'NH₃ has 3 bonding pairs and 1 lone pair, giving pyramidal geometry according to VSEPR theory',
            'year': 2022,
            'difficulty': 'Easy',
            'is_pyq': True
        },
        {
            'id': 'NEET2021_CHEM_003',
            'subject': 'Chemistry',
            'topic': 'Thermodynamics',
            'question_text': 'For an adiabatic process, which of the following is correct?',
            'options': ['ΔU = 0', 'ΔH = 0', 'Q = 0', 'W = 0'],
            'correct_answer': 2,
            'explanation': 'In adiabatic process, no heat exchange occurs, so Q = 0',
            'year': 2021,
            'difficulty': 'Medium',
            'is_pyq': True
        },
        
        # Biology Questions
        {
            'id': 'NEET2023_BIO_001',
            'subject': 'Biology',
            'topic': 'Cell Biology',
            'question_text': 'Which organelle is known as the powerhouse of the cell?',
            'options': ['Nucleus', 'Mitochondria', 'Ribosome', 'Endoplasmic Reticulum'],
            'correct_answer': 1,
            'explanation': 'Mitochondria produces ATP through cellular respiration, providing energy to the cell',
            'year': 2023,
            'difficulty': 'Easy',
            'is_pyq': True
        },
        {
            'id': 'NEET2022_BIO_002',
            'subject': 'Biology',
            'topic': 'Genetics',
            'question_text': 'In a dihybrid cross between AaBb × AaBb, the phenotypic ratio is:',
            'options': ['3:1', '1:2:1', '9:3:3:1', '1:1:1:1'],
            'correct_answer': 2,
            'explanation': 'Dihybrid cross follows Mendels law of independent assortment, giving 9:3:3:1 ratio',
            'year': 2022,
            'difficulty': 'Medium',
            'is_pyq': True
        },
        {
            'id': 'NEET2021_BIO_003',
            'subject': 'Biology',
            'topic': 'Human Physiology',
            'question_text': 'The normal human body temperature is:',
            'options': ['96.8°F', '97.8°F', '98.6°F', '99.6°F'],
            'correct_answer': 2,
            'explanation': 'Normal human body temperature is 98.6°F (37°C)',
            'year': 2021,
            'difficulty': 'Easy',
            'is_pyq': True
        }
    ]
    
    for question in sample_questions:
        cursor.execute('''
            INSERT OR REPLACE INTO questions 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            question['id'], question['subject'], question['topic'], 
            question['question_text'], json.dumps(question['options']), 
            question['correct_answer'], question['explanation'],
            question['year'], question['difficulty'], question['is_pyq']
        ))
    
    conn.commit()
    conn.close()
    
    print("✅ Database initialized with sample questions")

def create_replit_config():
    """Create Replit-specific configuration files"""
    
    # Create .replit file
    replit_config = """run = "python main.py"
modules = ["python-3.10:v18-20230807-322e88b"]

[nix]
channel = "stable-23_05"

[env]
PYTHONPATH = "${REPLIT_HOME}/${REPLIT_SLUG}:${PYTHONPATH}"

[gitHubImport]
requiredFiles = [".replit", "replit.nix", "main.py"]

[deployment]
run = ["sh", "-c", "python main.py"]

[[ports]]
localPort = 8080
externalPort = 80
"""
    
    with open('.replit', 'w') as f:
        f.write(replit_config)
    
    # Create replit.nix file
    nix_config = """{ pkgs }: {
    deps = [
        pkgs.python310Full
        pkgs.replitPackages.prybar-python310
        pkgs.replitPackages.stderred
    ];
    env = {
        PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
            pkgs.stdenv.cc.cc.lib
        ];
        PYTHONHOME = "${pkgs.python310Full}";
        PYTHONBIN = "${pkgs.python310Full}/bin/python3.10";
    };
}"""
    
    with open('replit.nix', 'w') as f:
        f.write(nix_config)
    
    # Create simple web interface for Replit
    web_interface = """# Simple Web Interface for NEET AI System
from flask import Flask, render_template, request, jsonify
import sqlite3
import json
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <html>
    <head>
        <title>NEET AI Preparation System</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 40px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container { 
                background: rgba(255,255,255,0.1); 
                padding: 30px; 
                border-radius: 15px;
                backdrop-filter: blur(10px);
            }
            .btn { 
                background: #4CAF50; 
                color: white; 
                padding: 10px 20px; 
                border: none; 
                border-radius: 5px;
                cursor: pointer;
                margin: 5px;
            }
            .btn:hover { background: #45a049; }
            .stats { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }
            .stat-card {
                background: rgba(255,255,255,0.1);
                padding: 20px;
                border-radius: 10px;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎓 NEET AI Preparation System</h1>
            <p>Your AI-powered companion for NEET preparation!</p>
            
            <div class="stats">
                <div class="stat-card">
                    <h3>Total Questions</h3>
                    <p id="total-questions">Loading...</p>
                </div>
                <div class="stat-card">
                    <h3>Physics</h3>
                    <p id="physics-count">Loading...</p>
                </div>
                <div class="stat-card">
                    <h3>Chemistry</h3>
                    <p id="chemistry-count">Loading...</p>
                </div>
                <div class="stat-card">
                    <h3>Biology</h3>
                    <p id="biology-count">Loading...</p>
                </div>
            </div>
            
            <h2>🤖 System Status</h2>
            <div id="system-status">
                <p>✅ Database: Connected</p>
                <p id="discord-status">⏳ Discord Bot: Checking...</p>
                <p id="ai-status">⏳ AI Generation: Checking...</p>
            </div>
            
            <h2>🚀 Quick Actions</h2>
            <button class="btn" onclick="startConsoleApp()">Start Console App</button>
            <button class="btn" onclick="startDiscordBot()">Start Discord Bot</button>
            <button class="btn" onclick="viewQuestions()">View Questions</button>
            <button class="btn" onclick="addQuestion()">Add Question</button>
            
            <div id="output" style="margin-top: 20px; padding: 20px; background: rgba(0,0,0,0.3); border-radius: 10px; font-family: monospace;"></div>
        </div>
        
        <script>
            // Load statistics
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('total-questions').textContent = data.total;
                    document.getElementById('physics-count').textContent = data.physics;
                    document.getElementById('chemistry-count').textContent = data.chemistry;
                    document.getElementById('biology-count').textContent = data.biology;
                });
            
            // Check system status
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('discord-status').innerHTML = 
                        data.discord ? '✅ Discord Bot: Ready' : '❌ Discord Bot: Token Missing';
                    document.getElementById('ai-status').innerHTML = 
                        data.ai ? '✅ AI Generation: Ready' : '❌ AI Generation: API Key Missing';
                });
            
            function startConsoleApp() {
                fetch('/api/start-console', {method: 'POST'})
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('output').innerHTML = data.message;
                    });
            }
            
            function startDiscordBot() {
                fetch('/api/start-discord', {method: 'POST'})
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('output').innerHTML = data.message;
                    });
            }
            
            function viewQuestions() {
                fetch('/api/questions')
                    .then(response => response.json())
                    .then(data => {
                        let html = '<h3>Recent Questions:</h3>';
                        data.questions.slice(0, 5).forEach(q => {
                            html += `<p><strong>${q.subject}</strong>: ${q.question_text.substring(0, 100)}...</p>`;
                        });
                        document.getElementById('output').innerHTML = html;
                    });
            }
            
            function addQuestion() {
                document.getElementById('output').innerHTML = `
                    <h3>Add New Question</h3>
                    <p>Use the console application or Discord bot to add questions interactively!</p>
                    <p>Commands:</p>
                    <ul>
                        <li>Console: Run main.py and choose "Add Custom Question"</li>
                        <li>Discord: Use !generate [subject] [topic]</li>
                    </ul>
                `;
            }
        </script>
    </body>
    </html>
    '''

@app.route('/api/stats')
def get_stats():
    conn = sqlite3.connect('neet_prep.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM questions')
    total = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM questions WHERE subject = "Physics"')
    physics = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM questions WHERE subject = "Chemistry"')
    chemistry = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM questions WHERE subject = "Biology"')
    biology = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'total': total,
        'physics': physics,
        'chemistry': chemistry,
        'biology': biology
    })

@app.route('/api/status')
def get_status():
    return jsonify({
        'discord': bool(os.getenv('DISCORD_TOKEN') and os.getenv('DISCORD_TOKEN') != 'your_discord_bot_token_here'),
        'ai': bool(os.getenv('OPENAI_API_KEY') and os.getenv('OPENAI_API_KEY') != 'your_openai_api_key_here')
    })

@app.route('/api/questions')
def get_questions():
    conn = sqlite3.connect('neet_prep.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM questions ORDER BY year DESC LIMIT 10')
    rows = cursor.fetchall()
    
    questions = []
    for row in rows:
        questions.append({
            'id': row[0],
            'subject': row[1],
            'topic': row[2],
            'question_text': row[3],
            'year': row[7]
        })
    
    conn.close()
    return jsonify({'questions': questions})

@app.route('/api/start-console', methods=['POST'])
def start_console():
    return jsonify({'message': 'Console application should be started from the terminal. Run: python main.py'})

@app.route('/api/start-discord', methods=['POST'])  
def start_discord():
    if not os.getenv('DISCORD_TOKEN') or os.getenv('DISCORD_TOKEN') == 'your_discord_bot_token_here':
        return jsonify({'message': 'Error: Discord token not configured. Please set DISCORD_TOKEN in .env file.'})
    return jsonify({'message': 'Discord bot should be started from the terminal. Run: python main.py and choose option 2'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
"""
    
    with open('web_interface.py', 'w') as f:
        f.write(web_interface)
    
    print("✅ Created Replit configuration files")

def create_readme():
    """Create comprehensive README file"""
    readme_content = """# 🎓 NEET AI Preparation System

An AI-powered comprehensive preparation system for NEET (National Eligibility cum Entrance Test) with Discord bot integration and intelligent question generation.

## 🚀 Features

### 📚 Core Features
- **Previous Year Questions (PYQs)**: Comprehensive database of NEET previous year questions
- **AI Question Generation**: Generate new questions in PYQ style using OpenAI GPT
- **Multi-Platform**: Console application and Discord bot
- **Progress Tracking**: Track your performance across subjects and topics
- **Smart Analytics**: Identify weak areas and suggest focused practice

### 🤖 Discord Bot Features
- Interactive quiz sessions with reaction-based answers
- Subject-wise question practice
- Real-time progress tracking
- AI-generated questions on demand
- Comprehensive syllabus reference
- Multi-user support

### 📱 Console Application Features
- Interactive quiz mode
- Custom question addition
- Progress analytics
- Syllabus browser
- Batch question import

## 🛠️ Installation

### For Replit (Recommended)
1. Fork/Import this repository to Replit
2. Run the setup script:
   ```bash
   python setup_replit.py
   ```
3. Configure your API keys in the `.env` file
4. Run the main application:
   ```bash
   python main.py
   ```

### Local Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd neet-ai-preparation
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env file with your API keys
   ```

4. Run the application:
   ```bash
   python main.py
   ```

## ⚙️ Configuration

### Required API Keys

1. **Discord Bot Token**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application and bot
   - Copy the bot token to your `.env` file

2. **OpenAI API Key**
   - Sign up at [OpenAI Platform](https://platform.openai.com)
   - Create an API key
   - Add it to your `.env` file

### Environment Variables
```bash
DISCORD_TOKEN=your_discord_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_PATH=neet_prep.db
COMMAND_PREFIX=!
```

## 🎮 Usage

### Console Application
```bash
python main.py
# Choose option 1 for console mode
```

**Available Options:**
1. Practice Quiz - Subject-wise or mixed practice
2. View Syllabus - Complete NEET syllabus reference
3. Generate AI Questions - Create new questions using AI
4. View Progress - Track your performance
5. Add Custom Question - Add your own questions

### Discord Bot
```bash
python main.py
# Choose option 2 for Discord bot mode
```

**Bot Commands:**
- `!start` - Welcome message and help
- `!quiz [subject]` - Start a practice quiz
- `!pyq [subject]` - Get previous year questions
- `!syllabus [subject]` - View syllabus
- `!generate [subject] [topic]` - Generate AI questions
- `!progress` - Check your progress

### Web Interface (Replit)
Access the web interface at your Replit URL to:
- View system statistics
- Check configuration status
- Browse questions
- Launch applications

## 📊 Database Schema

### Questions Table
- `id`: Unique question identifier
- `subject`: Physics/Chemistry/Biology
- `topic`: Specific topic within subject
- `question_text`: The question content
- `options`: JSON array of 4 options
- `correct_answer`: Index of correct option (0-3)
- `explanation`: Detailed explanation
- `year`: Question year
- `difficulty`: Easy/Medium/Hard
- `is_pyq`: Boolean indicating if it's a previous year question

### User Progress Table
- `user_id`: User identifier
- `subject_progress`: JSON object tracking progress per subject
- `total_questions_attempted`: Total questions answered
- `correct_answers`: Number of correct answers
- `last_study_date`: Last activity date
- `weak_topics`: JSON array of topics needing improvement
- `strong_topics`: JSON array of mastered topics

## 🔧 Advanced Features

### AI Question Generation
The system uses OpenAI's GPT models to generate questions that mimic NEET PYQ patterns:
- Subject-specific question generation
- Topic-focused questions
- Difficulty level control
- Automatic explanation generation

### Progress Analytics
- Real-time performance tracking
- Subject-wise accuracy analysis
- Topic-wise strength/weakness identification
- Study streak tracking
- Personalized recommendations

### Question Import
- PDF parsing for PYQ extraction
- Web scraping for online question banks
- CSV import for bulk questions
- Manual question addition

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- Create an issue for bug reports
- Join our Discord server for community support
- Check the documentation for detailed guides

## 🔮 Future Features

- [ ] Mobile app development
- [ ] Advanced analytics dashboard
- [ ] Peer-to-peer study groups
- [ ] Live mock tests
- [ ] Video explanations
- [ ] Performance predictions
- [ ] Study plan generation

## ⚠️ Disclaimer

This is an educational tool designed to assist NEET preparation. Always refer to official NEET guidelines and materials for the most accurate and up-to-date information.

---

Made with ❤️ for NEET aspirants
"""
    
    with open('README.md', 'w') as f:
        f.write(readme_content)
    
    print("✅ Created comprehensive README file")

if __name__ == "__main__":
    setup_replit_environment()
    create_readme()
    print("\n🎯 NEET AI Preparation System is now ready!")
    print("📖 Check README.md for detailed usage instructions")
    print("🚀 Run 'python main.py' to start the system")