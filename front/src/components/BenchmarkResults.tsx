import type {UploadResult} from "../types";
import {ChartGrid, SummaryCards} from "./benchmark"

interface BenchmarkResultsProps {
  results: UploadResult[];
  totalTests: number;
  elapsedSec: number;
}

export function BenchmarkResults({
  results,
  totalTests,
  elapsedSec,
}: BenchmarkResultsProps) {
  return (
    <div style={{ gridColumn: '1 / -1' }}>
      <SummaryCards results={results} totalTests={totalTests} elapsedSec={elapsedSec} />
      <ChartGrid results={results} />
    </div>
  )
}