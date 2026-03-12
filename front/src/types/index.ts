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
