import math
import requests
from client import (
    BASE_URL, CHUNK_SIZE,
    UPLOAD_PATH,
)
from pathlib import Path


def test_chunk_upload(file_path: str, size: int, type: str):
    full_path = Path(file_path) / f"{size}{type}.txt"
    file_size = full_path.stat().st_size
    total_chunks = math.ceil(file_size / CHUNK_SIZE)

    # 1. 세션 생성
    session_res = requests.post(
        f"{BASE_URL}/chunk/sessions",
        json={
            "filename": full_path.name,
            "total_size": file_size,
            "chunk_size": CHUNK_SIZE,
            "total_chunks": total_chunks,
        },
    )
    print(f"세션 생성 응답 코드: {session_res.status_code}")
    session_data = session_res.json()
    print(f"세션 생성 응답: {session_data}")
    session_id = session_data["session_id"]

    # 2. 청크 업로드
    with open(full_path, "rb") as f:
        for chunk_number in range(1, total_chunks + 1):
            chunk_data = f.read(CHUNK_SIZE)
            chunk_res = requests.post(
                f"{BASE_URL}/chunk/sessions/{session_id}/chunks/{chunk_number}",
                files={"chunk": (f"chunk_{chunk_number}", chunk_data, "application/octet-stream")},
            )
            remaining = chunk_res.json().get("remaining_chunks", "?")
            print(f"청크 {chunk_number}/{total_chunks} 업로드 완료 (남은 청크: {remaining})")

    # 3. 상태 확인
    status_res = requests.get(
        f"{BASE_URL}/chunk/sessions/{session_id}/status",
    )
    print(f"상태 조회 응답 코드: {status_res.status_code}")
    print(f"상태 조회 응답: {status_res.json()}")

    # 4. 업로드 완료
    complete_res = requests.post(
        f"{BASE_URL}/chunk/sessions/{session_id}/complete",
    )
    print(f"완료 응답 코드: {complete_res.status_code}")
    print(f"완료 응답: {complete_res.json()}")


# test_chunk_upload(UPLOAD_PATH, 500, 'mb')
