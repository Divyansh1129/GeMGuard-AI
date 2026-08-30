import React from "react";
import { Sparkles, CheckCircle2, AlertTriangle, XCircle, Info } from "lucide-react";

export default function AIAssessment({
  confidence = null,
  status = "PENDING",
  findings = [],
  reasoning = "No evidence assessment is available yet.",
  recommendation = "Upload documents and run the compliance check.",
}) {
  return (
    <div className="bg-surface-container-lowest border border-outline-variant/60 rounded-lg p-5">
      <div className="flex items-center justify-between pb-3 border-b border-outline-variant/40 mb-4">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-md bg-primary-container text-on-primary-container">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-on-surface uppercase tracking-wide">
              AI Compliance Assessment
            </h3>
            <span className="text-[11px] text-on-surface-variant">
              Advisory analysis grounded in extracted document evidence
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-right">
            <div className="text-[10px] text-on-surface-variant font-semibold uppercase">
              AI Confidence
            </div>
            <div className="text-sm font-bold text-primary">{confidence ?? "—"}%</div>
          </div>
          <div className="px-2.5 py-1 rounded-md bg-amber-50 border border-amber-200 text-amber-800 text-xs font-bold tracking-wider">
            {status}
          </div>
        </div>
      </div>

      {/* Structured Findings */}
      <div className="space-y-2 mb-4">
        <span className="text-xs font-bold text-on-surface-variant uppercase tracking-wider block">
          Key Verification Findings
        </span>
        <div className="grid gap-2">
          {findings.map((f, idx) => (
            <div
              key={idx}
              className={`p-2.5 rounded-md text-xs flex items-start gap-2.5 border ${
                f.type === "success"
                  ? "bg-green-50/60 border-green-200 text-green-900"
                  : f.type === "warning"
                  ? "bg-amber-50/60 border-amber-200 text-amber-900"
                  : "bg-red-50/60 border-red-200 text-red-900"
              }`}
            >
              {f.type === "success" && (
                <CheckCircle2 className="w-4 h-4 text-green-600 shrink-0 mt-0.5" />
              )}
              {f.type === "warning" && (
                <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
              )}
              {f.type === "danger" && (
                <XCircle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
              )}
              <span className="leading-relaxed font-medium">{f.text}</span>
            </div>
          ))}
          {!findings.length && <p className="text-xs text-on-surface-variant">No findings have been generated.</p>}
        </div>
      </div>

      {/* Algorithmic Reasoning */}
      <div className="bg-surface-container-low/70 border border-outline-variant/50 rounded-md p-3 mb-3">
        <span className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider block mb-1">
          Analysis & Evidence Summary
        </span>
        <p className="text-xs text-on-surface leading-relaxed">{reasoning}</p>
      </div>

      {/* Recommended Action */}
      <div className="bg-primary-fixed/30 border border-primary/20 rounded-md p-3">
        <div className="flex items-center gap-1.5 mb-1">
          <Info className="w-3.5 h-3.5 text-primary" />
          <span className="text-[11px] font-bold text-primary uppercase tracking-wider">
            Recommended Action
          </span>
        </div>
        <p className="text-xs text-on-surface font-medium leading-relaxed">
          {recommendation}
        </p>
      </div>
    </div>
  );
}
