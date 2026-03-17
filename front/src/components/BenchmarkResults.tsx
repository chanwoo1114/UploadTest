import type {UploadResult} from "../types";

interface BenchmarkResultsProps {
  results: UploadResult[];

}

export function BenchmarkResults({
  results,
}: BenchmarkResultsProps) {
  return (
    <div>
      <SummaryCards />
    </div>
  )
}