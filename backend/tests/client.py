from pathlib import Path

BASE_URL = 'http://localhost:8000'
CHUNK_SIZE = 5 * 1024 * 1024
UPLOAD_PATH = Path(__file__).parent.parent / 'app' / 'data' / 'output'