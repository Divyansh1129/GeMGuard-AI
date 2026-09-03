import React from "react";
import { useNavigate } from "react-router-dom";
import { FileText, CheckCircle, AlertTriangle, Eye, ShieldCheck } from "lucide-react";
import StatusBadge from "../common/StatusBadge";
import Button from "../common/Button";

function complianceBadge(overallStatus, overallScore) {
  if (overallStatus === "pass") {
    return (
      <span className="inline-flex items-center gap-1 text-xs font-bold px-2 py-0.5 rounded-full bg-green-50 text-green-700 border border-green-200">
        <CheckCircle className="w-3 h-3" /> {overallScore ?? "—"}
      </span>
    );
  }
  if (overallStatus === "fail") {
    return (
      <span className="inline-flex items-center gap-1 text-xs font-bold px-2 py-0.5 rounded-full bg-red-50 text-red-700 border border-red-200">
        <AlertTriangle className="w-3 h-3" /> {overallScore ?? "—"}
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 text-xs font-bold px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 border border-amber-200">
      <AlertTriangle className="w-3 h-3" /> {overallScore ?? "—"}
    </span>
  );
}

export default function DocumentChecklist({ documents = [], bidderId }) {
  const navigate = useNavigate();

  return (
    <div className="bg-surface-container-lowest border border-outline-variant/60 rounded-lg overflow-hidden flex flex-col">
      <div className="bg-surface-container-low px-5 py-3.5 border-b border-outline-variant/50 flex items-center justify-between">
        <div>
          <h3 className="text-base font-bold text-on-surface">
            Document Checklist & Verification
          </h3>
          <p className="text-xs text-on-surface-variant">
            Cross-indexed against Central Indian procurement registries
          </p>
        </div>
        <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-primary-container text-on-primary-container">
          {documents.length} Mandatory Files
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead className="bg-[#F1F5F9] text-xs font-semibold text-on-surface-variant uppercase tracking-wider border-b border-outline-variant/50">
            <tr>
              <th className="px-5 py-3">Document Type</th>
              <th className="px-5 py-3">Verification Status</th>
              <th className="px-5 py-3">OCR / System Findings</th>
              <th className="px-5 py-3">Compliance Score</th>
              <th className="px-5 py-3">Extraction Confidence</th>
              <th className="px-5 py-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="text-xs divide-y divide-outline-variant/30 bg-surface-container-lowest">
            {documents.map((doc) => {
              const isReview = doc.status === "Review Required";
              return (
                <tr
                  key={doc.id}
                  onClick={() => navigate(`/bids/${bidderId}/documents/${doc.id}`)}
                  className={`hover:bg-surface-container-low transition-colors group cursor-pointer ${
                    isReview ? "bg-amber-50/20" : ""
                  }`}
                >
                  <td className="px-5 py-3.5">
                    <div className="flex items-center gap-2.5">
                      <div
                        className={`w-7 h-7 rounded flex items-center justify-center ${
                          isReview
                            ? "bg-amber-100 text-amber-700"
                            : "bg-surface-container text-on-surface-variant"
                        }`}
                      >
                        <FileText className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="font-semibold text-on-surface">
                          {doc.name}
                        </div>
                        <div className="text-[11px] text-on-surface-variant font-mono">
                          {doc.type}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-5 py-3.5">
                    <StatusBadge status={doc.status} size="sm" />
                  </td>
                  <td className="px-5 py-3.5 text-on-surface-variant font-medium max-w-[220px]">
                    {doc.finding}
                  </td>
                  {/* Compliance Score — derived from backend field_checks */}
                  <td className="px-5 py-3.5">
                    {complianceBadge(doc.overallStatus, doc.overallScore)}
                  </td>
                  {/* Extraction Confidence — OCR quality, NOT compliance */}
                  <td className="px-5 py-3.5">
                    <span className="font-bold text-on-surface">
                      {doc.ocrConfidence != null ? `${doc.ocrConfidence}%` : "—"}
                    </span>
                    <span className="text-[10px] text-on-surface-variant ml-1">OCR</span>
                  </td>
                  <td className="px-5 py-3.5 text-right">
                    <Button
                      variant={isReview ? "primary" : "ghost"}
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/bids/${bidderId}/documents/${doc.id}`);
                      }}
                    >
                      {isReview ? "Resolve" : "View File"}
                    </Button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
