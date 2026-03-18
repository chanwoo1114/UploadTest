import type {UploadResult} from '../../types';
import {useMemo} from "react";
import styles from './SummaryCards.module.css'
import {Card} from '../Card'
import {METHOD_COLORS} from '../../utils/constants'

interface SummaryCardsProps {
  results: UploadResult[];
  totalTests: number;
  elapsedSec: number;
}

const METHOD_LABELS: Record<string, string> = {
  Simple: "직접 업로드",
  Streaming: "스트리밍 업로드",
  Chunked: "분할 업로드",
  Multipart: "S3 병렬 업로드",
};

export function SummaryCards({ results, totalTests, elapsedSec }: SummaryCardsProps) {
  const summary = useMemo(() => {
    if (results.length === 0) return null;
    const bestRow = results.reduce((a, b) => (a.throughputMBps > b.throughputMBps ? a : b));
    return {
      bestSpeed: Math.max(...results.map((r) => r.throughputMBps)),
      bestTime: Math.min(...results.map((r) => r.timeSec)),
      minMem: Math.min(...results.map((r) => r.memoryPeak)),
      minCpu: Math.min(...results.map((r) => r.cpuPeak)),
      maxCpu: Math.max(...results.map((r) => r.cpuPeak)),
      bestMethod: bestRow.method,
      bestLabel: METHOD_LABELS[bestRow.method] ?? bestRow.method,
    };
  }, [results]);

  if (!summary) return null;

  const cards = [
    { label: '서버 최고 속도', value: summary.bestSpeed.toFixed(1), unit: 'MB/s', color: '#10b981' },
    { label: '최단 시간', value: summary.bestTime.toFixed(3), unit: 'sec', color: '#3b82f6' },
    { label: '최소 메모리', value: summary.minMem.toFixed(1), unit: 'MB', color: '#8b5cf6' },
    { label: 'CPU 범위', value: `${summary.minCpu.toFixed(0)}~${summary.maxCpu.toFixed(0)}`, unit: '% peak', color: '#f59e0b' },
    { label: '추천 방식', value: summary.bestMethod, unit: '최고 처리량 기준', color: METHOD_COLORS[summary.bestMethod] ?? '#f0f0f5' },
  ];

  return (
    <>
      <div className={styles.banner}>
        ✓ {summary.bestLabel} 완료:{' '}
        <span className={styles.bannerStrong}>{totalTests}개 테스트</span> 완료, 총{' '}
        <span className={styles.bannerStrong}>{elapsedSec.toFixed(2)}초</span> 소요
      </div>
      <div className={styles.grid}>
        {cards.map((c) => (
          <Card key={c.label} variant="summary">
            <div className={styles.label}>{c.label}</div>
            <div className={styles.value} style={{ color: c.color }}>{c.value}</div>
            <div className={styles.unit}>{c.unit}</div>
          </Card>
        ))}
      </div>
    </>
  )
}