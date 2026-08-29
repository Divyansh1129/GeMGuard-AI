import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  FileText,
  UploadCloud,
  CheckCircle2,
  Clock,
  AlertCircle,
  ArrowRight,
  Gavel,
  Building2,
  Calendar,
  ChevronRight,
  AlertTriangle,
} from "lucide-react";
import KPICard from "../../components/common/KPICard";
import StatusBadge from "../../components/common/StatusBadge";
import Button from "../../components/common/Button";
import bidderStore from "../../services/bidderStore";

export default function BidderDashboard() {
  const navigate = useNavigate();
  const [state, setState] = useState(bidderStore.getState());

  useEffect(() => {
    const unsubscribe = bidderStore.subscribe((newState) => {
      setState(newState);
    });
    return unsubscribe;
  }, []);

  // Compute document stats dynamically from store
  const totalRequired = state.documents.filter((d) => d.required).length;
  const uploadedCount = state.documents.filter((d) => d.uploaded).length;
  const verifiedCount = state.documents.filter(
    (d) => d.status === "Verified"
  ).length;
  const pendingCount = state.documents.filter(
    (d) => !d.uploaded || d.status === "Not Uploaded" || d.status === "Clarification Required"
  ).length;

  const clarificationDocs = state.documents.filter(
    (d) => d.status === "Clarification Required"
  );

  return (
    <div className="space-y-6">
      {/* Header Greeting */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline-variant/40 pb-4">
        <div>
          <div className="text-[10px] font-bold tracking-wider text-secondary uppercase">
            BIDDER PORTAL
          </div>
          <h1 className="text-2xl font-bold text-on-surface mt-0.5">
            Welcome, {state.bidderName}
          </h1>
          <p className="text-xs text-on-surface-variant mt-0.5">
            Track your compliance documents and submission progress for active GeM tenders.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="primary"
            size="sm"
            onClick={() => navigate("/bidder/documents")}
            icon={UploadCloud}
          >
            Upload Documents
          </Button>
        </div>
      </div>

      {/* Clarification Alert Banner (If Officer requested clarification) */}
      {clarificationDocs.length > 0 && (
        <div className="bg-amber-50 border-2 border-amber-300 rounded-xl p-5 shadow-xs space-y-3">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-lg bg-amber-500 text-white flex items-center justify-center shrink-0 mt-0.5">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-base font-bold text-amber-950">
                    Clarification Required on {clarificationDocs[0].name}
                  </h3>
                  <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-amber-200 text-amber-900">
                    Action Needed
                  </span>
                </div>
                <p className="text-xs text-amber-900 mt-1 font-medium">
                  <strong>Officer Request:</strong>{" "}
                  {clarificationDocs[0].clarificationMessage ||
                    "Please provide an OEM authorization letter matching the bidder entity name."}
                </p>
              </div>
            </div>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => navigate("/bidder/documents")}
              className="shrink-0 bg-amber-600 text-white hover:bg-amber-700 border-transparent font-bold"
            >
              Replace Document
            </Button>
          </div>
        </div>
      )}

      {/* Current Tender Info Banner */}
      <div className="bg-surface-container-lowest border border-outline-variant/60 rounded-xl p-6 shadow-xs relative overflow-hidden">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded text-[11px] font-mono bg-surface-container font-semibold text-on-surface">
                {state.tenderId}
              </span>
              <StatusBadge status={state.status} />
            </div>

            <h2 className="text-xl font-bold text-on-surface">
              {state.tenderName}
            </h2>

            <div className="flex flex-wrap items-center gap-4 text-xs text-on-surface-variant">
              <span className="flex items-center gap-1.5">
                <Building2 className="w-4 h-4 text-outline" />
                {state.department}
              </span>
              <span>•</span>
              <span className="flex items-center gap-1.5 font-mono">
                Bid ID: {state.bidId}
              </span>
              <span>•</span>
              <span className="flex items-center gap-1.5 font-semibold text-on-surface">
                <Calendar className="w-4 h-4 text-primary" />
                Deadline: {state.submissionDeadline}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate("/bidder/status")}
              icon={FileText}
            >
              View Submission Status
            </Button>
          </div>
        </div>
      </div>

      {/* Summary KPI Cards Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          label="Documents Required"
          value={totalRequired}
          subtitle="Mandatory GeM compliance files"
          icon={FileText}
          iconColor="text-primary"
        />
        <KPICard
          label="Documents Uploaded"
          value={uploadedCount}
          subtitle={`${Math.round((uploadedCount / 8) * 100)}% checklist completed`}
          icon={UploadCloud}
          iconColor="text-secondary"
          onClick={() => navigate("/bidder/documents")}
        />
        <KPICard
          label="Documents Verified"
          value={verifiedCount}
          subtitle="Automated checks passed"
          icon={CheckCircle2}
          iconColor="text-green-700"
        />
        <KPICard
          label="Pending / Action"
          value={pendingCount}
          subtitle={
            pendingCount > 0
              ? `${pendingCount} document${pendingCount > 1 ? "s" : ""} still needed`
              : "All documents submitted"
          }
          icon={Clock}
          iconColor={pendingCount > 0 ? "text-amber-600" : "text-green-700"}
          onClick={() => navigate("/bidder/documents")}
        />
      </div>

      {/* Quick Checklist Snapshot & Progress */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left: Document Submission Status (7 cols) */}
        <div className="lg:col-span-7 bg-surface-container-lowest border border-outline-variant/60 rounded-xl overflow-hidden shadow-xs">
          <div className="p-4 bg-surface-container-low border-b border-outline-variant/50 flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-on-surface">
                Compliance Document Checklist
              </h3>
              <p className="text-xs text-on-surface-variant">
                Upload required certificates for automated verification
              </p>
            </div>
            <button
              onClick={() => navigate("/bidder/documents")}
              className="text-xs font-bold text-primary hover:underline flex items-center gap-1"
            >
              <span>Manage All</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="divide-y divide-outline-variant/30">
            {state.documents.map((doc) => (
              <div
                key={doc.id}
                onClick={() => navigate("/bidder/documents")}
                className="p-3.5 hover:bg-surface-container-low/60 transition-colors flex items-center justify-between gap-3 cursor-pointer"
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                      doc.status === "Verified"
                        ? "bg-green-100 text-green-700"
                        : doc.status === "Clarification Required"
                        ? "bg-amber-100 text-amber-700"
                        : doc.uploaded
                        ? "bg-primary-fixed text-primary"
                        : "bg-surface-container text-outline"
                    }`}
                  >
                    <FileText className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-on-surface">
                        {doc.name}
                      </span>
                      {doc.required ? (
                        <span className="text-[10px] text-on-surface-variant font-medium">
                          (Required)
                        </span>
                      ) : (
                        <span className="text-[10px] text-secondary font-medium">
                          (Optional)
                        </span>
                      )}
                    </div>
                    <span className="text-[11px] text-on-surface-variant">
                      {doc.uploaded ? doc.fileName : "Not uploaded yet"}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <StatusBadge status={doc.status} size="sm" />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Submission Steps Guide (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          <div className="bg-surface-container-lowest border border-outline-variant/60 rounded-xl p-5 shadow-xs space-y-4">
            <h3 className="text-sm font-bold text-on-surface uppercase tracking-wide">
              Submission Progress
            </h3>

            {/* Progress Bar */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs font-semibold">
                <span className="text-on-surface">Documents Readiness</span>
                <span className="text-primary font-bold">
                  {uploadedCount} / {totalRequired} Uploaded
                </span>
              </div>
              <div className="w-full h-2.5 bg-surface-container rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary rounded-full transition-all duration-500"
                  style={{
                    width: `${Math.min(100, (uploadedCount / totalRequired) * 100)}%`,
                  }}
                />
              </div>
            </div>

            <div className="space-y-3 pt-2">
              <div className="flex items-start gap-3 text-xs">
                <div
                  className={`w-6 h-6 rounded-full flex items-center justify-center font-bold text-xs shrink-0 ${
                    uploadedCount >= totalRequired
                      ? "bg-green-600 text-white"
                      : "bg-primary text-white"
                  }`}
                >
                  1
                </div>
                <div>
                  <span className="font-bold text-on-surface block">
                    Upload Mandatory Files
                  </span>
                  <span className="text-on-surface-variant text-[11px]">
                    PAN, GST, Udyam, EPFO, ESIC, OEM Authorization
                  </span>
                </div>
              </div>

              <div className="flex items-start gap-3 text-xs">
                <div
                  className={`w-6 h-6 rounded-full flex items-center justify-center font-bold text-xs shrink-0 ${
                    state.status === "Submitted" || state.status === "Under Verification" || state.status === "Verified"
                      ? "bg-green-600 text-white"
                      : "bg-surface-container text-on-surface-variant"
                  }`}
                >
                  2
                </div>
                <div>
                  <span className="font-bold text-on-surface block">
                    Submit Bid Documents
                  </span>
                  <span className="text-on-surface-variant text-[11px]">
                    Lock submission for official compliance verification
                  </span>
                </div>
              </div>

              <div className="flex items-start gap-3 text-xs">
                <div
                  className={`w-6 h-6 rounded-full flex items-center justify-center font-bold text-xs shrink-0 ${
                    state.status === "Verified"
                      ? "bg-green-600 text-white"
                      : "bg-surface-container text-on-surface-variant"
                  }`}
                >
                  3
                </div>
                <div>
                  <span className="font-bold text-on-surface block">
                    Officer Review & Resolution
                  </span>
                  <span className="text-on-surface-variant text-[11px]">
                    Respond to any clarification requests if raised
                  </span>
                </div>
              </div>
            </div>

            <div className="pt-2">
              <Button
                variant="primary"
                className="w-full py-2.5 text-xs font-bold"
                onClick={() => navigate("/bidder/documents")}
                icon={ArrowRight}
              >
                Continue to Document Submission
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
