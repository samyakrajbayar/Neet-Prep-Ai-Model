# 🎓 NEET AI Preparation System

An AI-powered comprehensive preparation system for NEET (National Eligibility cum Entrance Test) with Discord bot integration and intelligent question generation.

## 🚀 Features

### 📚 Core Features
- **Previous Year Questions (PYQs)**: Comprehensive database of NEET previous year questions
- **AI Question Generation**: Generate new questions in PYQ style using OpenAI GPT
- **Multi-Platform**: Console application, Discord bot, and web interface (Replit)
- **Progress Tracking**: Track performance across subjects and topics
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

### 🌐 Web Interface Features (Replit)
- Visual dashboard for system statistics
- Configuration status monitoring
- Question browsing
- Application launching

## 🛠️ Installation

### For Replit (Recommended)
1. Fork/Import this repository to Replit
2. Run the setup script:
   ```bash
   python setup_replit.py
   ```
3. Configure API keys in `.env`
4. Run the application:
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
   # Edit .env with API keys
   ```
4. Run the application:
   ```bash
   python main.py
   ```

## ⚙️ Configuration

### Required API Keys
1. **Discord Bot Token**
   - Create at [Discord Developer Portal](https://discord.com/developers/applications)
   - Add to `.env` as `DISCORD_TOKEN`
2. **OpenAI API Key**
   - Create at [OpenAI Platform](https://platform.openai.com)
   - Add to `.env` as `OPENAI_API_KEY`

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
# Select option 1
```
**Options:**
1. Practice Quiz - Subject-wise or mixed
2. View Syllabus - NEET syllabus reference
3. Generate AI Questions - Create new questions
4. View Progress - Track performance
5. Add Custom Question - Add your own questions

### Discord Bot
```bash
python main.py
# Select option 2
```
**Commands:**
- `!start` - Welcome message and help
- `!quiz [subject]` - Start practice quiz
- `!pyq [subject]` - Get previous year questions
- `!syllabus [subject]` - View syllabus
- `!generate [subject] [topic]` - Generate AI questions
- `!progress` - Check progress

### Web Interface (Replit)
Access at Replit URL to:
- View system statistics
- Check configuration status
- Browse questions
- Launch applications

## 📊 Database Schema

### Questions Table
- `id`: Unique identifier
- `subject`: Physics/Chemistry/Biology
- `topic`: Specific topic
- `question_text`: Question content
- `options`: JSON array of 4 options
- `correct_answer`: Index of correct option (0-3)
- `explanation`: Detailed explanation
- `year`: Question year
- `difficulty`: Easy/Medium/Hard
- `is_pyq`: Boolean for previous year question

### User Progress Table
- `user_id`: User identifier
- `subject_progress`: JSON object tracking subject progress
- `total_questions_attempted`: Total questions answered
- `correct_answers`: Number of correct answers
- `last_study_date`: Last activity date
- `weak_topics`: JSON array of topics needing improvement
- `strong_topics`: JSON array of mastered topics

## 🔧 Advanced Features

### AI Question Generation
Uses OpenAI GPT to generate NEET-style questions:
- Subject-specific
- Topic-focused
- Difficulty control
- Automatic explanations

### Progress Analytics
- Real-time performance tracking
- Subject-wise accuracy
- Topic strength/weakness analysis
- Study streak tracking
- Personalized recommendations

### Question Import
- PDF parsing for PYQs
- Web scraping for question banks
- CSV import for bulk questions
- Manual question addition

## 📝 License
MIT License - see LICENSE file for details.
