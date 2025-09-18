# PYQ Scraper - Collects NEET Previous Year Questions
import requests
from bs4 import BeautifulSoup
import json
import sqlite3
from datetime import datetime
import PyPDF2
import pdfplumber
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
import os

@dataclass
class ScrapedQuestion:
    question_text: str
    options: List[str]
    correct_answer: int
    subject: str
    topic: str
    year: int
    source_url: str
    explanation: str = ""

class NEETPYQScraper:
    def __init__(self, db_path: str = "neet_prep.db"):
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def scrape_neet_questions_from_urls(self, urls: List[str]) -> List[ScrapedQuestion]:
        """Scrape questions from various NEET preparation websites"""
        all_questions = []
        
        for url in urls:
            try:
                print(f"Scraping from: {url}")
                questions = self.scrape_single_url(url)
                all_questions.extend(questions)
                print(f"Found {len(questions)} questions from {url}")
            except Exception as e:
                print(f"Error scraping {url}: {e}")
                
        return all_questions
    
    def scrape_single_url(self, url: str) -> List[ScrapedQuestion]:
        """Scrape questions from a single URL"""
        response = self.session.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        questions = []
        
        # Generic question extraction patterns
        # This would need to be customized for each website
        question_blocks = soup.find_all(['div', 'section'], class_=re.compile(r'question|quiz|mcq'))
        
        for block in question_blocks:
            try:
                question = self.extract_question_from_block(block, url)
                if question:
                    questions.append(question)
            except Exception as e:
                print(f"Error extracting question: {e}")
                
        return questions
    
    def extract_question_from_block(self, block, source_url: str) -> Optional[ScrapedQuestion]:
        """Extract question data from HTML block"""
        # This is a generic implementation - would need customization for specific sites
        
        question_text = ""
        options = []
        correct_answer = -1
        subject = "Unknown"
        topic = "General"
        year = 2023  # Default
        
        # Find question text
        question_elem = block.find(['p', 'h3', 'h4', 'div'], text=re.compile(r'\?'))
        if question_elem:
            question_text = question_elem.get_text().strip()
        
        # Find options (A, B, C, D)
        option_elems = block.find_all(['li', 'div', 'p'], text=re.compile(r'^[A-D][\.\)]'))
        for elem in option_elems[:4]:  # Limit to 4 options
            option_text = elem.get_text().strip()
            # Remove A. B. C. D. prefixes
            clean_option = re.sub(r'^[A-D][\.\)]\s*', '', option_text)
            options.append(clean_option)
        
        # Try to find correct answer indicator
        correct_elem = block.find(['span', 'div'], class_=re.compile(r'correct|answer'))
        if correct_elem:
            correct_text = correct_elem.get_text()
            if 'A' in correct_text: correct_answer = 0
            elif 'B' in correct_text: correct_answer = 1
            elif 'C' in correct_text: correct_answer = 2
            elif 'D' in correct_text: correct_answer = 3
        
        # Extract subject if available
        subject_elem = block.find(['span', 'div'], class_=re.compile(r'subject|category'))
        if subject_elem:
            subject = subject_elem.get_text().strip()
        
        if question_text and len(options) == 4 and correct_answer >= 0:
            return ScrapedQuestion(
                question_text=question_text,
                options=options,
                correct_answer=correct_answer,
                subject=subject,
                topic=topic,
                year=year,
                source_url=source_url
            )
        
        return None
    
    def scrape_pdf_questions(self, pdf_path: str) -> List[ScrapedQuestion]:
        """Extract questions from NEET PYQ PDF files"""
        questions = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        page_questions = self.parse_pdf_text_for_questions(text, pdf_path)
                        questions.extend(page_questions)
                        
        except Exception as e:
            print(f"Error processing PDF {pdf_path}: {e}")
            
        return questions
    
    def parse_pdf_text_for_questions(self, text: str, source: str) -> List[ScrapedQuestion]:
        """Parse extracted PDF text to find questions"""
        questions = []
        
        # Pattern to match question numbers (1., 2., etc.)
        question_pattern = r'(\d+\.)\s*(.*?)(?=\d+\.|$)'
        matches = re.findall(question_pattern, text, re.DOTALL)
        
        for match in matches:
            question_num, question_content = match
            
            # Extract question text and options
            lines = question_content.strip().split('\n')
            question_text = ""
            options = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Check if this line is an option (A), (B), etc.
                if re.match(r'^\([A-D]\)', line):
                    option_text = re.sub(r'^\([A-D]\)\s*', '', line)
                    options.append(option_text)
                elif not options:  # Still building question text
                    question_text += " " + line
            
            # Try to determine subject from context or filename
            subject = self.determine_subject_from_context(question_text, source)
            
            if question_text and len(options) == 4:
                # For PDFs, correct answer would need to be provided separately
                # or extracted from answer key
                questions.append(ScrapedQuestion(
                    question_text=question_text.strip(),
                    options=options,
                    correct_answer=0,  # Placeholder - needs answer key
                    subject=subject,
                    topic="General",
                    year=self.extract_year_from_filename(source),
                    source_url=source
                ))
                
        return questions
    
    def determine_subject_from_context(self, question_text: str, source: str) -> str:
        """Determine subject based on question content and source"""
        question_lower = question_text.lower()
        source_lower = source.lower()
        
        # Physics keywords
        physics_keywords = ['force', 'velocity', 'acceleration', 'energy', 'momentum', 
                          'electric', 'magnetic', 'wave', 'frequency', 'mass', 'newton']
        
        # Chemistry keywords  
        chemistry_keywords = ['molecule', 'atom', 'bond', 'reaction', 'element', 
                            'compound', 'acid', 'base', 'oxidation', 'reduction']
        
        # Biology keywords
        biology_keywords = ['cell', 'organism', 'gene', 'protein', 'enzyme', 'tissue',
                          'organ', 'species', 'evolution', 'dna', 'rna']
        
        # Check source filename first
        if 'physics' in source_lower:
            return 'Physics'
        elif 'chemistry' in source_lower or 'chem' in source_lower:
            return 'Chemistry'  
        elif 'biology' in source_lower or 'bio' in source_lower:
            return 'Biology'
        
        # Check question content
        physics_count = sum(1 for keyword in physics_keywords if keyword in question_lower)
        chemistry_count = sum(1 for keyword in chemistry_keywords if keyword in question_lower)
        biology_count = sum(1 for keyword in biology_keywords if keyword in question_lower)
        
        if physics_count > chemistry_count and physics_count > biology_count:
            return 'Physics'
        elif chemistry_count > biology_count:
            return 'Chemistry'
        elif biology_count > 0:
            return 'Biology'
        
        return 'Unknown'
    
    def extract_year_from_filename(self, filename: str) -> int:
        """Extract year from filename"""
        year_match = re.search(r'20\d{2}', filename)
        if year_match:
            return int(year_match.group())
        return 2023  # Default
    
    def save_questions_to_db(self, questions: List[ScrapedQuestion]):
        """Save scraped questions to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for question in questions:
            question_id = f"SCRAPED_{question.subject.upper()}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            cursor.execute('''
                INSERT OR IGNORE INTO questions 
                (id, subject, topic, question_text, options, correct_answer, 
                 explanation, year, difficulty, is_pyq)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                question_id, question.subject, question.topic, question.question_text,
                json.dumps(question.options), question.correct_answer,
                question.explanation, question.year, "Medium", True
            ))
        
        conn.commit()
        conn.close()
        print(f"Saved {len(questions)} questions to database")

# Sample scraping targets (educational websites with NEET questions)
SAMPLE_URLS = [
    # Add legitimate educational websites here
    "https://www.embibe.com/exams/neet/",
    "https://www.aakash.ac.in/neet-exam/previous-year-question-papers",
    # Note: Always respect robots.txt and terms of service
]

def main():
    scraper = NEETPYQScraper()
    
    print("NEET PYQ Scraper")
    print("1. Scrape from URLs")
    print("2. Process PDF files")
    print("3. Both")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice in ['1', '3']:
        print(f"Scraping from {len(SAMPLE_URLS)} URLs...")
        questions = scraper.scrape_neet_questions_from_urls(SAMPLE_URLS)
        if questions:
            scraper.save_questions_to_db(questions)
        else:
            print("No questions found from URLs")
    
    if choice in ['2', '3']:
        pdf_dir = input("Enter PDF directory path (or press Enter for current directory): ").strip()
        if not pdf_dir:
            pdf_dir = "."
            
        pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
        
        if pdf_files:
            print(f"Processing {len(pdf_files)} PDF files...")
            all_pdf_questions = []
            
            for pdf_file in pdf_files:
                pdf_path = os.path.join(pdf_dir, pdf_file)
                questions = scraper.scrape_pdf_questions(pdf_path)
                all_pdf_questions.extend(questions)
                print(f"Extracted {len(questions)} questions from {pdf_file}")
            
            if all_pdf_questions:
                scraper.save_questions_to_db(all_pdf_questions)
        else:
            print("No PDF files found in directory")

if __name__ == "__main__":
    main()