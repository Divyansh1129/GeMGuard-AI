import React, { useState } from "react";
import { CheckCircle2, AlertCircle, XCircle, ShieldCheck, UserCheck } from "lucide-react";
import Button from "../common/Button";
import Modal from "../common/Modal";
import bidderStore from "../../services/bidderStore";

export default function OfficerDecision({
  currentStatus = "Review Required",
  onSubmitDecision,
}) {
  const [modalOpen, setModalOpen] = useState(false);
  const [decisionType, setDecisionType] = useState("Approve");
  const [remarks, setRemarks] = useState("");

  const handleOpenDecision = (type) => {
    setDecisionType(type);
    if (type === "Approve") {
      setRemarks("All documents verified satisfactory. Entity variations clarified with bidder record.");
    } else if (type === "Request Clarification") {
      setRemarks("Please provide an OEM authorization letter matching the bidder entity name.");
    } else {
      setRemarks("Multiple document entity discrepancies and non-compliance with tender eligibility criteria.");
    }
    setModalOpen(true);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!remarks.trim()) return;

    let targetStatus = "Verified";
    if (decisionType === "Request Clarification") {
      targetStatus = "Clarification Required";
      // Notify bidderStore about the clarification on OEM Authorization
      bidderStore.requestClarification("OEM", remarks);
    } else if (decisionType === "Mark Non-Compliant") {
      targetStatus = "Non-Compliant";
    }

    onSubmitDecision(targetStatus, decisionType, remarks);
    setModalOpen(false);
  };

  return (
    <div className="bg-surface-container-lowest border-2 border-primary/20 rounded-lg p-5 shadow-xs">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-outline-variant/40 mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-primary text-on-primary">
            <UserCheck className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-on-surface">
              Procurement Officer Decision
            </h3>
            <p className="text-xs text-on-surface-variant">
              AI recommendations are advisory. Final authority rests solely with the designated procurement officer.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-on-surface-variant">Current Status:</span>
          <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-surface-container text-on-surface border border-outline-variant">
            {currentStatus}
          </span>
        </div>
      </div>

      {/* Actions */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <Button
          variant="success"
          icon={CheckCircle2}
          onClick={() => handleOpenDecision("Approve")}
          className="w-full py-2.5"
        >
          Approve Bid
        </Button>

        <Button
          variant="secondary"
          icon={AlertCircle}
          onClick={() => handleOpenDecision("Request Clarification")}
          className="w-full py-2.5 border-amber-300 text-amber-900 hover:bg-amber-50"
        >
          Request Clarification
        </Button>

        <Button
          variant="danger"
          icon={XCircle}
          onClick={() => handleOpenDecision("Mark Non-Compliant")}
          className="w-full py-2.5"
        >
          Mark Non-Compliant
        </Button>
      </div>

      {/* Decision Modal */}
      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title={`Submit Officer Decision: ${decisionType}`}
        subtitle="This action will update the official bid status and create an immutable entry in the audit trail."
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-on-surface uppercase tracking-wider mb-1.5">
              Decision Category
            </label>
            <div className="p-2.5 rounded border border-outline-variant bg-surface-container-low text-xs font-semibold text-on-surface">
              {decisionType}
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-on-surface uppercase tracking-wider mb-1.5">
              Officer Remarks & Justification *
            </label>
            <textarea
              required
              rows={4}
              value={remarks}
              onChange={(e) => setRemarks(e.target.value)}
              placeholder="Enter official remarks..."
              className="w-full text-xs p-3 rounded border border-outline-variant bg-surface-container-lowest text-on-surface placeholder:text-outline focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary"
            />
          </div>

          <div className="bg-surface-container-low p-3 rounded border border-outline-variant/50 text-[11px] text-on-surface-variant flex items-start gap-2">
            <ShieldCheck className="w-4 h-4 text-primary shrink-0 mt-0.5" />
            <span>
              By submitting, your officer ID (88294-GOV) and timestamp will be logged for regulatory audit and transparency.
            </span>
          </div>

          <div className="flex items-center justify-end gap-2.5 pt-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setModalOpen(false)}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant={
                decisionType === "Approve"
                  ? "success"
                  : decisionType === "Mark Non-Compliant"
                  ? "danger"
                  : "primary"
              }
              size="sm"
            >
              Submit Official Decision
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
