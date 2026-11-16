import { SCORE_HEADERS } from "@/constants/results.constants";
import type { AnalysisResult } from "@/interfaces/result.interface";
import { formatResultValue } from "@/utils/format.utils";
import { resultScores } from "@/utils/result.utils";

/** R/C scores: `Factor | R | C | R+C | R-C` (crisp) or with Prominence/Relation tuples. */
export function ScoresTable({ result }: { result: AnalysisResult }) {
  const { tuples, rows } = resultScores(result);
  const headers = tuples ? SCORE_HEADERS.TUPLE : SCORE_HEADERS.CRISP;

  return (
    <div className="w-full overflow-x-auto rounded-lg border">
      <table className="w-max min-w-full text-sm">
        <thead className="bg-muted">
          <tr>
            {headers.map((header, i) => (
              <th
                key={header}
                scope="col"
                className={
                  i === 0 ? "px-3 py-2 text-left" : "px-3 py-2 text-right"
                }
              >
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y">
          {rows.map((row) => (
            <tr key={row.factor}>
              <th scope="row" className="px-3 py-2 text-left font-semibold">
                {row.factor}
              </th>
              {row.values.map((value, i) => (
                <td
                  key={headers[i + 1]}
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
