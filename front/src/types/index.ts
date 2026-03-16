export type UploadMethod = 'simple' | 'chunked' | 'streaming' | 'multipart_parallel';

export interface TabItem {
  id: string;
  label: string;
  icon?: string;
}

export interface MethodInfo {
  name: string;
  badge: string;
  desc: string;
  color: string;
}

export type UploadStatus = 'idle' | 'uploading' | 'complete' | 'error';

export interface UploadProgress {
  status: UploadStatus;
  percent: number;
  uploadedBytes: number;
  totalBytes: number;
  speed: number;
  elapsedSec: number;
}

export interface UploadResult {
  method: string;
  fileSize: number;
  timeSec: number;
  throughputMBps: number;
  memoryMB: number;
  progressAccuracy: number;
}
