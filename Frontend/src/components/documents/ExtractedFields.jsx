import React, { useState } from "react";
import { Edit2, Check, X, Sparkles, CheckCircle2, AlertTriangle, ShieldCheck } from "lucide-react";
import Button from "../common/Button";
import { showToast } from "../common/Toast";

function FieldCheckBadge({ status }) {
  if (status === "pass") return <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-green-50 text-green-700 border border-green-200">PASS</span>;
  if (status === "fail") return <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-red-50 text-red-700 border border-red-200">FAIL</span>;
  return <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-200">REVIEW</span>;
}

export default function ExtractedFields({
  document: doc,
  onSaveField,
}) {
  const [editingKey, setEditingKey] = useState(null);
  const [editValue, setEditValue] = useState("");

  const handleStartEdit = (key, val) => {
    setEditingKey(key);
    setEditValue(val);
  };

  const handleSave = (key) => {
    if (onSaveField) {
      onSaveField(key, editValue);
    }
    setEditingKey(null);
    showToast(`✓ Field '${key}' updated successfully`, "success");
  };

  const handleCancel = () => {
    setEditingKey(null);
    setEditValue("");
  };

  const fieldChecks = doc?.fieldChecks || [];

  return (
    <div className="bg-surface-container-lowest border border-outline-variant/60 rounded-lg p-5 flex flex-col h-full">
      <div className="flex items-center justify-between pb-3 border-b border-outline-variant/40 mb-4">
        <div>
          <h3 className="text-base font-bold text-on-surface">
            Extracted Fields & OCR
          </h3>
          <p className="text-xs text-on-surface-variant">
            Data automatically parsed via OCR. Click edit icon to make corrections.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold px-2 py-0.5 rounded bg-green-50 text-green-700 border border-green-200">
            {doc?.ocrConfidence ?? "—"}% Extraction Confidence
          </span>
        </div>
      </div>

      {/* Fields List */}
      <div className="space-y-3 flex-1 overflow-y-auto pr-1">
        {doc?.extractedFields &&
          Object.entries(doc.extractedFields).map(([key, value]) => {
            const isEditing = editingKey === key;
            return (
              <div
                key={key}
                className={`p-3 rounded-lg border transition-all ${
                  isEditing
                    ? "border-primary bg-primary-fixed/10"
                    : "border-outline-variant/40 bg-surface-container-low/40 hover:bg-surface-container-low"
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <label className="text-[11px] font-bold text-on-surface-variant uppercase tracking-wider">
                    {key}
                  </label>
                  {!isEditing && (
                    <button
                      onClick={() => handleStartEdit(key, value)}
                      className="p-1 rounded hover:bg-surface-container text-primary transition-colors"
                      title="Edit field value"
                    >
                      <Edit2 className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>

                {isEditing ? (
                  <div className="flex items-center gap-2 mt-1.5">
                    <input
                      type="text"
                      value={editValue}
                      onChange={(e) => setEditValue(e.target.value)}
                      autoFocus
                      className="flex-1 text-xs px-2.5 py-1.5 rounded border border-primary bg-surface-container-lowest text-on-surface focus:outline-none"
                    />
                    <button
                      onClick={() => handleSave(key)}
                      className="p-1.5 rounded bg-primary text-on-primary hover:bg-primary-container"
                      title="Save"
                    >
                      <Check className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={handleCancel}
                      className="p-1.5 rounded bg-surface-container text-on-surface hover:bg-surface-container-high"
                      title="Cancel"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ) : (
                  <div className="text-xs font-semibold text-on-surface font-mono break-words">
                    {typeof value === "object" ? JSON.stringify(value) : String(value ?? "")}
                  </div>
                )}
              </div>
            );
          })}
      </div>

      {/* Backend Field Checks — compliance checks per field */}
      {fieldChecks.length > 0 && (
        <div className="mt-5 pt-4 border-t border-outline-variant/40">
          <h4 className="text-xs font-bold text-on-surface uppercase tracking-wider mb-3 flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-primary" />
            Compliance Field Checks
          </h4>
          <div className="space-y-2">
            {fieldChecks.map((check, idx) => (
              <div
                key={`${check.rule_key}-${idx}`}
                className={`p-3 rounded-lg border text-xs ${
                  check.status === "pass"
                    ? "bg-green-50/50 border-green-200"
                    : check.status === "fail"
                    ? "bg-red-50/50 border-red-200"
                    : "bg-amber-50/50 border-amber-200"
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-bold text-on-surface uppercase tracking-wider text-[11px]">
                    {check.field_name}
                  </span>
                  <FieldCheckBadge status={check.status} />
                </div>
                <p className="text-on-surface-variant leading-relaxed">{check.reason}</p>
                {check.compared_against && (
                  <p className="text-[10px] text-on-surface-variant mt-1">
                    Compared against: <strong>{check.compared_against}</strong>
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Verification Result Section — separate labels for extraction vs compliance */}
      <div className="mt-5 pt-4 border-t border-outline-variant/40">
        <h4 className="text-xs font-bold text-on-surface uppercase tracking-wider mb-2 flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5 text-primary" />
          Verification Result
        </h4>

        <div
          className={`p-3 rounded-lg border text-xs ${
            doc?.verificationResult?.valid
              ? "bg-green-50/70 border-green-200 text-green-950"
              : "bg-amber-50/70 border-amber-200 text-amber-950"
          }`}
        >
          <div className="flex items-center gap-1.5 font-bold mb-1">
            {doc?.verificationResult?.valid ? (
              <>
                <CheckCircle2 className="w-4 h-4 text-green-600" />
                <span>✓ Valid & Active</span>
              </>
            ) : (
              <>
                <AlertTriangle className="w-4 h-4 text-amber-600" />
                <span>⚠ Verification Finding</span>
              </>
            )}
          </div>
          <p className="leading-relaxed text-xs">
            {doc?.verificationResult?.message}
          </p>

          {/* Two SEPARATE, EXPLICIT labels — never conflated */}
          <div className="flex items-center gap-4 mt-2.5 pt-2 border-t border-black/5 text-[11px] text-on-surface-variant font-medium">
            <span>Extraction Confidence: <strong>{doc?.ocrConfidence ?? "—"}%</strong></span>
            <span>Compliance Score: <strong>{doc?.overallScore ?? "—"}/100</strong></span>
          </div>
        </div>
      </div>
    </div>
  );
}
