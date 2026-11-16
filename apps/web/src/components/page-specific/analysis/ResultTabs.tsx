import { CausalDiagramPanel } from "@/components/page-specific/analysis/CausalDiagramPanel";
import { ExplanationPanel } from "@/components/page-specific/analysis/ExplanationPanel";
import { HeatmapPanel } from "@/components/page-specific/analysis/HeatmapPanel";
import { MatrixTable } from "@/components/page-specific/analysis/MatrixTable";
import { ScoresTable } from "@/components/page-specific/analysis/ScoresTable";
import { SummaryPanel } from "@/components/page-specific/analysis/SummaryPanel";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  MATRIX_TAB_PREFIX,
  MATRIX_TABS,
  TAB_IDS,
  TAB_LABELS,
} from "@/constants/results.constants";
import type { AnalysisRequest } from "@/interfaces/analysis.interface";
import type { AnalysisData } from "@/interfaces/result.interface";
import { hasTotalMatrix, resultMatrix } from "@/utils/result.utils";

const TRIGGER_CLASS = "flex-none px-3 max-sm:h-10";

/**
 * Qt's result tabs as a segmented control. Only the open tab is mounted (charts load on first
 * view), except the AI tab, which keeps its key, output and endpoint while the results stay.
 */
export function ResultTabs({
  snapshot,
  snapshotHash,
  data,
}: {
  snapshot: AnalysisRequest;
  snapshotHash: string;
  data: AnalysisData;
}) {
  const { result } = data;
  const prefix = MATRIX_TAB_PREFIX[result.solver_type] ?? "";
  const available = hasTotalMatrix(result);

  return (
    <Tabs defaultValue={TAB_IDS.SUMMARY} className="gap-4">
      <div className="w-full overflow-x-auto pb-1">
        <TabsList className="h-9 max-sm:h-11">
          <TabsTrigger value={TAB_IDS.SUMMARY} className={TRIGGER_CLASS}>
            {TAB_LABELS.SUMMARY}
          </TabsTrigger>
          {MATRIX_TABS.map((tab) => (
            <TabsTrigger
              key={tab.kind}
              value={tab.kind}
              className={TRIGGER_CLASS}
            >
              {prefix}
              {tab.title}
            </TabsTrigger>
          ))}
          <TabsTrigger value={TAB_IDS.SCORES} className={TRIGGER_CLASS}>
            {TAB_LABELS.SCORES}
          </TabsTrigger>
          <TabsTrigger value={TAB_IDS.CAUSAL} className={TRIGGER_CLASS}>
            {TAB_LABELS.CAUSAL}
          </TabsTrigger>
          <TabsTrigger value={TAB_IDS.HEATMAP} className={TRIGGER_CLASS}>
            {TAB_LABELS.HEATMAP}
          </TabsTrigger>
          <TabsTrigger value={TAB_IDS.AI} className={TRIGGER_CLASS}>
            {TAB_LABELS.AI}
          </TabsTrigger>
        </TabsList>
      </div>
      <TabsContent value={TAB_IDS.SUMMARY}>
        <SummaryPanel data={data} />
      </TabsContent>
      {MATRIX_TABS.map((tab) => (
        <TabsContent key={tab.kind} value={tab.kind}>
          <MatrixTable
            factors={result.factors}
            matrix={resultMatrix(result, tab.kind)}
            caption={`${prefix}${tab.title}`}
          />
        </TabsContent>
      ))}
      <TabsContent value={TAB_IDS.SCORES}>
        <ScoresTable result={result} />
      </TabsContent>
      <TabsContent value={TAB_IDS.CAUSAL}>
        <CausalDiagramPanel
          snapshot={snapshot}
          snapshotHash={snapshotHash}
          available={available}
        />
      </TabsContent>
      <TabsContent value={TAB_IDS.HEATMAP}>
        <HeatmapPanel
          snapshot={snapshot}
          snapshotHash={snapshotHash}
          available={available}
        />
      </TabsContent>
      <TabsContent value={TAB_IDS.AI} keepMounted>
        <ExplanationPanel snapshot={snapshot} />
      </TabsContent>
    </Tabs>
  );
}
