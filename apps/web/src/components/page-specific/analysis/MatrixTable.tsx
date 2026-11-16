import type { ResultValue } from "@/interfaces/result.interface";
import { formatResultValue } from "@/utils/format.utils";

/** A result matrix with factor names as row and column headers (4 decimals or tuples). */
export function MatrixTable({
  factors,
  matrix,
  caption,
}: {
  factors: string[];
  matrix: ResultValue[][];
  caption: string;
}) {
  return (
    <div className="w-full overflow-x-auto rounded-lg border">
      <table className="w-max min-w-full text-sm">
        <caption className="sr-only">{caption}</caption>
        <thead className="bg-muted">
          <tr>
            <th scope="col" className="sticky left-0 bg-muted px-3 py-2" />
            {factors.map((factor) => (
              <th
                key={factor}
                scope="col"
                className="px-3 py-2 text-right font-semibold"
              >
                {factor}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y">
          {matrix.map((row, i) => (
            <tr key={factors[i]}>
              <th
                scope="row"
                className="sticky left-0 bg-card px-3 py-2 text-left font-semibold"
              >
                {factors[i]}
              </th>
              {row.map((value, j) => (
                <td
                  key={factors[j]}
                  className="px-3 py-2 text-right tabular-nums"
                >
                  {formatResultValue(value)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
