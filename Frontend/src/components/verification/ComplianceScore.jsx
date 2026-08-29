import React from "react";

export default function ComplianceScore({
  score = 94,
  breakdown = [
    { label: "Document Completeness", value: 100 },
    { label: "Document Validity", value: 98 },
    { label: "Entity Consistency", value: 94 },
    { label: "OEM Verification", value: 100 },
    { label: "Blacklisting Check", value: 100 },
  ],
}) {
  return (
    <div className="bg-surface-container-lowest border border-outline-variant/60 rounded-lg p-5">
      <div className="flex items-center justify-between mb-4 border-b border-outline-variant/40 pb-3">
        <div>
          <h3 className="text-sm font-bold text-on-surface uppercase tracking-wide">
            Compliance Score Breakdown
          </h3>
          <p className="text-xs text-on-surface-variant">
            Weighted algorithmic assessment of submitted compliance documents
          </p>
        </div>
        <div className="text-right">
          <span className="text-2xl font-bold text-primary">{score}</span>
          <span className="text-xs text-on-surface-variant font-medium">/100</span>
        </div>
      </div>

      <div className="space-y-3.5">
        {breakdown.map((item, idx) => (
          <div key={idx} className="space-y-1.5">
            <div className="flex justify-between items-center text-xs">
              <span className="font-medium text-on-surface">{item.label}</span>
              <span className="font-bold text-on-surface">{item.value}%</span>
            </div>
            <div className="w-full bg-surface-container rounded-full h-2 overflow-hidden">
              <div
                className={`h-2 rounded-full transition-all duration-500 ${
                  item.value >= 95
                    ? "bg-green-600"
                    : item.value >= 85
                    ? "bg-primary"
                    : item.value >= 70
                    ? "bg-amber-500"
                    : "bg-red-600"
                }`}
                style={{ width: `${item.value}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
