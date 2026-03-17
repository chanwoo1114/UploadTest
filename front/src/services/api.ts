import type {TimeSample, UploadMethod, UploadProgress, UploadResult} from '../types';

type OnProgress = (progress: UploadProgress) => void;

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000';

function makeProgress(
  status: UploadProgress['status'],
  uploaded: number,
  total: number,
  startTime: number,
): UploadProgress {
  const now = performance.now();
  const elapsedSec = (now - startTime) / 1000;
  const speed = elapsedSec > 0 ? uploaded / elapsedSec : 0;
  const percent = total > 0 ? (uploaded / total) * 100 : 0;
  return { status, percent, uploadedBytes: uploaded, totalBytes: total, speed, elapsedSec };
}

function parseMetrics(method: string, fileSize: number, metrics: any): UploadResult {
  const timeSec = metrics?.time?.total_sec ?? 0;
  const uploadSec = metrics?.time?.upload_sec ?? timeSec;
  const processingSec = metrics?.time?.processing_sec ?? 0;
  const throughput = timeSec > 0 ? (fileSize / 1024 / 1024) / timeSec : 0;

  const cpuSamples: TimeSample[] = (metrics?.cpu?.samples ?? []).map((s: any) => ({
    elapsedSec: s.elapsed_sec,
    value: s.value,
  }));

  const memorySamples: TimeSample[] = (metrics?.memory?.samples ?? []).map((s: any) => ({
    elapsedSec: s.elapsed_sec,
    value: s.value,
  }));

  return {
    method,
    fileSize,
    success: metrics?.success ?? true,
    timeSec,
    uploadSec,
    processingSec,
    throughputMBps: throughput,
    networkSpeedMBps: metrics?.network?.speed_avg_mbps ?? 0,
    cpuPeak: metrics?.cpu?.peak ?? 0,
    cpuAvg: metrics?.cpu?.avg ?? 0,
    cpuSamples,
    memoryPeak: metrics?.memory?.peak ?? 0,
    memoryAvg: metrics?.memory?.avg ?? 0,
    memorySamples,
    progressAccuracy: 100,
  };
}

export { parseMetrics };

async function simpleUpload(
  file: File,
  onProgress: OnProgress,
): Promise<UploadResult> {
  const startTime = performance.now();
  const total = file.size;

  onProgress(makeProgress('uploading', 0, total, startTime));

  const xhr = new XMLHttpRequest();
  const formData = new FormData();
  formData.append('file', file);

  const result = await new Promise<any>((resolve, reject) => {
    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable) {
        onProgress(makeProgress('uploading', e.loaded, total, startTime));
      }
    });
    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(JSON.parse(xhr.responseText));
      } else {
        reject(new Error(`Upload failed: ${xhr.status}`));
      }
    });
    xhr.addEventListener('error', () => reject(new Error('Network error')));
    xhr.open('POST', `${API_BASE}/simple/upload`);
    xhr.send(formData);
  });

  onProgress(makeProgress('complete', total, total, startTime));
  return parseMetrics('Simple', total, result.metrics);
}


export async function uploadFile(
  file: File,
  method: UploadMethod,
  onProgress: OnProgress,
): Promise<UploadResult> {
  switch (method) {
    case 'simple':
      return simpleUpload(file, onProgress);
    // case 'chunked':
    //   return chunkedUpload(file, onProgress);
    // case 'streaming':
    //   return streamingUpload(file, onProgress);
    // case 'multipart_parallel':
    //   return multipartUpload(file, onProgress);
  }
}
