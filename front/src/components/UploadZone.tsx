import type {ChangeEvent, DragEvent} from 'react';
import {useCallback, useRef, useState} from 'react';
import {File, Upload} from 'lucide-react';
import {formatSize} from '../utils/format';
import styles from './UploadZone.module.css';

interface UploadZoneProps {
  file: File | null;
  onFileSelect: (file: File) => void;
}

export function UploadZone({ file, onFileSelect }: UploadZoneProps) {
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) onFileSelect(droppedFile);
  }, [onFileSelect]);

  const handleDragOver = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setDragOver(false);
  }, []);

  const handleChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) onFileSelect(selected);
  }, [onFileSelect]);

  const handleClick = useCallback(() => {
    inputRef.current?.click();
  }, []);

  return (
    <div
      className={`${styles.zone} ${dragOver ? styles.dragOver : ''}`}
      onClick={handleClick}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
    >
      <input
        ref={inputRef}
        type="file"
        className={styles.input}
        onChange={handleChange}
      />

      <div className={styles.icon}>
        <Upload size={48} strokeWidth={1.5} />
      </div>

      <h3 className={styles.title}>파일을 드래그하거나 클릭하여 선택</h3>
      <p className={styles.subtitle}>모든 파일 형식 지원</p>

      {file && (
        <div className={styles.fileInfo}>
          <div className={styles.fileIcon}>
            <File size={20} />
          </div>
          <div className={styles.fileDetails}>
            <div className={styles.fileName}>{file.name}</div>
            <div className={styles.fileSize}>{formatSize(file.size)}</div>
          </div>
        </div>
      )}
    </div>
  );
}