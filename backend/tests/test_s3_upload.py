import math
import requests
from client import (
    BASE_URL, CHUNK_SIZE,
    UPLOAD_PATH,
)
from pathlib import Path


def test_s3_upload(file_path: str, size: int, type: str):
    full_path = Path(file_path) / f"{size}{type}.txt"
    file_size = full_path.stat().st_size
    part_size = CHUNK_SIZE
    total_parts = math.ceil(file_size / part_size)

    # 1. 초기화
    init_res = requests.post(
        f"{BASE_URL}/s3/init",
        json={
            "filename": full_path.name,
            "total_size": file_size,
            "part_size": part_size,
            "concurrency": 4,
        },
    )
    print(f"초기화 응답 코드: {init_res.status_code}")
    init_data = init_res.json()
    print(f"초기화 응답: {init_data}")
    upload_id = init_data["upload_id"]

    # 2. 파트 업로드
    parts_info = []
    with open(full_path, "rb") as f:
        for part_number in range(1, total_parts + 1):
            part_data = f.read(part_size)
            part_res = requests.post(
                f"{BASE_URL}/s3/{upload_id}/parts/{part_number}",
                files={"part": (f"part_{part_number}", part_data, "application/octet-stream")},
            )
            part_json = part_res.json()
            parts_info.append({
                "part_number": part_json["part_number"],
                "etag": part_json["etag"],
                "size": part_json["size"],
            })
            print(f"파트 {part_number}/{total_parts} 업로드 완료 (etag: {part_json['etag'][:8]}...)")

    # 3. 업로드 완료
    complete_res = requests.post(
        f"{BASE_URL}/s3/{upload_id}/complete",
        json={
            "upload_id": upload_id,
            "parts": parts_info,
        },
    )
    print(f"완료 응답 코드: {complete_res.status_code}")
    print(f"완료 응답: {complete_res.json()}")


test_s3_upload(UPLOAD_PATH, 500, 'mb')
