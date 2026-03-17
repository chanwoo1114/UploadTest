import styles from './App.module.css';
import type {TabItem, UploadMethod, UploadProgress, UploadResult} from './types';
import {BenchmarkResults, Button, Card, MethodSelector, ProgressBar, Tabs, UploadZone} from './components'
import {useCallback, useRef, useState} from "react";
import {File as FileIcon, Zap} from 'lucide-react';
import {uploadFile} from './services/api';

const TABS: TabItem[] = [
  { id: 'upload', label: '직접 업로드', icon: '📤' },
  { id: 'benchmark', label: '벤치마크', icon: '📊' }
];

const INITIAL_PROGRESS: UploadProgress = {
  status: 'idle',
  percent: 0,
  uploadedBytes: 0,
  totalBytes: 0,
  speed: 0,
  elapsedSec: 0,
};

function App() {
  const [activeTab, setActiveTab] = useState('upload');
  const [file, setFile] = useState<File | null>(null);
  const [method, setMethod] = useState<UploadMethod>('simple');
  const [progress, setProgress] = useState<UploadProgress>(INITIAL_PROGRESS);
  const [results, setResults] = useState<UploadResult[]>([]);
  const firstUploadTime = useRef<number>(0);

  const isUploading = progress.status === 'uploading';
  const showProgress = progress.status === 'uploading' || progress.status === 'complete';

  const handleUpload = useCallback(async () => {
    if (!file || isUploading) return;

    setProgress(INITIAL_PROGRESS);

    if (results.length === 0) {
      firstUploadTime.current = performance.now();
    }

    try {
      const result = await uploadFile(file, method, (p) => {
        setProgress(p);
      });
      setResults((prev) => [...prev, result]);
    } catch (err) {
      console.error('Upload failed:', err);
      setProgress((prev) => ({ ...prev, status: 'error' }));
    }
  }, [file, method, isUploading, results.length]);

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1 className={styles.title}>Upload Benchmark</h1>
        <p className={styles.subtitle}>
          파일 업로드 방식별 성능을 비교하고 최적의 방식을 찾아보세요.
        </p>
      </header>

      <Tabs tabs={TABS} activeTab={activeTab} onChange={setActiveTab} />

      <div className={styles.grid}>
        {activeTab === 'upload' && (
          <>
            <Card title={"파일 선택"} icon={FileIcon}>
              <UploadZone
                file={file}
                onFileSelect={setFile}
              />
            </Card>

            <Card title={"업로드 방식"} icon={Zap}>
              <MethodSelector
                selected={method}
                onChange={setMethod}
              />

              <Button
                onClick={handleUpload}
                disabled={!file || isUploading}
              >
                {isUploading ? '업로드 중...' : '업로드 시작'}
              </Button>
              {showProgress && <ProgressBar progress={progress} />}
            </Card>

            {results.length > 0 && (
              <BenchmarkResults
                results={results}

              />
            )}
          </>
        )}
      </div>


    </div>
  )
}

export default App
