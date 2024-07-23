from bs4 import BeautifulSoup
import requests
import os
import time
from urllib.parse import quote
from tqdm import tqdm

# Configuration
LOG_FILE_PATH = 'E:/AI/FoocusAI/Fooocus_win64_2-5-0/Fooocus/outputs/2024-07-23/log.html'
UPLOAD_API_URL = 'https://ai.0u.gay/api/?key={api-key}'
CHECK_FILE_API_URL = 'https://ai.0u.gay/api/check_file.php'  # Endpoint to check file existence

def extract_image_data(log_file_path):
    with open(log_file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
    
    images_data = []
    for container in soup.find_all('div', class_='image-container'):
        img_tag = container.find('img')
        if img_tag:
            image_src = img_tag.get('src', '')
            metadata_rows = container.find_all('tr')
            
            metadata = {}
            for row in metadata_rows:
                label_tag = row.find('td', class_='label')
                value_tag = row.find('td', class_='value')
                if label_tag and value_tag:
                    label = label_tag.text.strip()
                    value = value_tag.text.strip()
                    metadata[label] = value
            
            images_data.append({
                'image_src': image_src,
                'prompt': metadata.get('Prompt', ''),
                'seed': metadata.get('Seed', ''),
                'full_raw_prompt': metadata.get('Full raw prompt', '')
            })
    
    return images_data

def file_exists_on_server(image_src):
    encoded_src = quote(image_src)  # Encode the image source URL
    url = f'{CHECK_FILE_API_URL}?filename={encoded_src}'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        json_response = response.json()
        return json_response.get('exists', False)
    except requests.exceptions.RequestException:
        return False

def upload_image(image_data):
    try:
        with open(image_data['image_src'], 'rb') as image_file:
            files = {'image': image_file}
            response = requests.post(UPLOAD_API_URL, files=files)
            response.raise_for_status()  # Raise an exception for HTTP errors
            json_response = response.json()
            if json_response.get('message') == 'File uploaded successfully.':
                post_metadata(image_data)
            else:
                print(f"Upload failed: {json_response.get('message', 'Unknown error')}")
    except FileNotFoundError:
        print(f"File not found: {image_data['image_src']}")
    except requests.exceptions.RequestException:
        print(f"Error uploading image: {image_data['image_src']}")

def post_metadata(image_data):
    metadata_url = 'https://ai.0u.gay/api/metadata.php'  # Replace with actual metadata API URL
    try:
        response = requests.post(metadata_url, json=image_data)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.exceptions.RequestException:
        print(f"Error posting metadata for: {image_data['image_src']}")

def countdown_with_progress_bar(duration):
    """Displays a countdown progress bar for a given duration."""
    with tqdm(total=duration, desc="Waiting", unit='s') as pbar:
        for _ in range(duration):
            time.sleep(1)  # Sleep for 1 second
            pbar.update(1)  # Update the progress bar

def main():
    while True:
        images_data = extract_image_data(LOG_FILE_PATH)
        # Use tqdm to display a progress bar for processing images
        for image_data in tqdm(images_data, desc="Processing Images"):
            if not file_exists_on_server(image_data['image_src']):
                upload_image(image_data)
        # countdown_with_progress_bar(60)  # Wait for 1 minute with a progress bar

if __name__ == "__main__":
    main()
