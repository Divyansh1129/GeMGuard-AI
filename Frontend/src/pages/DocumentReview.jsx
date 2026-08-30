import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, CheckCircle2, ChevronRight, AlertTriangle } from "lucide-react";
import Button from "../components/common/Button";
import StatusBadge from "../components/common/StatusBadge";
import DocumentViewer from "../components/documents/DocumentViewer";
import ExtractedFields from "../components/documents/ExtractedFields";
import documentService from "../services/documentService";
import bidderService from "../services/bidderService";
import { showToast } from "../components/common/Toast";

export default function DocumentReview() {
  const { bidderId, documentId } = useParams();
  const navigate = useNavigate();

  const currentBidderId = bidderId;
  const currentDocId = documentId;

  const [bidder, setBidder] = useState(null);
  const [doc, setDoc] = useState(null);
  const [allDocs, setAllDocs] = useState([]);

  useEffect(() => {
    async function load() {
      const b = await bidderService.getById(currentBidderId);
      const d = await documentService.getById(currentBidderId, currentDocId);
      const docs = await documentService.getByBidder(currentBidderId);
      setBidder(b);
      setDoc(d);
      setAllDocs(docs);
    }
    load();
  }, [currentBidderId, currentDocId]);

  const handleSaveField = async (fieldName, newValue) => {
    const updated = await documentService.updateField(
      currentBidderId,
      currentDocId,
      fieldName,
      newValue
    );
    setDoc({ ...updated });
  };

  if (!doc) {
    return (
      <div className="text-center py-12">
        <h2 className="text-lg font-bold text-on-surface">Document Not Found</h2>
        <Button
          variant="outline"
          size="sm"
          onClick={() => navigate(`/bids/${currentBidderId}`)}
          className="mt-4"
        >
          Return to Workspace
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Header with Breadcrumbs */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline-variant/40 pb-4">
        <div>
          <button
            onClick={() => navigate(`/bids/${currentBidderId}`)}
            className="inline-flex items-center gap-1 text-xs text-primary font-semibold hover:underline mb-1"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Bidder Verification
          </button>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-on-surface">{doc.name}</h1>
            <StatusBadge status={doc.status} />
          </div>
          <p className="text-xs text-on-surface-variant mt-0.5">
            Bidder: <strong className="text-on-surface">{bidder?.name}</strong> · Document ID: {doc.id}
          </p>
        </div>

        {/* Document Selector Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 max-w-full">
          {allDocs.map((d) => (
            <button
              key={d.id}
              onClick={() => navigate(`/bids/${currentBidderId}/documents/${d.id}`)}
              className={`px-2.5 py-1 text-xs font-semibold rounded transition-colors shrink-0 ${
                d.id === doc.id
                  ? "bg-primary text-on-primary shadow-xs"
                  : "bg-surface-container text-on-surface-variant hover:bg-surface-container-high"
              }`}
            >
              {d.type}
            </button>
          ))}
        </div>
      </div>

      {/* Two Column Layout: Left Document Viewer (6 Cols), Right Extracted Fields (6 Cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch min-h-[600px]">
        {/* Left: Document Viewer */}
        <div className="lg:col-span-6 flex flex-col">
          <DocumentViewer document={doc} />
        </div>

        {/* Right: Extracted OCR Fields */}
        <div className="lg:col-span-6 flex flex-col">
          <ExtractedFields document={doc} onSaveField={handleSaveField} />
        </div>
      </div>
    </div>
  );
}
