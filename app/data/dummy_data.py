import os
import time


def generate_test_txt_files():
    # 파일 용량 정의 (바이트 단위)
    MB = 1024 * 1024
    GB = 1024 * 1024 * 1024

    target_sizes = {
        "10mb.txt": 10 * MB,
        "50mb.txt": 50 * MB,
        "100mb.txt": 100 * MB,
        "300mb.txt": 300 * MB,
        "500mb.txt": 500 * MB,
        "1gb.txt": 1 * GB,
        "3gb.txt": 3 * GB,
        "5gb.txt": 5 * GB,
        "10gb.txt": 10 * GB,
        "30gb.txt": 30 * GB
    }

    # output 폴더 생성
    os.makedirs("output", exist_ok=True)

    # 1MB 크기의 텍스트 청크 미리 생성 (쓰기 속도 최적화용)
    base_line = "FastAPI_Chunk_Upload_Test_Data_Row_" * 3 + "\n"
    base_bytes = base_line.encode('utf-8')
    chunk_size = 1 * MB

    # 1MB 크기에 맞게 문자열 반복
    repeats = chunk_size // len(base_bytes)
    chunk_data = base_bytes * repeats

    # 정확히 1MB(1048576 바이트)를 맞추기 위해 남은 공간 패딩
    chunk_data += b'A' * (chunk_size - len(chunk_data))

    print("파일 생성을 시작합니다...")

    for filename, target_size in target_sizes.items():
        filepath = os.path.join("output", filename)
        print(f"[{filename}] 생성 중... (목표: {target_size / MB:,.0f} MB)", end=" ", flush=True)

        start_time = time.time()

        # 파일 쓰기 작업
        with open(filepath, "wb") as f:
            written = 0
            while written < target_size:
                write_size = min(chunk_size, target_size - written)
                f.write(chunk_data[:write_size])
                written += write_size

        elapsed = time.time() - start_time
        print(f"-> 완료! (소요 시간: {elapsed:.2f}초)")


if __name__ == "__main__":
    generate_test_txt_files()
