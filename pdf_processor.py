import os
import re
import json
import csv
from datetime import datetime
import fitz  # PyMuPDF
import tiktoken
import shutil
from IPython.display import display, HTML

# Constants
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def color_print(text, color="", font_size="14", debug=False):
    if debug:
        color_str = f"<pre style='color: {color}; font-size: {font_size}px;white-space: pre-line;white-space: pre-wrap;word-wrap: break-word;'>{text}</pre>"
        display(HTML(color_str))

def read_config():
    config_path = os.path.join(ROOT_DIR, "test_configuration.json")
    with open(config_path, "r") as f:
        return json.load(f)

def delete_output_folder(config):
    if config.get('reset_output', False):
        output_folder = os.path.join(ROOT_DIR, config['output_folder'])
        if os.path.exists(output_folder) and os.path.isdir(output_folder):
            shutil.rmtree(output_folder)
            print(f"Folder {output_folder} has been deleted!")
        else:
            print(f"Folder {output_folder} does not exist!")
    else:
        print("Reset output is not set to True. No action performed.")

def initialize_output_folder(config, folder_name):
    path = os.path.join(ROOT_DIR, config[folder_name])
    if not os.path.exists(path):
        os.mkdir(path)
    return path

def initialize_csv_log(output_folder, config):
    path = f"{output_folder}/log.csv"
    if not os.path.exists(path):
        with open(path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['original_input_file', 'output_file', 'paragraph_name', 'chunk_number', 'start_date_time', 'stop_date_time', 'status', 'errors'])
    return path

def extract_table_of_contents(pdf_path, toc_pages):
    pdf_document = fitz.open(pdf_path)
    toc_text = ""
    for page_number in toc_pages:
        if 0 <= page_number < len(pdf_document):
            page = pdf_document.load_page(page_number)
            toc_text += page.get_text("text")
        else:
            print(f"Page number {page_number} is out of range.")
    print("TOC Text Extracted:")  # Debug statement
    print(toc_text)  # Debug statement
    return parse_toc(toc_text)

def parse_toc(toc_text):
    toc_dict = {}
    for line in toc_text.splitlines():
        match = re.match(r'(.*?)\s*\.+\s*(\d+)', line)
        if match:
            chapter_title, page_number = match.groups()
            toc_dict[chapter_title.strip()] = int(page_number) - 1  # Adjust for zero-based index
    print("Parsed TOC:")  # Debug statement
    print(toc_dict)  # Debug statement
    return toc_dict

def extract_chapter_content(pdf_path, toc_dict):
    pdf_document = fitz.open(pdf_path)
    chapter_content = {}
    chapters = list(toc_dict.keys())
    for i, chapter in enumerate(chapters):
        start_page = toc_dict[chapter]
        end_page = toc_dict[chapters[i + 1]] if i + 1 < len(chapters) else len(pdf_document)
        content = ""
        for page_number in range(start_page, end_page):
            if 0 <= page_number < len(pdf_document):
                page = pdf_document.load_page(page_number)
                content += page.get_text("text")
        chapter_content[chapter] = content
    print("Extracted Chapter Content:")  # Debug statement
    for chapter, content in chapter_content.items():
        print(f"Chapter: {chapter}, Content: {content[:500]}...")  # Print first 500 chars for debugging
    return chapter_content

import re

import re

def split_text(text, max_length):
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        if current_length + len(word) + (1 if current_chunk else 0) > max_length:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_length = 0

        current_chunk.append(word)
        current_length += len(word) + (1 if current_chunk else 0)

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    # print("Chunks :", chunks) # Debug print to see the chunks formed
    return chunks

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.encoding_for_model(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '', filename).replace(' ', '_')

def process_chapter_content(config, csv_log_path):
    pdf_path = os.path.join(ROOT_DIR, config['pdf_path'])
    toc_pages = config['toc_pages']
    toc_dict = extract_table_of_contents(pdf_path, toc_pages)
    chapter_content = extract_chapter_content(pdf_path, toc_dict)

    chapter_output_folder = initialize_output_folder(config, 'output_chapters')

    for chapter, content in chapter_content.items():
        chunks = split_text(content, config['token_size_input'])
        for j, chunk in enumerate(chunks):
            start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            safe_filename = sanitize_filename(chapter)
            base_name = safe_filename
            output_filename = f"{base_name}-{j+1}.txt"

            try:
                with open(os.path.join(chapter_output_folder, output_filename), 'w', encoding='utf-8') as f:
                    f.write(chunk)
                status = "COMPLETED"
                errors = "None"
            except Exception as e:
                status = "ERROR"
                errors = f"Error: {e}"

            stop_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            with open(csv_log_path, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    chapter, output_filename, chapter, j+1,
                    start_time, stop_time, status, errors
                ])
            print(f"Processed {output_filename}: {status} - {errors}")  # Debug statement