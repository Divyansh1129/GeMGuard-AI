import React, { useState, useEffect } from "react";
import {
  UploadCloud,
  FileText,
  CheckCircle2,
  AlertCircle,
  Clock,
  Eye,
  RefreshCw,
  Plus,
  Loader2,
  Check,
  AlertTriangle,
  Send,
  HelpCircle,
} from "lucide-react";
import Button from "../../components/common/Button";
import StatusBadge from "../../components/common/StatusBadge";
import Modal from "../../components/common/Modal";
import DocumentPreviewModal from "../../components/bidder/DocumentPreviewModal";
import { showToast } from "../../components/common/Toast";
import bidderStore from "../../services/bidderStore";

export default function BidderDocuments() {
  const [state, setState] = useState(bidderStore.getState());
  const [selectedDocType, setSelectedDocType] = useState("OEM");
  const [previewDoc, setPreviewDoc] = useState(null);
  const [submitModalOpen, setSubmitModalOpen] = useState(false);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [isReplacingClarification, setIsReplacingClarification] = useState(false);

  // Upload simulation state
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStep, setUploadStep] = useState(0);
  const [activeFileName, setActiveFileName] = useState("");

  const pipelineSteps = [
    "Uploading encrypted file...",
    "Document classification & validation",
    "OCR text & entity extraction",
    "Pre-submission compliance check",
    "Ready for verification",
  ];

  useEffect(() => {
    const unsubscribe = bidderStore.subscribe((newState) => {
      setState(newState);
    });
    return unsubscribe;
  }, []);

  const totalRequired = state.documents.filter((d) => d.required).length;
  const uploadedCount = state.documents.filter((d) => d.uploaded).length;
  const uploadedRequiredCount = state.documents.filter(
    (d) => d.required && d.uploaded
  ).length;
  const isReadyForSubmission =
    uploadedRequiredCount === totalRequired &&
    (state.status === "Draft" || state.status === "Incomplete" || state.status === "Ready for Submission");

  const isAlreadySubmitted =
    state.status === "Submitted" ||
    state.status === "Under Verification" ||
    state.status === "Verified";

  const handleStartUpload = (docType, isClarification = false) => {
    setSelectedDocType(docType);
    setIsReplacingClarification(isClarification);
    setUploadModalOpen(true);
  };

  const handleFileDrop = async (e) => {
    const files = e.target.files || e.dataTransfer.files;
    if (!files || files.length === 0) return;
    const file = files[0];

    // File validation (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      showToast("File size exceeds 10 MB maximum limit", "error");
      return;
    }

    setActiveFileName(file.name);
    setIsUploading(true);
    setUploadStep(0);

    for (let i = 0; i < pipelineSteps.length; i++) {
      setUploadStep(i);
      await new Promise((res) => setTimeout(res, 600));
    }

    // Save to shared store
    bidderStore.uploadDocument(selectedDocType, file, isReplacingClarification);

    setIsUploading(false);
    setUploadModalOpen(false);

    if (isReplacingClarification) {
      showToast(
        `✓ Corrected ${selectedDocType} document submitted to Officer for review!`,
        "success"
      );
    } else {
      showToast(
        `✓ ${selectedDocType} document uploaded & processed successfully!`,
        "success"
      );
    }
  };

  const handleFinalSubmit = () => {
    bidderStore.submitBid();
    setSubmitModalOpen(false);
    showToast(
      "✓ Bid compliance documents submitted successfully! Status updated to 'Under Verification'.",
      "success"
    );
  };

  return (
    <div className="space-y-6">
      {/* Page Title & Subtitle */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline-variant/40 pb-4">
        <div>
          <div className="text-[10px] font-bold tracking-wider text-secondary uppercase">
            DOCUMENT SUBMISSION
          </div>
          <h1 className="text-2xl font-bold text-on-surface mt-0.5">
            Submit Compliance Documents
          </h1>
          <p className="text-xs text-on-surface-variant mt-0.5">
            Upload the required documents for your bid. Each document will be checked for completeness and compliance.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-xs font-semibold text-on-surface-variant">
            Status:
          </span>
          <StatusBadge status={state.status} />
        </div>
      </div>

      {/* Clarification Action Banner if needed */}
      {state.documents.some((d) => d.status === "Clarification Required") && (
        <div className="bg-amber-50 border-2 border-amber-300 rounded-xl p-5 shadow-xs space-y-3">
          <div className="flex items-start gap-3">
            <div className="w-9 h-9 rounded-lg bg-amber-500 text-white flex items-center justify-center shrink-0 mt-0.5">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div className="space-y-1 flex-1">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-bold text-amber-950">
                  Clarification Requested by Procurement Officer
                </h4>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-200 text-amber-900">
                  Action Required
                </span>
              </div>
              <p className="text-xs text-amber-800">
                <strong>Officer Note:</strong> "Please provide an OEM authorization letter matching the bidder entity name."
              </p>
              <div className="pt-2">
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => handleStartUpload("OEM", true)}
                  icon={RefreshCw}
                  className="bg-amber-700 hover:bg-amber-800 text-white border-transparent"
                >
                  Upload Corrected OEM Letter
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Progress & Quick Stats Card */}
      <div className="bg-surface-container-lowest border border-outline-variant/60 rounded-xl p-5 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1.5 flex-1 max-w-md">
          <div className="flex justify-between text-xs font-bold">
            <span className="text-on-surface">Mandatory Compliance Progress</span>
            <span className="text-primary font-mono">
              {uploadedRequiredCount} / {totalRequired} Files Ready
            </span>
          </div>
          <div className="w-full h-2.5 bg-surface-container rounded-full overflow-hidden">
            <div
              className="h-full bg-primary rounded-full transition-all duration-500"
              style={{
                width: `${(uploadedRequiredCount / totalRequired) * 100}%`,
              }}
            />
          </div>
        </div>

        <div className="flex items-center gap-3">
          {isReadyForSubmission && (
            <Button
              variant="primary"
              size="sm"
              icon={Send}
              onClick={() => setSubmitModalOpen(true)}
              className="bg-green-700 hover:bg-green-800"
            >
              Submit Bid Documents
            </Button>
          )}

          {isAlreadySubmitted && (
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-green-50 text-green-800 border border-green-200 text-xs font-bold">
              <CheckCircle2 className="w-4 h-4 text-green-600" />
              <span>Bid Documents Submitted</span>
            </div>
          )}

          <Button
            variant="outline"
            size="sm"
            icon={UploadCloud}
            onClick={() => handleStartUpload("OEM", false)}
          >
            Upload File
          </Button>
        </div>
      </div>

      {/* Document Checklist Cards / Table */}
      <div className="bg-surface-container-lowest border border-outline-variant/60 rounded-xl overflow-hidden shadow-xs">
        <div className="p-4 bg-surface-container-low border-b border-outline-variant/50 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h3 className="text-base font-bold text-on-surface">
              Required Compliance Documents (8)
            </h3>
            <p className="text-xs text-on-surface-variant">
              All documents are processed using OCR extraction and checked against statutory guidelines.
            </p>
          </div>
          <span className="text-xs font-mono px-2.5 py-1 rounded bg-surface-container text-on-surface-variant">
            Max file size: 10 MB (PDF, JPG, PNG)
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead className="bg-[#F1F5F9] text-xs font-semibold text-on-surface-variant uppercase tracking-wider border-b border-outline-variant/50">
              <tr>
                <th className="px-5 py-3">Document Name</th>
                <th className="px-5 py-3">Requirement</th>
                <th className="px-5 py-3">Upload Status</th>
                <th className="px-5 py-3">Verification Status</th>
                <th className="px-5 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="text-xs divide-y divide-outline-variant/30 bg-surface-container-lowest">
              {state.documents.map((doc) => {
                const isClarification = doc.status === "Clarification Required";
                return (
                  <tr
                    key={doc.id}
                    className={`hover:bg-surface-container-low/50 transition-colors ${
                      isClarification ? "bg-amber-50/40" : ""
                    }`}
                  >
                    {/* Document Info */}
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-3">
                        <div
                          className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                            doc.status === "Verified"
                              ? "bg-green-100 text-green-700"
                              : isClarification
                              ? "bg-amber-100 text-amber-700"
                              : doc.uploaded
                              ? "bg-primary-fixed text-primary"
                              : "bg-surface-container text-outline"
                          }`}
                        >
                          <FileText className="w-4 h-4" />
                        </div>
                        <div>
                          <div className="font-bold text-on-surface flex items-center gap-2">
                            <span>{doc.name}</span>
                          </div>
                          <div className="text-[11px] text-on-surface-variant">
                            {doc.uploaded ? (
                              <span className="font-mono">{doc.fileName} ({doc.fileSize})</span>
                            ) : (
                              <span className="text-outline">File not attached</span>
                            )}
                          </div>
                        </div>
                      </div>
                    </td>

                    {/* Requirement */}
                    <td className="px-5 py-4">
                      {doc.required ? (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold bg-primary-fixed/50 text-on-primary-fixed">
                          Required
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-surface-container text-on-surface-variant">
                          Optional
                        </span>
                      )}
                    </td>

                    {/* Upload Status */}
                    <td className="px-5 py-4">
                      {doc.uploaded ? (
                        <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-green-700">
                          <CheckCircle2 className="w-4 h-4" />
                          <span>Uploaded</span>
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 text-xs text-outline">
                          <Clock className="w-4 h-4" />
                          <span>Not Uploaded</span>
                        </span>
                      )}
                    </td>

                    {/* Verification Status */}
                    <td className="px-5 py-4">
                      <StatusBadge status={doc.status} size="sm" />
                      {doc.clarificationMessage && (
                        <div className="text-[10px] text-amber-800 font-medium mt-1 max-w-[200px] truncate" title={doc.clarificationMessage}>
                          Note: {doc.clarificationMessage}
                        </div>
                      )}
                    </td>

                    {/* Actions */}
                    <td className="px-5 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        {doc.uploaded ? (
                          <>
                            <Button
                              variant="ghost"
                              size="sm"
                              icon={Eye}
                              onClick={() => setPreviewDoc(doc)}
                            >
                              View
                            </Button>
                            <Button
                              variant={isClarification ? "secondary" : "outline"}
                              size="sm"
                              icon={RefreshCw}
                              onClick={() =>
                                handleStartUpload(doc.type, isClarification)
                              }
                              className={
                                isClarification
                                  ? "border-amber-300 text-amber-900 bg-amber-50"
                                  : ""
                              }
                            >
                              {isClarification ? "Replace (Clarify)" : "Replace"}
                            </Button>
                          </>
                        ) : (
                          <Button
                            variant="primary"
                            size="sm"
                            icon={UploadCloud}
                            onClick={() => handleStartUpload(doc.type, false)}
                          >
                            Upload
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Ready for Final Submission Alert Card */}
      {isReadyForSubmission && (
        <div className="bg-green-50 border-2 border-green-300 rounded-xl p-6 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-full bg-green-600 text-white flex items-center justify-center shrink-0">
              <Check className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-base font-bold text-green-950">
                Ready for Final Bid Submission
              </h3>
              <p className="text-xs text-green-800 mt-0.5">
                All 8 mandatory compliance documents are successfully uploaded. Click submit to send your dossier to the GeM Procurement Officer for verification.
              </p>
            </div>
          </div>

          <Button
            variant="success"
            size="md"
            icon={Send}
            onClick={() => setSubmitModalOpen(true)}
            className="shrink-0 font-bold px-6"
          >
            Submit Bid Documents
          </Button>
        </div>
      )}

      {/* Upload Modal with Pipeline Simulation */}
      <Modal
        isOpen={uploadModalOpen}
        onClose={() => !isUploading && setUploadModalOpen(false)}
        title={
          isReplacingClarification
            ? `Submit Corrected Document: ${selectedDocType}`
            : `Upload Compliance Document: ${selectedDocType}`
        }
        subtitle="Upload PDF, JPG, or PNG document (Max 10 MB per file)."
      >
        <div className="space-y-4">
          {/* Target Document Selector */}
          <div>
            <label className="block text-xs font-bold text-on-surface uppercase tracking-wider mb-1.5">
              Select Document Type
            </label>
            <select
              value={selectedDocType}
              onChange={(e) => setSelectedDocType(e.target.value)}
              disabled={isUploading}
              className="w-full px-3 py-2 rounded-lg border border-outline-variant bg-surface-container-lowest text-xs text-on-surface focus:outline-none focus:border-primary"
            >
              {state.documents.map((d) => (
                <option key={d.id} value={d.type}>
                  {d.name} {d.required ? "(Required)" : "(Optional)"}
                </option>
              ))}
            </select>
          </div>

          {/* Drag & Drop Zone */}
          <label className="border-2 border-dashed border-outline-variant hover:border-primary rounded-xl p-8 flex flex-col items-center justify-center text-center cursor-pointer bg-surface-container-low/30 hover:bg-surface-container-low transition-colors">
            <input
              type="file"
              accept=".pdf,.png,.jpg,.jpeg"
              onChange={handleFileDrop}
              className="hidden"
              disabled={isUploading}
            />
            <div className="w-12 h-12 rounded-full bg-primary/10 text-primary flex items-center justify-center mb-3">
              <UploadCloud className="w-6 h-6" />
            </div>
            <p className="text-sm font-semibold text-on-surface">
              Drag & drop your file here, or <span className="text-primary underline">Browse</span>
            </p>
            <p className="text-xs text-on-surface-variant mt-1">
              Supported formats: PDF, JPG, PNG (Maximum file size: 10 MB)
            </p>
          </label>

          {/* Uploading Pipeline Animation */}
          {isUploading && (
            <div className="bg-primary-fixed/20 border border-primary/30 rounded-lg p-4 space-y-2.5">
              <div className="flex items-center gap-2 text-xs font-bold text-primary">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Processing: {activeFileName}</span>
              </div>

              <div className="space-y-1.5 text-xs">
                {pipelineSteps.map((step, idx) => (
                  <div
                    key={step}
                    className={`flex items-center gap-2 transition-colors ${
                      idx < uploadStep
                        ? "text-green-700 font-semibold"
                        : idx === uploadStep
                        ? "text-primary font-bold animate-pulse"
                        : "text-on-surface-variant/60"
                    }`}
                  >
                    {idx < uploadStep ? (
                      <CheckCircle2 className="w-3.5 h-3.5 text-green-600" />
                    ) : idx === uploadStep ? (
                      <div className="w-3.5 h-3.5 rounded-full border-2 border-primary border-t-transparent animate-spin" />
                    ) : (
                      <div className="w-3.5 h-3.5 rounded-full bg-outline-variant/40" />
                    )}
                    <span>{step}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="flex justify-end gap-2 pt-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setUploadModalOpen(false)}
              disabled={isUploading}
            >
              Cancel
            </Button>
          </div>
        </div>
      </Modal>

      {/* Document Preview Modal */}
      <DocumentPreviewModal
        isOpen={Boolean(previewDoc)}
        onClose={() => setPreviewDoc(null)}
        document={previewDoc}
      />

      {/* Final Submission Confirmation Modal */}
      <Modal
        isOpen={submitModalOpen}
        onClose={() => setSubmitModalOpen(false)}
        title="Submit Bid Documents?"
        subtitle="Confirm compliance document submission for official verification."
      >
        <div className="space-y-4 text-xs">
          <p className="text-on-surface leading-relaxed">
            You are about to submit your compliance documents for official GeM bid verification.
          </p>

          <div className="bg-amber-50 p-3.5 rounded-lg border border-amber-200 text-amber-900 leading-relaxed">
            <strong>Important Notice:</strong> After submission, documents may not be editable until an official clarification is requested by the procurement officer.
          </div>

          <div className="bg-surface-container-low p-3 rounded-lg border border-outline-variant/50 space-y-1">
            <div className="flex justify-between font-semibold">
              <span className="text-on-surface-variant">Tender:</span>
              <span className="text-on-surface">{state.tenderName}</span>
            </div>
            <div className="flex justify-between font-semibold">
              <span className="text-on-surface-variant">Bidder:</span>
              <span className="text-on-surface">{state.bidderName}</span>
            </div>
            <div className="flex justify-between font-semibold">
              <span className="text-on-surface-variant">Total Documents:</span>
              <span className="text-primary font-bold">8 Documents Attached</span>
            </div>
          </div>

          <div className="flex items-center justify-end gap-2.5 pt-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSubmitModalOpen(false)}
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={handleFinalSubmit}
              icon={Send}
            >
              Confirm Submission
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
