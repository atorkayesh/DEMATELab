import type { Ref } from "react";
import { ConfigurationPanel } from "@/components/page-specific/analysis/ConfigurationPanel";
import { FactorBadgeGroup } from "@/components/page-specific/analysis/FactorBadgeGroup";
import { ProminenceRanking } from "@/components/page-specific/analysis/ProminenceRanking";
import { StatBox } from "@/components/page-specific/analysis/StatBox";
import { STAT_BOXES, SUMMARY_TEXT } from "@/constants/results.constants";
import type { AnalysisData } from "@/interfaces/result.interface";
import { formatFixed, formatSigned } from "@/utils/format.utils";

/** The Summary tab: insights, configuration, cause and effect groups, prominence ranking. */
export function SummaryPanel({
  data,
  ref,
}: {
  data: AnalysisData;
  ref?: Ref<HTMLDivElement>;
}) {
  const { summary, result } = data;
  const stats = [
    { ...STAT_BOXES.DRIVING, value: String(summary.driving_factor_count) },
    { ...STAT_BOXES.DEPENDENT, value: String(summary.dependent_factor_count) },
    { ...STAT_BOXES.PROMINENCE, value: formatFixed(summary.top_prominence, 2) },
    {
      ...STAT_BOXES.RELATION,
      value: formatSigned(summary.strongest_relation, 2),
    },
  ];

  return (
    <div ref={ref} className="flex flex-col gap-4 bg-card p-1">
      <section className="flex flex-col gap-3">
        <div>
          <h3 className="font-semibold">{SUMMARY_TEXT.INSIGHTS_TITLE}</h3>
          <p className="text-sm text-muted-foreground">
            {SUMMARY_TEXT.INSIGHTS_SUBTITLE}
          </p>
        </div>
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
          {stats.map((stat) => (
            <StatBox key={stat.title} {...stat} />
          ))}
        </div>
      </section>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-12">
        <div className="flex flex-col gap-4 md:col-span-5">
          <ConfigurationPanel summary={summary} />
          <FactorBadgeGroup
            title={SUMMARY_TEXT.CAUSE_TITLE}
            factors={result.cause_group}
            tone="cause"
          />
          <FactorBadgeGroup
            title={SUMMARY_TEXT.EFFECT_TITLE}
            factors={result.effect_group}
            tone="effect"
          />
        </div>
        <div className="md:col-span-7">
          <ProminenceRanking summary={summary} />
        </div>
      </div>
    </div>
  );
}
