import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  FileCheck2,
  CheckCircle2,
  Clock,
  AlertCircle,
  UploadCloud,
  Send,
  Calendar,
  Building2,
  ArrowRight,
  ShieldCheck,
} from "lucide-react";
import StatusBadge from "../../components/common/StatusBadge";
import Button from "../../components/common/Button";
import bidderStore from "../../services/bidderStore";

export default function BidderStatus() {
  const navigate = useNavigate();
  const [state, setState] = useState(bidderStore.getState());

  useEffect(() => {
    const unsubscribe = bidderStore.subscribe((newState) => {
      setState(newState);
    });
    return unsubscribe;
  }, []);

  const totalRequired = state.documents.filter((d) => d.required).length;
  const uploadedCount = state.documents.filter((d) => d.uploaded).length;
  const verifiedCount = state.documents.filter(
    (d) => d.status === "Verified"
  ).length;

  const steps = [
    {
      id: 1,
      title: "Document Preparation",
      desc: "Gather statutory, tax and OEM certificates",
      completed: uploadedCount >= 6,
      current: state.status === "Incomplete" || state.status === "Draft",
    },
    {
      id: 2,
      title: "Bid Submission",
      desc: "Formal submission to GeM procurement officer",
      completed:
        state.status === "Submitted" ||
        state.status === "Under Verification" ||
        state.status === "Clarification Required" ||
        state.status === "Verified",
      current: state.status === "Ready for Submission",
    },
    {
      id: 3,
      title: "Automated Rule & OCR Verification",
      desc: "Automated entity check and cross-registry validation",
      completed: state.status === "Verified" || state.status === "Clarification Required" || state.status === "Under Verification",
      current: state.status === "Under Verification",
    },
    {
      id: 4,
      title: "Officer Compliance Decision",
      desc: "Final verification decision by Ministry Officer",
      completed: state.status === "Verified",
      current: state.status === "Clarification Required",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline-variant/40 pb-4">
        <div>
          <div className="text-[10px] font-bold tracking-wider text-secondary uppercase">
            BID TRACKING
          </div>
          <h1 className="text-2xl font-bold text-on-surface mt-0.5">
            Submission Status
          </h1>
          <p className="text-xs text-on-surface-variant mt-0.5">
            Real-time status tracking for bid submission and GeM officer compliance verification.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate("/bidder/documents")}
            icon={UploadCloud}
          >
            Manage Documents
          </Button>
        </div>
      </div>

      {/* Main Status Hero Card */}
      <div className="bg-surface-container-lowest border border-outline-variant/60 rounded-xl p-6 shadow-xs space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-outline-variant/40">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-mono font-bold text-on-surface-variant bg-surface-container px-2 py-0.5 rounded">
                Bid ID: {state.bidId}
              </span>
              <span className="text-xs text-on-surface-variant">•</span>
              <span className="text-xs font-semibold text-on-surface">
                {state.tenderName}
              </span>
            </div>
            <h2 className="text-xl font-bold text-on-surface">
              Overall Status: <span className="text-primary">{state.status}</span>
            </h2>
          </div>

          <StatusBadge status={state.status} size="lg" />
        </div>

        {/* Progress Timeline Steps */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {steps.map((step) => (
            <div
              key={step.id}
              className={`p-4 rounded-xl border transition-all ${
                step.completed
                  ? "bg-green-50/50 border-green-200 text-green-950"
                  : step.current
                  ? "bg-primary-fixed/30 border-primary/40 text-on-surface"
                  : "bg-surface-container-low border-outline-variant/40 text-on-surface-variant opacity-70"
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-[11px] font-bold uppercase tracking-wider">
                  Step {step.id}
                </span>
                {step.completed ? (
                  <CheckCircle2 className="w-4 h-4 text-green-600" />
                ) : step.current ? (
                  <div className="w-2.5 h-2.5 rounded-full bg-primary animate-ping" />
                ) : (
                  <Clock className="w-4 h-4 text-outline" />
                )}
              </div>
              <h4 className="text-xs font-bold mb-1">{step.title}</h4>
              <p className="text-[11px] leading-relaxed">{step.desc}</p>
            </div>
          ))}
        </div>

        {/* Progress Breakdown Bar */}
        <div className="bg-surface-container-low p-4 rounded-lg border border-outline-variant/40 space-y-2">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between text-xs gap-1">
            <span className="font-semibold text-on-surface">
              Document Completion: {uploadedCount} / {totalRequired} documents uploaded ({verifiedCount} verified)
            </span>
            <span className="font-mono font-bold text-primary">
              {Math.round((uploadedCount / totalRequired) * 100)}% Complete
            </span>
          </div>
          <div className="w-full h-2 bg-surface-container rounded-full overflow-hidden">
            <div
              className="h-full bg-primary rounded-full transition-all duration-500"
              style={{
                width: `${(uploadedCount / totalRequired) * 100}%`,
              }}
            />
          </div>
        </div>
      </div>

      {/* Document Status Breakdown List */}
      <div className="bg-surface-container-lowest border border-outline-variant/60 rounded-xl overflow-hidden shadow-xs">
        <div className="p-4 bg-surface-container-low border-b border-outline-variant/50 flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-on-surface">
              Document Compliance Audit Snapshot
            </h3>
            <p className="text-xs text-on-surface-variant">
              Individual status of compliance documents submitted for verification
            </p>
          </div>
          <span className="text-xs font-bold text-primary">
            {uploadedCount} of 8 Uploaded
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-outline-variant/30">
          {/* Column 1 */}
          <div className="divide-y divide-outline-variant/30">
            {state.documents.slice(0, 4).map((doc) => (
              <div key={doc.id} className="p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div
                    className={`w-6 h-6 rounded-full flex items-center justify-center text-xs shrink-0 ${
                      doc.uploaded
                        ? "bg-green-100 text-green-700 font-bold"
                        : "bg-surface-container text-outline"
                    }`}
                  >
                    {doc.uploaded ? "✓" : "○"}
                  </div>
                  <div>
                    <span className="text-xs font-bold text-on-surface block">
                      {doc.name}
                    </span>
                    <span className="text-[11px] text-on-surface-variant">
                      {doc.uploaded ? doc.fileName : "Not uploaded"}
                    </span>
                  </div>
                </div>
                <StatusBadge status={doc.status} size="sm" />
              </div>
            ))}
          </div>

          {/* Column 2 */}
          <div className="divide-y divide-outline-variant/30">
            {state.documents.slice(4, 8).map((doc) => (
              <div key={doc.id} className="p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div
                    className={`w-6 h-6 rounded-full flex items-center justify-center text-xs shrink-0 ${
                      doc.uploaded
                        ? "bg-green-100 text-green-700 font-bold"
                        : "bg-surface-container text-outline"
                    }`}
                  >
                    {doc.uploaded ? "✓" : "○"}
                  </div>
                  <div>
                    <span className="text-xs font-bold text-on-surface block">
                      {doc.name}
                    </span>
                    <span className="text-[11px] text-on-surface-variant">
                      {doc.uploaded ? doc.fileName : "Not uploaded"}
                    </span>
                  </div>
                </div>
                <StatusBadge status={doc.status} size="sm" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
