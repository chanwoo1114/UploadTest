import styles from './App.module.css';
import type {TabItem} from './types';
import {Tabs} from './components/Tabs.tsx'
import {useState} from "react";

const TABS: TabItem[] = [
  { id: 'upload', label: '직접 업로드', icon: '📤' },
  { id: 'benchmark', label: '벤치마크', icon: '📊' }
];


function App() {
  const [activeTab, setActiveTab] = useState('upload');

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1 className={styles.title}>Upload Benchmark</h1>
        <p className={styles.subtitle}>
          파일 업로드 방식별 성능을 비교하고 최적의 방식을 찾아보세요.
        </p>
      </header>

      <Tabs tabs={TABS} />

      <div className={styles.grid}>
        {activeTab === 'upload' && (
          <>
            <p>test</p>
          </>
        )}
      </div>


    </div>
  )
}

export default App
