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
  speed: number;       // bytes/sec
  elapsedSec: number;
}

export interface TimeSample {
  elapsedSec: number;
  value: number;
}

export interface UploadResult {
  method: string;
  fileSize: number;
  success: boolean;

  timeSec: number;
  uploadSec: number;
  processingSec: number;

  throughputMBps: number;
  networkSpeedMBps: number;

  cpuPeak: number;
  cpuAvg: number;
  cpuSamples: TimeSample[];

  memoryPeak: number;
  memoryAvg: number;
  memorySamples: TimeSample[];

  progressAccuracy: number;
}