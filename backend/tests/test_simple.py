import requests
from client import (
    BASE_URL, UPLOAD_PATH
)
from pathlib import Path

def test_simple_upload(file_path: str, size: int, type: str):
    full_path = Path(file_path) / f"{size}{type}.txt"

    with open(full_path, "rb") as f:
        response = requests.post(
            f"{BASE_URL}/simple/upload",
            files={"file": (full_path.name, f, "application/octet-stream")},
        )

    print(f"응답 코드: {response.status_code}")
    print(f"응답: {response.json()}")
