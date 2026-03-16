import type {UploadProgress} from '../types';
import {formatSize} from '../utils/format';
import styles from './ProgressBar.module.css';

interface ProgressBarProps {
  progress: UploadProgress;
}

export function ProgressBar({ progress }: ProgressBarProps) {
  const { percent, uploadedBytes, speed, elapsedSec, status } = progress;

  const label = status === 'complete' ? '업로드 완료' : '업로드 중...';
  const speedStr = formatSize(speed) + '/s';
  const timeStr = elapsedSec.toFixed(2) + 's';

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <span className={styles.label}>{label}</span>
        <span className={styles.percent}>{Math.round(percent)}%</span>
      </div>

      <div className={styles.track}>
        <div
          className={styles.bar}
          style={{ width: `${Math.min(percent, 100)}%` }}
        />
      </div>

      <div className={styles.stats}>
        <div className={styles.stat}>
          <div className={styles.statValue}>{formatSize(uploadedBytes)}</div>
          <div className={styles.statLabel}>업로드됨</div>
        </div>
        <div className={styles.stat}>
          <div className={styles.statValue}>{speedStr}</div>
          <div className={styles.statLabel}>속도</div>
        </div>
        <div className={styles.stat}>
          <div className={styles.statValue}>{timeStr}</div>
          <div className={styles.statLabel}>경과 시간</div>
        </div>
      </div>
    </div>
  );
}
