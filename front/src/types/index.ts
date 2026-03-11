export type UploadMethod = 'simple' | 'chunked' | 'streaming' | 'multipart_parallel';

export interface TabItem {
  id: string;
  label: string;
  icon?: string;
}