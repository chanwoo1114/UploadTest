import type {MethodInfo, UploadMethod} from '../types';

export const METHODS: Record<UploadMethod, MethodInfo> = {
  simple: {
    name: 'Simple',
    badge: '~10MB',
    desc: '한 번에 전송, 가장 빠름',
    color: '#10b981'
  },
  chunked: {
    name: 'Chunked',
    badge: '10-500MB',
    desc: '분할 전송, 재시도 가능',
    color: '#3b82f6'
  },
  streaming: {
    name: 'Streaming',
    badge: '500MB+',
    desc: '메모리 효율적, 대용량',
    color: '#8b5cf6'
  },
  multipart_parallel: {
    name: 'Multipart',
    badge: '대용량',
    desc: '병렬 업로드, S3 스타일',
    color: '#f59e0b'
  }
};

export const DEFAULT_CHUNK_SIZE = 5 * 1024 * 1024;
export const DEFAULT_PART_SIZE = 10 * 1024 * 1024;