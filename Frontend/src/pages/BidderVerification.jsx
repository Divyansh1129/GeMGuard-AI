import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Shield,
  FileText,
  CheckCircle,
  AlertTriangle,
  ArrowLeft,
  Share2,
  Download,
  Building2,
  Mail,
  MapPin,
  Calendar,
} from "lucide-react";
import KPICard from "../components/common/KPICard";
import StatusBadge from "../components/common/StatusBadge";
import RiskBadge from "../components/common/RiskBadge";
import Button from "../components/common/Button";
import ComplianceScore from "../components/verification/ComplianceScore";
import CrossDocVerification from "../components/verification/CrossDocVerification";
import AIAssessment from "../components/verification/AIAssessment";
import IssueCard from "../components/verification/IssueCard";
import OfficerDecision from "../components/verification/OfficerDecision";
import AuditTrail from "../components/verification/AuditTrail";
import DocumentChecklist from "../components/verification/DocumentChecklist";
import { showToast } from "../components/common/Toast";

import bidderService from "../services/bidderService";
import documentService from "../services/documentService";
import api from "../services/api";

// NOTE: normaliseEntityName has been REMOVED. All name-consistency checks
// are now performed by the backend rule_engine and delivered via
// compliance.document_results[].field_checks.

export default function BidderVerification() {
  const { bidderId } = useParams();
  const navigate = useNavigate();
  const currentBidderId = bidderId;

  const [bidder, setBidder] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [issuesList, setIssuesList] = useState([]);
  const [auditList, setAuditList] = useState([]);
  const [compliance, setCompliance] = useState(null);

  useEffect(() => {
    async function load() {
      const b = await bidderService.getById(currentBidderId);
      const docs = await documentService.getByBidder(currentBidderId);
      let latest = null;
      try { latest = await bidderService.runComplianceCheck(currentBidderId); } catch (error) { console.error(error); }

      // Build issues from rule_engine_result — use applies_to from the rule
      // itself, never infer from key.split("_")[0].
      const iss = Object.entries(latest?.rule_engine_result || {})
        .filter(([, value]) => !value.pass)
        .map(([key, value]) => ({
          id: key,
          title: key.replaceAll("_", " "),
          description: value.detail,
          reviewed: false,
          severity: "warning",
          aiConfidence: Math.round((1 - (latest?.ml_risk_probability || 0)) * 100),
          // Use the rule's explicit applies_to list instead of string parsing
          affectedDocuments: value.applies_to || [],
          recommendedAction: "Review uploaded evidence",
        }));

      let aud = [];
      try {
        const { data } = await api.get(`/dashboard/${currentBidderId}/audit`);
        aud = data.map((log) => ({ ...log, action: log.details, type: log.actor === "procurement_officer" ? "officer" : "ai" }));
      } catch (error) { console.error(error); }

      setBidder(latest ? { ...b, complianceScore: latest.compliance_score, risk: latest.risk_level } : b);
      setDocuments(docs);
      setIssuesList(iss);
      setAuditList(aud);
      setCompliance(latest);
    }
    load();
  }, [currentBidderId]);

  if (!bidder) {
    return (
      <div className="text-center py-12">
        <h2 className="text-lg font-bold text-on-surface">Bidder Not Found</h2>
        <Button
          variant="outline"
          size="sm"
          onClick={() => navigate("/dashboard")}
          className="mt-4"
        >
          Return to Dashboard
        </Button>
      </div>
    );
  }

  const handleMarkReviewed = (issueId) => {
    setIssuesList((prev) =>
      prev.map((iss) =>
        iss.id === issueId ? { ...iss, reviewed: !iss.reviewed } : iss
      )
    );
    showToast("✓ Issue status updated", "success");
  };

  const handleOfficerDecision = async (newStatus, decisionType, remarks) => {
    await bidderService.updateStatus(bidder.id, newStatus, remarks);

    setBidder((prev) => ({
      ...prev,
      status: newStatus,
      officerRemarks: remarks,
    }));

    const { data } = await api.get(`/dashboard/${bidder.id}/audit`);
    setAuditList(data.map((log) => ({ ...log, action: log.details, type: log.actor === "procurement_officer" ? "officer" : "ai" })));

    showToast(`✓ Decision '${decisionType}' submitted successfully!`, "success");
  };

  return (
    <div className="space-y-6">
      {/* Top Breadcrumb & Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-outline-variant/40 pb-4">
        <div>
          <button
            onClick={() => navigate(-1)}
            className="inline-flex items-center gap-1 text-xs text-primary font-semibold hover:underline mb-1"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> Back
          </button>
          <div className="text-[10px] font-bold tracking-wider text-secondary uppercase">
            BID VERIFICATION WORKSPACE
          </div>
          <div className="flex items-center gap-3 mt-1">
            <h1 className="text-2xl font-bold text-on-surface">{bidder.name}</h1>
            <StatusBadge status={bidder.status} />
          </div>
          <div className="flex flex-wrap items-center gap-3 text-xs text-on-surface-variant mt-1.5">
            <span className="font-mono bg-surface-container px-2 py-0.5 rounded">
              Bid ID: {bidder.id}
            </span>
            <span>•</span>
            <span className="font-medium text-on-surface">{bidder.tenderName}</span>
            <span>•</span>
            <span>Reg Date: {bidder.registrationDate}</span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => showToast("Report downloaded successfully", "success")}
            icon={Download}
          >
            Export Dossier
          </Button>
        </div>
      </div>

      {/* Prominent KPI Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          label="Compliance Score"
          value={`${bidder.complianceScore}/100`}
          subtitle="Calculated from uploaded evidence"
          icon={Shield}
          iconColor="text-primary"
          progress={bidder.complianceScore}
        />
        <KPICard
          label="Verification Status"
          value={bidder.status}
          subtitle="Decision support; officer review required"
          icon={CheckCircle}
          iconColor="text-amber-600"
        />
        <KPICard
          label="Risk Assessment"
          value={bidder.risk}
          subtitle="Based on current evidence findings"
          icon={AlertTriangle}
          iconColor="text-amber-600"
        />
        <KPICard
          label="Submitted Documents"
          value={`${bidder.documentsSubmitted} / ${bidder.documentsTotal}`}
          subtitle="Current uploaded files"
          icon={FileText}
          iconColor="text-primary"
        />
      </div>

      {/* Main Two-Column Verification Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Documents & Cross-Check (7 Cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Document Checklist Table */}
          <DocumentChecklist documents={documents} bidderId={bidder.id} />

          {/* Cross Document Verification — uses backend document_results only */}
          <CrossDocVerification documentResults={compliance?.document_results || []} />

          {/* AI Compliance Assessment */}
          <AIAssessment confidence={compliance ? Math.round((1 - compliance.ml_risk_probability) * 100) : 0} status={bidder.status.toUpperCase()} findings={issuesList.map((issue) => ({ type: "warning", text: issue.description }))} reasoning={compliance?.ai_recommendation || "Run a compliance check after documents are uploaded."} recommendation={compliance?.ai_recommendation || "No assessment is available yet."} />

          {/* Compliance Score Breakdown */}
          <ComplianceScore score={bidder.complianceScore} />
        </div>

        {/* Right Column: Issues Requiring Attention & Officer Decision (5 Cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Officer Decision Section (Prominent) */}
          <OfficerDecision
            currentStatus={bidder.status}
            onSubmitDecision={handleOfficerDecision}
          />

          {/* Issues Requiring Attention */}
          <div className="bg-surface-container-lowest border border-outline-variant/60 rounded-lg p-5 space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-outline-variant/40">
              <div>
                <h3 className="text-sm font-bold text-on-surface uppercase tracking-wide">
                  Issues Requiring Attention
                </h3>
                <p className="text-xs text-on-surface-variant">
                  Items flagged by AI Rule Engine for human officer confirmation
                </p>
              </div>
              <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-amber-50 text-amber-800 border border-amber-200">
                {issuesList.length} Flagged
              </span>
            </div>

            <div className="space-y-3">
              {issuesList.map((issue) => (
                <IssueCard
                  key={issue.id}
                  issue={issue}
                  onMarkReviewed={handleMarkReviewed}
                />
              ))}
            </div>
          </div>

          {/* Audit Trail Timeline */}
          <AuditTrail logs={auditList} />
        </div>
      </div>
    </div>
  );
}
