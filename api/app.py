from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
from pathlib import Path

#Regex to get links
import re

# Initialize FastAPI app
app = FastAPI()

# Create a directory to store downloads
DOWNLOAD_DIR = "downloads"
Path(DOWNLOAD_DIR).mkdir(exist_ok=True)

# Input Model
class URLInput(BaseModel):
    url: HttpUrl

# Function to download a file
def download_file(file_url: str, output_dir: str):
    local_filename = os.path.join(output_dir, file_url.split("/")[-1])
    response = requests.get(file_url, stream=True)
    if response.status_code == 200:
        with open(local_filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        return local_filename
    else:
        raise Exception(f"Failed to download file from {file_url}")

# Process the URL
@app.post("/process-url/")
async def process_url(input: URLInput):
    try:
        #https://jupyter.org/try is loaded
        url = input.url
        response = requests.get(url)
        response.raise_for_status()

        # Parse HTML content -- nothing to be concerned for here
        soup = BeautifulSoup(response.text, "html.parser")
        #links = [a.get("href") for a in soup.find_all("a", href=True)]

        links = []
        for x in soup.find_all("a", href=True):
            links.append(x.get("href"))

        #print(f"Links to visit: {links}")
        # Supported file extensions-- nothing to be concerned for here
        supported_extensions = [".pdf", ".ipynb", ".mp4"]
        files_found = []

        formatted_links = []
        # Crawl through the links
       
        for link in links:
            """
            if link.strip() and link[-1] != '/':
                absolute_url = link + '/'
            else:
                absolute_url = link
            """
            absolute_url = link
            print(absolute_url) 
            if (absolute_url.endswith(ext) for ext in supported_extensions):
                try:
                    # Download the file
                    downloaded_file = download_file(absolute_url, DOWNLOAD_DIR)
                    files_found.append(absolute_url)
                except Exception as e:
                    print(f"Error downloading {absolute_url}: {e}")

        return {"status": "success", "files": files_found}

    except Exception as e:
        print(f"This is the error: {e}")
