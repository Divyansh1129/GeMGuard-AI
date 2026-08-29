import React from "react";
import { AlertCircle, CheckCircle, ArrowRight, ExternalLink } from "lucide-react";
import Button from "../common/Button";

export default function IssueCard({ issue, onMarkReviewed }) {
  const isHigh = issue.severity.toLowerCase() === "high";

  return (
    <div
      className={`rounded-lg border p-4 transition-all duration-200 ${
        issue.reviewed
          ? "bg-surface-container-low/50 border-outline-variant/40 opacity-75"
          : isHigh
          ? "bg-red-50/30 border-red-200"
          : "bg-amber-50/30 border-amber-200"
      }`}
    >
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex items-start gap-2.5">
          <div
            className={`p-1.5 rounded-md mt-0.5 ${
              issue.reviewed
                ? "bg-surface-container text-on-surface-variant"
                : isHigh
                ? "bg-red-100 text-red-700"
                : "bg-amber-100 text-amber-700"
            }`}
          >
            <AlertCircle className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h4 className="text-sm font-bold text-on-surface">{issue.title}</h4>
              <span
                className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase ${
                  isHigh
                    ? "bg-red-100 text-red-800"
                    : "bg-amber-100 text-amber-800"
                }`}
              >
                {issue.severity} Severity
              </span>
              {issue.reviewed && (
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-green-100 text-green-800 flex items-center gap-1">
                  <CheckCircle className="w-3 h-3" /> Reviewed
                </span>
              )}
            </div>
            <p className="text-xs text-on-surface-variant mt-1">
              {issue.description}
            </p>
          </div>
        </div>

        <div className="text-right shrink-0">
          <span className="text-[10px] text-on-surface-variant uppercase font-semibold block">
            Confidence
          </span>
          <span className="text-xs font-bold text-primary">
            {issue.aiConfidence}%
          </span>
        </div>
      </div>

      {/* Affected Documents */}
      <div className="flex flex-wrap items-center gap-2 my-3 text-xs">
        <span className="text-on-surface-variant font-medium">Affected:</span>
        {issue.affectedDocuments?.map((doc, idx) => (
          <span
            key={idx}
            className="px-2 py-0.5 rounded bg-surface-container border border-outline-variant/60 font-semibold text-on-surface text-[11px]"
          >
            {doc}
          </span>
        ))}
      </div>

      {/* AI Explanation / Evidence */}
      {issue.details?.aiExplanation && (
        <div className="bg-surface-container-lowest/80 border border-outline-variant/40 rounded p-2.5 text-xs text-on-surface mb-3 leading-relaxed">
          <span className="font-semibold text-primary block mb-0.5">
            AI Finding Detail:
          </span>
          {issue.details.aiExplanation}
        </div>
      )}

      {/* Footer / Actions */}
      <div className="flex items-center justify-between pt-2 border-t border-outline-variant/30 text-xs">
        <span className="text-on-surface-variant font-medium">
          Action: <strong className="text-on-surface">{issue.recommendedAction}</strong>
        </span>

        <Button
          variant={issue.reviewed ? "secondary" : "outline"}
          size="sm"
          onClick={() => onMarkReviewed(issue.id)}
        >
          {issue.reviewed ? "Mark Unreviewed" : "Mark as Reviewed"}
        </Button>
      </div>
    </div>
  );
}
