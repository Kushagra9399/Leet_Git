from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import base64
import requests

from dotenv import load_dotenv
import os

load_dotenv()  # Loads from .env

# ====== FIXED CONFIGURATION ======
GITHUB_USERNAME = "Kushagra9399"
REPO_NAME = "Leetcode"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
BRANCH = "main"

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def upload_text_as_file(file_name, file_content):
    # Encode content to base64 (required by GitHub API)
    content_encoded = base64.b64encode(file_content.encode("utf-8")).decode("utf-8")

    # GitHub API URL to upload file to root of the repo
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/contents/{file_name}"

    # Payload for GitHub API
    data = {
        "message": f"Add {file_name}",
        "content": content_encoded,
        "branch": BRANCH
    }

    # Send PUT request
    response = requests.put(url, json=data, auth=(GITHUB_USERNAME, GITHUB_TOKEN))

    if response.status_code == 201:
        message = f"✅ File '{file_name}' uploaded successfully to the repo."
        print(f"✅ File '{file_name}' uploaded successfully to the repo.")
        return True, message
    elif response.status_code == 422:
        message = f"❌ File '{file_name}' already exists on GitHub."
        print("❌ File already exists on GitHub. Use update logic if needed.")
        print(response.json())
        return False, message
    else:
        message = "❌ Upload failed:", response.status_code
        print("❌ Upload failed:", response.status_code)
        print(response.json())
        return False, message


# Show the form (GET)
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Handle form submission (POST)
@app.post("/submit", response_class=HTMLResponse)
def submit_form(
    request: Request,
    filename: str = Form(...),
    content: str = Form(...)
):
    file_name = filename.strip().split(" ")
    filename = "_".join(file_name) + ".py"
    successfully_upload, message = upload_text_as_file(filename, content)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "uploaded":successfully_upload, "message": message}
    )
