import React, { useEffect, useState } from "react";
import { FileText, CheckCircle2, AlertCircle, Clock, X, Calendar, HardDrive, Hash, Shield } from "lucide-react";
import Modal from "../common/Modal";
import Button from "../common/Button";
import StatusBadge from "../common/StatusBadge";

export default function DocumentPreviewModal({ isOpen, onClose, document: doc }) {
  const [previewUrl, setPreviewUrl] = useState(null);

  useEffect(() => {
    if (!isOpen || !doc?.fileUrl) return undefined;
    let objectUrl;
    fetch(doc.fileUrl)
      .then((response) => {
        if (!response.ok) throw new Error("The uploaded file is unavailable.");
        return response.blob();
      })
      .then((blob) => {
        objectUrl = URL.createObjectURL(blob);
        setPreviewUrl(objectUrl);
      })
      .catch(() => setPreviewUrl(null));
    return () => {
      if (objectUrl) URL.revokeObjectURL(objectUrl);
      setPreviewUrl(null);
    };
  }, [isOpen, doc?.fileUrl]);

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
              <h4 className="text-sm font-bold text-on-surface">{doc.fileName || "Uploaded document"}</h4>
              <div className="flex items-center gap-2 text-xs text-on-surface-variant mt-0.5">
                <span className="font-mono">{doc.type}</span>
                <span>•</span>
                <span>{doc.fileSize ? `${doc.fileSize} bytes` : "Size unavailable"}</span>
                <span>•</span>
                <span>Uploaded on {doc.uploadDate || "date unavailable"}</span>
              </div>
            </div>
          </div>
          <StatusBadge status={doc.status} size="sm" />
        </div>

        {previewUrl ? <object data={previewUrl} type="application/pdf" className="w-full h-80 border border-outline-variant rounded-lg"><a href={previewUrl} target="_blank" rel="noreferrer">Open uploaded PDF</a></object> : <p className="text-xs text-on-surface-variant">Loading the uploaded file preview…</p>}

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
