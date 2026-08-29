import React from "react";
import { FileText, CheckCircle2, AlertCircle, Clock, X, Calendar, HardDrive, Hash, Shield } from "lucide-react";
import Modal from "../common/Modal";
import Button from "../common/Button";
import StatusBadge from "../common/StatusBadge";

export default function DocumentPreviewModal({ isOpen, onClose, document: doc }) {
  if (!doc) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Document Preview: ${doc.name}`}
      subtitle="View your submitted compliance file details."
      maxWidth="max-w-2xl"
    >
      <div className="space-y-4">
        {/* Document Header Meta */}
        <div className="bg-surface-container-low p-4 rounded-lg border border-outline-variant/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-primary/10 text-primary flex items-center justify-center shrink-0">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-on-surface">{doc.fileName || `${doc.type}_Document.pdf`}</h4>
              <div className="flex items-center gap-2 text-xs text-on-surface-variant mt-0.5">
                <span className="font-mono">{doc.type}</span>
                <span>•</span>
                <span>{doc.fileSize || "1.8 MB"}</span>
                <span>•</span>
                <span>Uploaded on {doc.uploadDate || "20 Aug 2026"}</span>
              </div>
            </div>
          </div>
          <StatusBadge status={doc.status} size="sm" />
        </div>

        {/* Mock Document Render Window */}
        <div className="border border-outline-variant rounded-lg p-6 bg-surface-container-lowest flex flex-col items-center justify-center min-h-[220px] text-center space-y-3">
          <div className="w-14 h-14 rounded-full bg-primary-fixed/40 flex items-center justify-center text-primary">
            <FileText className="w-7 h-7" />
          </div>
          <div>
            <p className="text-xs font-bold text-on-surface">
              {doc.fileName || `${doc.name}.pdf`}
            </p>
            <p className="text-[11px] text-on-surface-variant mt-0.5">
              Secure GeM Document Repository · SHA-256 Verified
            </p>
          </div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-green-50 text-green-700 text-xs font-semibold border border-green-200">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Document Integrity Verified</span>
          </div>
        </div>

        {/* Basic Extracted Fields Preview (Clean, bidder-appropriate) */}
        {doc.extractedFields && Object.keys(doc.extractedFields).length > 0 && (
          <div className="space-y-2">
            <h5 className="text-xs font-bold text-on-surface uppercase tracking-wider">
              Extracted Information
            </h5>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 bg-surface-container-low/50 p-3 rounded-lg border border-outline-variant/40">
              {Object.entries(doc.extractedFields).map(([k, v]) => (
                <div key={k} className="text-xs">
                  <span className="text-on-surface-variant font-medium block text-[11px]">
                    {k}
                  </span>
                  <span className="font-semibold text-on-surface break-words">
                    {String(v)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Clarification Alert if applicable */}
        {doc.clarificationMessage && (
          <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-900 flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold block">Officer Clarification Note:</span>
              <p className="mt-0.5 text-amber-800">{doc.clarificationMessage}</p>
            </div>
          </div>
        )}

        <div className="flex justify-end pt-2">
          <Button variant="ghost" size="sm" onClick={onClose}>
            Close Preview
          </Button>
        </div>
      </div>
    </Modal>
  );
}
