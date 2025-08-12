import os
import re
import json
import glob
from typing import List, Dict, Optional

def get_subject_from_filename(filename: str) -> Optional[str]:
    """Extracts the subject from the filename."""
    if "varc" in filename or "verbal-ability" in filename:
        return "varc"
    elif "quant" in filename:
        return "quant"
    elif "dilr" in filename or "lrdi" in filename:
        return "dilr"
    return None

def parse_markdown_file(file_path: str) -> List[Dict]:
    """Parses a single markdown file and extracts questions."""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    subject = get_subject_from_filename(os.path.basename(file_path))
    questions = []
    
    # Use a regex that captures the question number and the content following it.
    # The lookahead ensures we capture content up to the next question or end of file.
    question_blocks = re.split(r'## (Question \d+)', content)
    
    instructions_content = question_blocks[0].strip()
    
    # We get pairs of (question_header, question_content)
    for i in range(1, len(question_blocks), 2):
        header = question_blocks[i]
        block = question_blocks[i+1]
        
        question_data = {}
        
        question_number = int(re.search(r'\d+', header).group())
        question_data['question_number'] = question_number

        # Extract question text, options, and solution
        parts = re.split(r'Solution', block)
        question_part = parts[0]
        solution_part = parts[1] if len(parts) > 1 else ""

        # Extract the question body
        options_regex = r'\n[A-D]\n'
        options_match = re.search(options_regex, question_part)
        
        if options_match:
            question_data['question_text'] = question_part[:options_match.start()].strip()
            options_text = question_part[options_match.start():].strip()
        else:
            question_data['question_text'] = question_part.strip()
            options_text = ""

        # Extract options
        options = {}
        if options_text:
            # Split by the option letters A, B, C, D
            option_parts = re.split(r'\n([B-D])\n', options_text)
            # The first part starts with A
            current_option = 'A'
            current_text = option_parts[0].replace('A\n', '').strip()
            
            for j in range(1, len(option_parts), 2):
                options[current_option] = current_text
                current_option = option_parts[j]
                current_text = option_parts[j+1].strip()
            options[current_option] = current_text

        question_data['options'] = options

        # Extract solution and correct answer
        solution_text = solution_part.strip()
        question_data['solution'] = solution_text
        
        correct_answer_match = re.search(r'option ([A-D]) is the (?:right|correct) answer', solution_text, re.IGNORECASE)
        if correct_answer_match:
            question_data['correct_answer'] = correct_answer_match.group(1)
        else:
            question_data['correct_answer'] = "See Solution"

        # Extract image URLs
        image_urls = re.findall(r'!.*\[.*?]\]\((.*?)\)', block)
        question_data['image_urls'] = image_urls

        # Add subject and instructions
        question_data['subject'] = subject
        question_data['instructions'] = instructions_content
        
        questions.append(question_data)
        
    return questions

def create_question_banks():
    """Creates separate question banks for each subject from all cleaned markdown files."""
    docs_path = os.path.join(os.path.dirname(__file__), '..', 'chatbot', 'data', 'documents')
    output_path = os.path.join(os.path.dirname(__file__), 'frontend', 'public')
    
    categorized_questions = {
        "varc": [],
        "quant": [],
        "dilr": []
    }
    
    # Use glob to get all file paths and sort them to ensure a consistent processing order
    file_paths = sorted(glob.glob(os.path.join(docs_path, '*_cleaned.md')))

    for file_path in file_paths:
        print(f"Parsing {file_path}...")
        subject = get_subject_from_filename(os.path.basename(file_path))
        if subject:
            parsed_questions = parse_markdown_file(file_path)
            categorized_questions[subject].extend(parsed_questions)

    for subject, questions in categorized_questions.items():
        if questions:
            # No longer sorting by question number to maintain file order
            output_file = os.path.join(output_path, f'{subject}_question_bank.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(questions, f, indent=4)
            
            print(f"\nSuccessfully generated {subject} question bank with {len(questions)} questions.")
            print(f"File saved to: {output_file}")

if __name__ == '__main__':
    create_question_banks()