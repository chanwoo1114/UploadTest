import requests
from client import (
    BASE_URL, CHUNK_SIZE,
    UPLOAD_PATH,
)
from pathlib import Path

def stream_file_in_5mb(file_path: str):
    with open(file_path, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            yield chunk


def test_streaming_upload(file_path: str, size: int, type: str):
    full_path = Path(file_path) / f'{size}{type}.txt'
    filename = full_path.name

    response = requests.post(
        f"{BASE_URL}/streaming/upload",
        params={"filename": filename, "size": full_path.stat().st_size},
        data=stream_file_in_5mb(full_path),
        headers={"Content-Type": "application/octet-stream"},
    )

    print(f"응답 코드: {response.status_code}")
    print(f"응답: {response.json()}")
