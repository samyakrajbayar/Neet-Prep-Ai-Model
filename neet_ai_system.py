# NEET AI Preparation System
# Main application with Discord bot integration

import discord
from discord.ext import commands
import openai
import json
import random
import sqlite3
from datetime import datetime, timedelta
import asyncio
import os
from typing import List, Dict, Optional
import requests
from dataclasses import dataclass, asdict
import pickle

# Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DATABASE_PATH = 'neet_prep.db'

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

@dataclass
class Question:
    id: str
    subject: str
    topic: str
    question_text: str
    options: List[str]
    correct_answer: int
    explanation: str
    year: int
    difficulty: str
    is_pyq: bool = True

@dataclass
class UserProgress:
    user_id: str
    subject_progress: Dict[str, float]
    total_questions_attempted: int
    correct_answers: int
    last_study_date: str
    weak_topics: List[str]
    strong_topics: List[str]

class NEETDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Questions table
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
        
        # User progress table
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
        
        # User responses table
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
        
        conn.commit()
        conn.close()
        
        # Load initial PYQ data if database is empty
        self.load_initial_data()
    
    def load_initial_data(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM questions")
        count = cursor.fetchone()[0]
        conn.close()
        
        if count == 0:
            self.insert_sample_pyqs()
    
    def insert_sample_pyqs(self):
        """Insert sample PYQ data"""
        sample_questions = [
            Question(
                id="NEET2023_PHY_001",
                subject="Physics",
                topic="Mechanics",
                question_text="A body of mass 2 kg is moving with velocity 10 m/s. What is its kinetic energy?",
                options=["50 J", "100 J", "200 J", "400 J"],
                correct_answer=1,
                explanation="KE = (1/2)mv² = (1/2)(2)(10)² = 100 J",
                year=2023,
                difficulty="Easy",
                is_pyq=True
            ),
            Question(
                id="NEET2022_CHEM_001",
                subject="Chemistry",
                topic="Organic Chemistry",
                question_text="Which of the following is an example of nucleophilic substitution reaction?",
                options=["CH₃Cl + OH⁻ → CH₃OH + Cl⁻", "C₂H₄ + H₂ → C₂H₆", "CH₄ + Cl₂ → CH₃Cl + HCl", "C₂H₄ + HBr → C₂H₅Br"],
                correct_answer=0,
                explanation="Nucleophilic substitution involves nucleophile attacking electrophilic carbon",
                year=2022,
                difficulty="Medium",
                is_pyq=True
            ),
            Question(
                id="NEET2023_BIO_001",
                subject="Biology",
                topic="Cell Biology",
                question_text="Which organelle is known as the powerhouse of the cell?",
                options=["Nucleus", "Mitochondria", "Ribosome", "Endoplasmic Reticulum"],
                correct_answer=1,
                explanation="Mitochondria produces ATP through cellular respiration",
                year=2023,
                difficulty="Easy",
                is_pyq=True
            )
        ]
        
        for question in sample_questions:
            self.add_question(question)
    
    def add_question(self, question: Question):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO questions 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            question.id, question.subject, question.topic, question.question_text,
            json.dumps(question.options), question.correct_answer, question.explanation,
            question.year, question.difficulty, question.is_pyq
        ))
        conn.commit()
        conn.close()
    
    def get_questions_by_subject(self, subject: str) -> List[Question]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM questions WHERE subject = ?", (subject,))
        rows = cursor.fetchall()
        conn.close()
        
        questions = []
        for row in rows:
            questions.append(Question(
                id=row[0], subject=row[1], topic=row[2], question_text=row[3],
                options=json.loads(row[4]), correct_answer=row[5], explanation=row[6],
                year=row[7], difficulty=row[8], is_pyq=bool(row[9])
            ))
        return questions
    
    def get_random_question(self, subject: str = None) -> Optional[Question]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if subject:
            cursor.execute("SELECT * FROM questions WHERE subject = ? ORDER BY RANDOM() LIMIT 1", (subject,))
        else:
            cursor.execute("SELECT * FROM questions ORDER BY RANDOM() LIMIT 1")
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Question(
                id=row[0], subject=row[1], topic=row[2], question_text=row[3],
                options=json.loads(row[4]), correct_answer=row[5], explanation=row[6],
                year=row[7], difficulty=row[8], is_pyq=bool(row[9])
            )
        return None
    
    def update_user_progress(self, user_id: str, question_id: str, selected_answer: int, is_correct: bool):
        # Record user response
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO user_responses (user_id, question_id, selected_answer, is_correct, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, question_id, selected_answer, is_correct, datetime.now().isoformat()))
        
        # Update user progress
        cursor.execute("SELECT * FROM user_progress WHERE user_id = ?", (user_id,))
        progress_row = cursor.fetchone()
        
        if progress_row:
            subject_progress = json.loads(progress_row[1])
            total_attempted = progress_row[2] + 1
            correct_answers = progress_row[3] + (1 if is_correct else 0)
            weak_topics = json.loads(progress_row[5])
            strong_topics = json.loads(progress_row[6])
        else:
            subject_progress = {"Physics": 0, "Chemistry": 0, "Biology": 0}
            total_attempted = 1
            correct_answers = 1 if is_correct else 0
            weak_topics = []
            strong_topics = []
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_progress 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, json.dumps(subject_progress), total_attempted, correct_answers,
            datetime.now().isoformat(), json.dumps(weak_topics), json.dumps(strong_topics)
        ))
        
        conn.commit()
        conn.close()

class AIQuestionGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        openai.api_key = api_key
    
    def generate_question(self, subject: str, topic: str, difficulty: str = "Medium") -> Optional[Question]:
        """Generate AI question in PYQ style"""
        try:
            prompt = f"""
            Generate a NEET {subject} question on {topic} with {difficulty} difficulty level.
            
            Format the response as JSON with these fields:
            - question_text: The main question
            - options: Array of 4 options (A, B, C, D)
            - correct_answer: Index of correct answer (0-3)
            - explanation: Brief explanation of the answer
            
            Make it similar to actual NEET previous year questions in style and difficulty.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            question_data = json.loads(content)
            
            question = Question(
                id=f"AI_{subject.upper()}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                subject=subject,
                topic=topic,
                question_text=question_data['question_text'],
                options=question_data['options'],
                correct_answer=question_data['correct_answer'],
                explanation=question_data['explanation'],
                year=datetime.now().year,
                difficulty=difficulty,
                is_pyq=False
            )
            
            return question
            
        except Exception as e:
            print(f"Error generating AI question: {e}")
            return None

class NEETSyllabusTracker:
    def __init__(self):
        self.syllabus = self.load_neet_syllabus()
    
    def load_neet_syllabus(self) -> Dict:
        return {
            "Physics": {
                "Class 11": [
                    "Physical World and Measurement",
                    "Kinematics",
                    "Laws of Motion",
                    "Work, Energy and Power",
                    "Motion of System of Particles and Rigid Body",
                    "Gravitation",
                    "Properties of Bulk Matter",
                    "Thermodynamics",
                    "Behaviour of Perfect Gas and Kinetic Theory",
                    "Oscillations and Waves"
                ],
                "Class 12": [
                    "Electrostatics",
                    "Current Electricity",
                    "Magnetic Effects of Current and Magnetism",
                    "Electromagnetic Induction and Alternating Currents",
                    "Electromagnetic Waves",
                    "Optics",
                    "Dual Nature of Matter and Radiation",
                    "Atoms and Nuclei",
                    "Electronic Devices"
                ]
            },
            "Chemistry": {
                "Class 11": [
                    "Some Basic Concepts of Chemistry",
                    "Structure of Atom",
                    "Classification of Elements and Periodicity",
                    "Chemical Bonding and Molecular Structure",
                    "States of Matter",
                    "Thermodynamics",
                    "Equilibrium",
                    "Redox Reactions",
                    "Hydrogen",
                    "s-Block Elements",
                    "Some p-Block Elements",
                    "Organic Chemistry - Basic Principles",
                    "Hydrocarbons",
                    "Environmental Chemistry"
                ],
                "Class 12": [
                    "Solid State",
                    "Solutions",
                    "Electrochemistry",
                    "Chemical Kinetics",
                    "Surface Chemistry",
                    "General Principles of Metallurgy",
                    "p-Block Elements",
                    "d and f Block Elements",
                    "Coordination Compounds",
                    "Haloalkanes and Haloarenes",
                    "Alcohols, Phenols and Ethers",
                    "Aldehydes, Ketones and Carboxylic Acids",
                    "Organic Compounds containing Nitrogen",
                    "Biomolecules",
                    "Polymers",
                    "Chemistry in Everyday Life"
                ]
            },
            "Biology": {
                "Class 11": [
                    "Diversity in Living World",
                    "Structural Organisation in Animals and Plants",
                    "Cell Structure and Function",
                    "Plant Physiology",
                    "Human Physiology"
                ],
                "Class 12": [
                    "Reproduction",
                    "Genetics and Evolution",
                    "Biology and Human Welfare",
                    "Biotechnology and Its Applications",
                    "Ecology and Environment"
                ]
            }
        }
    
    def get_syllabus(self, subject: str = None) -> Dict:
        if subject:
            return self.syllabus.get(subject, {})
        return self.syllabus
    
    def get_topics_by_subject(self, subject: str) -> List[str]:
        subject_syllabus = self.syllabus.get(subject, {})
        topics = []
        for class_topics in subject_syllabus.values():
            topics.extend(class_topics)
        return topics

# Discord Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize components
db = NEETDatabase(DATABASE_PATH)
ai_generator = AIQuestionGenerator(OPENAI_API_KEY) if OPENAI_API_KEY else None
syllabus_tracker = NEETSyllabusTracker()

# Global variables for quiz sessions
active_quizzes = {}

@bot.event
async def on_ready():
    print(f'{bot.user} has landed on Discord!')
    print(f'Bot is ready to help with NEET preparation!')

@bot.command(name='start')
async def start_command(ctx):
    """Start message for the bot"""
    embed = discord.Embed(
        title="🎓 NEET AI Preparation System",
        description="Your AI-powered companion for NEET preparation!",
        color=0x00ff00
    )
    embed.add_field(
        name="📚 Available Commands:",
        value="""
        `!quiz [subject]` - Start a practice quiz
        `!pyq [subject]` - Get previous year questions
        `!syllabus [subject]` - View syllabus
        `!progress` - Check your progress
        `!generate [subject] [topic]` - Generate AI questions
        `!help` - Show all commands
        """,
        inline=False
    )
    embed.add_field(
        name="📖 Subjects:",
        value="Physics, Chemistry, Biology",
        inline=True
    )
    await ctx.send(embed=embed)

@bot.command(name='quiz')
async def quiz_command(ctx, subject: str = None):
    """Start a quiz session"""
    if subject and subject.title() not in ["Physics", "Chemistry", "Biology"]:
        await ctx.send("❌ Please specify a valid subject: Physics, Chemistry, or Biology")
        return
    
    question = db.get_random_question(subject.title() if subject else None)
    if not question:
        await ctx.send("❌ No questions available for this subject!")
        return
    
    # Store active quiz
    active_quizzes[ctx.author.id] = question
    
    embed = discord.Embed(
        title=f"📝 {question.subject} Quiz",
        description=f"**Topic:** {question.topic}",
        color=0x3498db
    )
    embed.add_field(name="Question:", value=question.question_text, inline=False)
    
    options_text = ""
    for i, option in enumerate(question.options):
        options_text += f"**{chr(65+i)}.** {option}\n"
    
    embed.add_field(name="Options:", value=options_text, inline=False)
    embed.add_field(name="Instructions:", value="React with 🇦, 🇧, 🇨, or 🇩 to answer!", inline=False)
    
    if question.is_pyq:
        embed.set_footer(text=f"PYQ {question.year} | Difficulty: {question.difficulty}")
    else:
        embed.set_footer(text=f"AI Generated | Difficulty: {question.difficulty}")
    
    message = await ctx.send(embed=embed)
    
    # Add reaction options
    reactions = ['🇦', '🇧', '🇨', '🇩']
    for reaction in reactions:
        await message.add_reaction(reaction)

@bot.event
async def on_reaction_add(reaction, user):
    """Handle quiz answers"""
    if user.bot:
        return
    
    if user.id not in active_quizzes:
        return
    
    if str(reaction.emoji) not in ['🇦', '🇧', '🇨', '🇩']:
        return
    
    question = active_quizzes[user.id]
    selected_answer = ['🇦', '🇧', '🇨', '🇩'].index(str(reaction.emoji))
    is_correct = selected_answer == question.correct_answer
    
    # Update user progress
    db.update_user_progress(str(user.id), question.id, selected_answer, is_correct)
    
    # Send result
    embed = discord.Embed(
        title="📊 Quiz Result",
        color=0x00ff00 if is_correct else 0xff0000
    )
    
    if is_correct:
        embed.add_field(name="✅ Correct!", value="Well done!", inline=False)
    else:
        embed.add_field(
            name="❌ Incorrect!",
            value=f"The correct answer was: **{question.options[question.correct_answer]}**",
            inline=False
        )
    
    embed.add_field(name="Explanation:", value=question.explanation, inline=False)
    
    channel = reaction.message.channel
    await channel.send(embed=embed)
    
    # Remove from active quizzes
    del active_quizzes[user.id]

@bot.command(name='syllabus')
async def syllabus_command(ctx, subject: str = None):
    """Show NEET syllabus"""
    if subject and subject.title() not in ["Physics", "Chemistry", "Biology"]:
        await ctx.send("❌ Please specify a valid subject: Physics, Chemistry, or Biology")
        return
    
    if subject:
        syllabus_data = syllabus_tracker.get_syllabus(subject.title())
        embed = discord.Embed(
            title=f"📚 NEET {subject.title()} Syllabus",
            color=0x9b59b6
        )
        
        for class_name, topics in syllabus_data.items():
            topics_text = "\n".join([f"• {topic}" for topic in topics])
            embed.add_field(name=f"{class_name}:", value=topics_text, inline=False)
    else:
        embed = discord.Embed(
            title="📚 NEET Complete Syllabus",
            description="Use `!syllabus [subject]` for detailed view",
            color=0x9b59b6
        )
        
        for subject in ["Physics", "Chemistry", "Biology"]:
            topic_count = len(syllabus_tracker.get_topics_by_subject(subject))
            embed.add_field(
                name=f"{subject}:",
                value=f"{topic_count} topics",
                inline=True
            )
    
    await ctx.send(embed=embed)

@bot.command(name='generate')
async def generate_command(ctx, subject: str = None, *, topic: str = None):
    """Generate AI questions"""
    if not ai_generator:
        await ctx.send("❌ AI question generation not available. Please set OPENAI_API_KEY.")
        return
    
    if not subject or subject.title() not in ["Physics", "Chemistry", "Biology"]:
        await ctx.send("❌ Please specify a valid subject: Physics, Chemistry, or Biology")
        return
    
    if not topic:
        topics = syllabus_tracker.get_topics_by_subject(subject.title())
        topic = random.choice(topics)
    
    await ctx.send("🤖 Generating AI question... Please wait!")
    
    question = ai_generator.generate_question(subject.title(), topic)
    if question:
        # Add to database
        db.add_question(question)
        
        # Start quiz with generated question
        active_quizzes[ctx.author.id] = question
        
        embed = discord.Embed(
            title=f"🤖 AI Generated {question.subject} Question",
            description=f"**Topic:** {question.topic}",
            color=0xe74c3c
        )
        embed.add_field(name="Question:", value=question.question_text, inline=False)
        
        options_text = ""
        for i, option in enumerate(question.options):
            options_text += f"**{chr(65+i)}.** {option}\n"
        
        embed.add_field(name="Options:", value=options_text, inline=False)
        embed.add_field(name="Instructions:", value="React with 🇦, 🇧, 🇨, or 🇩 to answer!", inline=False)
        embed.set_footer(text=f"AI Generated | Difficulty: {question.difficulty}")
        
        message = await ctx.send(embed=embed)
        
        # Add reaction options
        reactions = ['🇦', '🇧', '🇨', '🇩']
        for reaction in reactions:
            await message.add_reaction(reaction)
    else:
        await ctx.send("❌ Failed to generate question. Please try again!")

@bot.command(name='progress')
async def progress_command(ctx):
    """Show user progress"""
    # This would typically fetch from database
    embed = discord.Embed(
        title="📈 Your NEET Progress",
        color=0xf39c12
    )
    embed.add_field(name="Total Questions Attempted:", value="0", inline=True)
    embed.add_field(name="Accuracy:", value="0%", inline=True)
    embed.add_field(name="Study Streak:", value="0 days", inline=True)
    embed.add_field(
        name="Subject Progress:",
        value="Physics: 0%\nChemistry: 0%\nBiology: 0%",
        inline=False
    )
    await ctx.send(embed=embed)

# Console Application
class NEETConsoleApp:
    def __init__(self):
        self.db = NEETDatabase(DATABASE_PATH)
        self.ai_generator = AIQuestionGenerator(OPENAI_API_KEY) if OPENAI_API_KEY else None
        self.syllabus_tracker = NEETSyllabusTracker()
    
    def run(self):
        print("🎓 NEET AI Preparation System")
        print("=" * 40)
        
        while True:
            print("\n📚 Main Menu:")
            print("1. Practice Quiz")
            print("2. View Syllabus")
            print("3. Generate AI Questions")
            print("4. View Progress")
            print("5. Add Custom Question")
            print("6. Exit")
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == '1':
                self.practice_quiz()
            elif choice == '2':
                self.view_syllabus()
            elif choice == '3':
                self.generate_ai_questions()
            elif choice == '4':
                self.view_progress()
            elif choice == '5':
                self.add_custom_question()
            elif choice == '6':
                print("👋 Good luck with your NEET preparation!")
                break
            else:
                print("❌ Invalid choice! Please try again.")
    
    def practice_quiz(self):
        print("\n📝 Practice Quiz")
        print("1. Physics")
        print("2. Chemistry") 
        print("3. Biology")
        print("4. Mixed (All subjects)")
        
        subject_choice = input("Choose subject (1-4): ").strip()
        subject_map = {'1': 'Physics', '2': 'Chemistry', '3': 'Biology', '4': None}
        subject = subject_map.get(subject_choice)
        
        question = self.db.get_random_question(subject)
        if not question:
            print("❌ No questions available!")
            return
        
        print(f"\n📚 Subject: {question.subject}")
        print(f"📖 Topic: {question.topic}")
        print(f"📅 Year: {question.year} ({'PYQ' if question.is_pyq else 'AI Generated'})")
        print(f"\n❓ {question.question_text}")
        
        for i, option in enumerate(question.options):
            print(f"{chr(65+i)}. {option}")
        
        while True:
            answer = input("\nYour answer (A/B/C/D): ").upper().strip()
            if answer in ['A', 'B', 'C', 'D']:
                selected_answer = ord(answer) - ord('A')
                break
            print("❌ Please enter A, B, C, or D")
        
        is_correct = selected_answer == question.correct_answer
        
        if is_correct:
            print("✅ Correct! Well done!")
        else:
            print(f"❌ Incorrect! The correct answer was: {question.options[question.correct_answer]}")
        
        print(f"\n💡 Explanation: {question.explanation}")
        
        # Update progress (simplified for console)
        self.db.update_user_progress("console_user", question.id, selected_answer, is_correct)
    
    def view_syllabus(self):
        print("\n📚 NEET Syllabus")
        print("1. Physics")
        print("2. Chemistry")
        print("3. Biology")
        print("4. All subjects")
        
        choice = input("Choose option (1-4): ").strip()
        
        if choice in ['1', '2', '3']:
            subject = ['Physics', 'Chemistry', 'Biology'][int(choice)-1]
            syllabus_data = self.syllabus_tracker.get_syllabus(subject)
            print(f"\n📖 {subject} Syllabus:")
            for class_name, topics in syllabus_data.items():
                print(f"\n{class_name}:")
                for topic in topics:
                    print(f"  • {topic}")
        elif choice == '4':
            for subject in ['Physics', 'Chemistry', 'Biology']:
                print(f"\n📖 {subject}:")
                topics = self.syllabus_tracker.get_topics_by_subject(subject)
                print(f"  Total topics: {len(topics)}")
    
    def generate_ai_questions(self):
        if not self.ai_generator:
            print("❌ AI question generation not available. Please set OPENAI_API_KEY.")
            return
        
        print("\n🤖 AI Question Generator")
        subject = input("Enter subject (Physics/Chemistry/Biology): ").strip().title()
        if subject not in ['Physics', 'Chemistry', 'Biology']:
            print("❌ Invalid subject!")
            return
        
        topic = input(f"Enter topic for {subject}: ").strip()
        if not topic:
            topics = self.syllabus_tracker.get_topics_by_subject(subject)
            topic = random.choice(topics)
            print(f"🎲 Random topic selected: {topic}")
        
        print("🤖 Generating question... Please wait!")
        question = self.ai_generator.generate_question(subject, topic)
        
        if question:
            self.db.add_question(question)
            print("✅ Question generated and added to database!")
            
            # Show the generated question
            print(f"\n📚 Generated Question:")
            print(f"Subject: {question.subject}")
            print(f"Topic: {question.topic}")
            print(f"\n❓ {question.question_text}")
            
            for i, option in enumerate(question.options):
                print(f"{chr(65+i)}. {option}")
            
            print(f"\n✅ Correct Answer: {chr(65+question.correct_answer)}")
            print(f"💡 Explanation: {question.explanation}")
        else:
            print("❌ Failed to generate question!")
    
    def view_progress(self):
        print("\n📈 Progress Summary")
        print("This feature would show detailed progress from database")
        print("For now, showing placeholder data:")
        print("Total Questions: 0")
        print("Accuracy: 0%")
        print("Weak Areas: To be determined")
    
    def add_custom_question(self):
        print("\n➕ Add Custom Question")
        
        subject = input("Subject (Physics/Chemistry/Biology): ").strip().title()
        if subject not in ['Physics', 'Chemistry', 'Biology']:
            print("❌ Invalid subject!")
            return
        
        topic = input("Topic: ").strip()
        question_text = input("Question: ").strip()
        
        options = []
        for i in range(4):
            option = input(f"Option {chr(65+i)}: ").strip()
            options.append(option)
        
        while True:
            correct = input("Correct answer (A/B/C/D): ").upper().strip()
            if correct in ['A', 'B', 'C', 'D']:
                correct_answer = ord(correct) - ord('A')
                break
            print("❌ Please enter A, B, C, or D")
        
        explanation = input("Explanation: ").strip()
        
        question = Question(
            id=f"CUSTOM_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            subject=subject,
            topic=topic,
            question_text=question_text,
            options=options,
            correct_answer=correct_answer,
            explanation=explanation,
            year=datetime.now().year,
            difficulty="Custom",
            is_pyq=False
        )
        
        self.db.add_question(question)
        print("✅ Custom question added successfully!")

# Main execution
def main():
    print("🎓 NEET AI Preparation System")
    print("Choose mode:")
    print("1. Console Application")
    print("2. Discord Bot")
    
    choice = input("Enter choice (1-2): ").strip()
    
    if choice == '1':
        app = NEETConsoleApp()
        app.run()
    elif choice == '2':
        if not DISCORD_TOKEN:
            print("❌ Discord token not found! Please set DISCORD_TOKEN environment variable.")
            return
        print("🤖 Starting Discord bot...")
        print("Available commands: !start, !quiz, !syllabus, !generate, !progress")
        bot.run(DISCORD_TOKEN)
    else:
        print("❌ Invalid choice!")

if __name__ == "__main__":
    # Check environment variables
    if not OPENAI_API_KEY:
        print("⚠️  Warning: OPENAI_API_KEY not set. AI question generation will be disabled.")
    
    if not DISCORD_TOKEN:
        print("⚠️  Warning: DISCORD_TOKEN not set. Discord bot mode will not work.")
    
    main()