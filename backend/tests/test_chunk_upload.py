import math
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from client import (
    BASE_URL, CHUNK_SIZE,
)
from pathlib import Path

MAX_WORKERS = 8


def upload_one_chunk(session_id: str, chunk_number: int, chunk_data: bytes) -> dict:
    resp = requests.post(
        f"{BASE_URL}/chunk/sessions/{session_id}/chunks/{chunk_number}",
        files={"chunk": (f"chunk_{chunk_number}", chunk_data, "application/octet-stream")},
    )
    resp.raise_for_status()
    return resp.json()


def test_chunk_upload(file_path: str, size: int, type: str, session_id: str = None):
    full_path = Path(file_path) / f'{size}{type}.txt'
    filename = full_path.name
    file_size = full_path.stat().st_size
    total_chunks = math.ceil(file_size / CHUNK_SIZE)

    # 이어받기: 기존 세션이 있으면 상태 조회
    if session_id:
        print(f"[이어받기] 세션 {session_id} 복구 시도")
        status_resp = requests.get(
            f"{BASE_URL}/chunk/sessions/{session_id}/status",
        )
        if status_resp.status_code != 200:
            print(f"[이어받기] 세션 복구 실패: {status_resp.status_code} - {status_resp.text}")
            return
        status_data = status_resp.json()
        uploaded_set = set(status_data["uploaded_chunks"])
        remaining = status_data["remaining_chunks"]
        print(f"[이어받기] 이미 업로드된 청크: {len(uploaded_set)}/{total_chunks}, "
              f"남은 청크: {len(remaining)}개")
    else:
        # 새 세션 생성
        session_resp = requests.post(
            f"{BASE_URL}/chunk/sessions",
            json={
                "filename": filename,
                "total_size": file_size,
                "chunk_size": CHUNK_SIZE,
                "total_chunks": total_chunks,
            },
        )
        print(f"[세션 생성] 응답 코드: {session_resp.status_code}")
        session_data = session_resp.json()
        print(f"[세션 생성] 응답: {session_data}")

        if session_resp.status_code != 200:
            print("세션 생성 실패, 테스트 중단")
            return

        session_id = session_data["session_id"]
        uploaded_set = set()
        remaining = list(range(1, total_chunks + 1))

    # 청크 업로드 (남은 것만)
    remaining_set = set(remaining)
    chunks = []
    with open(full_path, "rb") as f:
        for i in range(1, total_chunks + 1):
            chunk_data = f.read(CHUNK_SIZE)
            if i in remaining_set:
                chunks.append((i, chunk_data))

    uploaded = 0
    total_remaining = len(chunks)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(upload_one_chunk, session_id, num, data): num
            for num, data in chunks
        }
        for future in as_completed(futures):
            chunk_number = futures[future]
            try:
                future.result()
                uploaded += 1
                if uploaded % 50 == 0 or uploaded == total_remaining:
                    print(f"[진행] {uploaded}/{total_remaining} 청크 완료")
            except Exception as e:
                print(f"[청크 {chunk_number}] 업로드 실패: {e}")
                print(f"[중단] session_id: {session_id} (이어받기용)")
                return

    # 상태 조회
    status_resp = requests.get(
        f"{BASE_URL}/chunk/sessions/{session_id}/status",
    )
    print(f"\n[상태 조회] 응답 코드: {status_resp.status_code}")
    status_data = status_resp.json()
    print(f"[상태 조회] progress: {status_data['progress_percent']}%, "
          f"uploaded: {status_data['uploaded_size']}/{status_data['total_size']}")

    # 완료 요청
    complete_resp = requests.post(
        f"{BASE_URL}/chunk/sessions/{session_id}/complete",
    )
    print(f"\n[완료] 응답 코드: {complete_resp.status_code}")
    complete_data = complete_resp.json()
    print(f"[완료] 응답: {complete_data}")
