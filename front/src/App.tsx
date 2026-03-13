import styles from './App.module.css';
import type {TabItem, UploadMethod} from './types';
import {Button, Card, MethodSelector, Tabs, UploadZone} from './components'
import {useState} from "react";
import {File, Zap} from 'lucide-react';

const TABS: TabItem[] = [
  { id: 'upload', label: '직접 업로드', icon: '📤' },
  { id: 'benchmark', label: '벤치마크', icon: '📊' }
];


function App() {
  const [activeTab, setActiveTab] = useState('upload');
  const [file, setFile] = useState<File | null>(null);
  const [method, setMethod] = useState<UploadMethod>('simple');

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
            <Card title={"파일 선택"} icon={File}>
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

              <Button>
                업로드 시작
              </Button>

            </Card>



          </>
        )}
      </div>


    </div>
  )
}

export default App
