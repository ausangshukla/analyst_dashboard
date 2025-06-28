from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import List
import httpx
import os
import uuid
import shutil
import asyncio
from dashboard_generator import DashboardGenerator

app = FastAPI()

class FileDownload(BaseModel):
    file_name: str
    url: str

class URLList(BaseModel):
    files: List[FileDownload]

@app.post("/download-files/")
async def download_files(url_list: URLList, background_tasks: BackgroundTasks):
    unique_id = str(uuid.uuid4())
    download_dir = os.path.join("downloads", unique_id)
    os.makedirs(download_dir, exist_ok=True)
    downloaded_files = []

    async with httpx.AsyncClient() as client:
        for file_entry in url_list.files:
            file_name = file_entry.file_name
            url = file_entry.url
            try:
                response = await client.get(url)
                response.raise_for_status()  # Raise an exception for HTTP errors

                filename = os.path.join(download_dir, file_name)
                with open(filename, "wb") as f:
                    f.write(response.content)
                downloaded_files.append(filename)
            except httpx.HTTPStatusError as e:
                print(f"HTTP error downloading {url} (file: {file_name}): {e}")
            except Exception as e:
                print(f"Error downloading {url} (file: {file_name}): {e}")

    dashboard_generator = DashboardGenerator(download_dir)
    background_tasks.add_task(dashboard_generator.generate_dashboard)
    return {"message": "Files downloaded successfully, dashboard generation started in background", "download_directory": download_dir, "downloaded_files": downloaded_files}