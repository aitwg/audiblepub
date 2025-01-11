import httpx
import ffmpeg
import json
import logging
import os
import re
import sys
import zipfile

import voicedata

from bs4 import BeautifulSoup
from openai import OpenAI

api_key = 'sk-V2T5h1fG16VcfwLi7b731102100344DdAe4dF2C482A90142TTS'
base_url = 'https://tts.aitwg.com/v1'


client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

_VOICE_INDEX = 0
# list of voices available in Edge TTS.txt
# https://gist.github.com/BettyJJ/17cbaa1de96235a7f5773b8690a20462
def tts_service(text, output_path):
    """
    Generate MP3 audio file from text

    Parameters:
      text(str): text to get audio
      output_path(str): the pathname of audiofile
    """
    data = {
      'model': 'tts-1',
      'input': 'sample',
      'voice': 'en-US-ChristopherNeural',
      'response_format': 'mp3',
      'speed': 1.0,
    }
    # Update the input text
    data['input'] = text
    # Modify the 'voice'
    data['voice'] = voicedata.voices[_VOICE_INDEX]["ShortName"]
    # Adjust the 'speed'
    data['speed'] = 1.0
    try:
        response = client.audio.speech.create(
          **data
        )
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f'MP3 file saved successfully to {output_path}')

    except Exception as e:
        print(f"An error occurred: {e}")


def extract_epub_text(_epub_path):
    """
    Extract texts from epub

    Parameters:
      epub_path(str): the pathname of epub

    Returns:
        the full text of ebook
    """
    with zipfile.ZipFile(_epub_path, 'r') as z:
        file_list = z.namelist()
        text = []

        for file in file_list:
            if file.endswith('.xhtml') or file.endswith('.html'):
                with z.open(file) as f:
                    soup = BeautifulSoup(f, 'html.parser')
                    for paragraph in soup.find_all('p'):
                        text.append(paragraph.get_text())
                        print(text)

    return ' '.join(text)


def split_text_into_chunks(text, max_words=300):
    """
    Splits a long text into a list of smaller texts, each with fewer than max_words.

    Parameters:
        text (str): The input text to be split.
        max_words (int): The maximum number of words per chunk (default is 100).

    Returns:
        list: A list of text chunks, each containing less than max_words.
    """
    words = text.split()  # Split the text into words
    _chunks = []

    for i in range(0, len(words), max_words):
        _chunk = " ".join(words[i:i + max_words])  # Create a chunk of max_words
        _chunks.append(_chunk)

    return _chunks


def extract_base_and_extension(filepath):
    """
    Extracts the base name (excluding numbers) and extension from a full file path.

    Parameters:
        filepath (str): The full file path.

    Returns:
        tuple: A tuple containing the base name (without numbers) and the extension.
    """
    # Extract the file name and extension
    filename, extension = os.path.splitext(os.path.basename(filepath))

    # Remove digits from the file name
    base_name = re.sub(r'\d+', '', filename)

    # Remove the dot from the extension
    extension = extension.lstrip('.')

    return base_name, extension


def get_full_path_from_argv():
    """
    Gets a filename from sys.argv and generates its full path in the current directory
    if the provided filename is a relative path or just a filename.
    If the filename is already a full path, it returns it as-is.

    Returns:
        str: The full path of the file.
    """
    if len(sys.argv) < 2:
        print('Usage: python script.py <filename>')
        sys.exit(1)

    # Get the filename from argv
    filename = sys.argv[1]

    # Check if the provided filename is already a full path
    if os.path.isabs(filename):
        return filename  # If it's a full path, return it directly

    # Get the current directory
    current_dir = os.getcwd()

    # Generate the full path
    full_path = os.path.join(current_dir, filename)

    return full_path

def merge_mp3_files(file_list, output_file):
    """
    Merge list of mp3s file into one file
    Parameters:
      file_list : mp3 file list
      output_file : mp3 output file nam
    """
    input_files = [ffmpeg.input(f) for f in file_list]
    ffmpeg.concat(*input_files, v=0, a=1).output(output_file).run()


if __name__ == "__main__":
    epub_path = get_full_path_from_argv()
    print(f'Start processing file: {epub_path}')

    # epub_path = '/Users/yckm4/Aicode/epubread/killingfloor.epub'

    print(f"Extracting text from {epub_path}...")
    mp3_base, ext = extract_base_and_extension(epub_path)
    book_contents = extract_epub_text(epub_path)
    print(book_contents)

    
    # per test, max 1200 words take about 8 minutes around 3M
    # chunks = split_text_into_chunks(book_contents, max_words=1200)
    _MAX_WORDS_MP3 = 1200
    # _MAX_WORDS_MP3 = 20
    chunks = split_text_into_chunks(book_contents, max_words=_MAX_WORDS_MP3)
    print("Converting text to speech...")
    count = 0
    for index, chunk in enumerate(chunks):
        tts_service(chunk, f"{mp3_base}_{index}.mp3")
        count += 1

    print(f'Audio book saved as {mp3_base}_xxx.mp3, start mergine files....')
    file_list = [f'{mp3_base}_{i}.mp3' for i in range(0, count)]  # Adjust range as needed
    output_file = f'{mp3_base}_all.mp3'
    merge_mp3_files(file_list, output_file)
