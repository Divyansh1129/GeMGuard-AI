import React from "react";
import { CheckCircle2, AlertTriangle, ArrowRightLeft } from "lucide-react";

export default function CrossDocVerification({
  entityComparisons = [],
}) {
  const mismatchCount = entityComparisons.filter((item) => item.status === "mismatch").length;
  return (
    <div className="bg-surface-container-lowest border border-outline-variant/60 rounded-lg p-5">
      <div className="flex items-center gap-2 mb-1">
        <ArrowRightLeft className="w-4 h-4 text-primary" />
        <h3 className="text-base font-bold text-on-surface">
          Cross-Document Verification
        </h3>
      </div>
      <p className="text-xs text-on-surface-variant mb-4">
        Checking whether entity identity and key attributes are consistent across submitted documents.
      </p>

      {/* Entity Name Cross-Check Card */}
      <div className="rounded-lg border border-outline-variant/60 bg-surface-container-low/40 p-4 space-y-3">
        <div className="flex items-center justify-between pb-2 border-b border-outline-variant/40">
          <span className="text-xs font-bold text-on-surface uppercase tracking-wider">
            Attribute: Legal Entity Name
          </span>
          <span className={`inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-full border ${mismatchCount ? "bg-amber-50 text-amber-800 border-amber-200" : "bg-green-50 text-green-800 border-green-200"}`}>
            <AlertTriangle className="w-3 h-3" />
            {mismatchCount ? `${mismatchCount} Variation${mismatchCount === 1 ? "" : "s"} Detected` : "No variations detected"}
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
          {entityComparisons.length ? entityComparisons.map((item, idx) => {
            const isMismatch = item.status === "mismatch";
            return (
              <div
                key={idx}
                className={`p-3 rounded border text-xs flex flex-col justify-between min-w-0 ${
                  isMismatch
                    ? "bg-amber-50/70 border-amber-300"
                    : "bg-surface-container-lowest border-outline-variant/40"
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-bold text-on-surface-variant uppercase break-words">
                    {item.doc}
                  </span>
                  {isMismatch ? (
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                  ) : (
                    <CheckCircle2 className="w-3.5 h-3.5 text-green-600" />
                  )}
                </div>
                <div
                  className={`font-medium break-words ${
                    isMismatch ? "text-amber-900 font-semibold" : "text-on-surface"
                  }`}
                >
                  {item.name}
                </div>
                <div className="text-[10px] mt-1 text-on-surface-variant">
                  {isMismatch ? "⚠ Potential Mismatch" : "✓ Strong Match"}
                </div>
              </div>
            );
          }) : <p className="text-xs text-on-surface-variant">No uploaded document contains an extracted legal name yet.</p>}
        </div>
      </div>
    </div>
  );
}
