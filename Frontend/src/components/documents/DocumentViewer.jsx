import React, { useState } from "react";
import {
  ZoomIn,
  ZoomOut,
  RotateCw,
  Maximize2,
  ChevronLeft,
  ChevronRight,
  Download,
  FileCheck,
} from "lucide-react";
import Button from "../common/Button";

export default function DocumentViewer({ document: doc }) {
  const [zoom, setZoom] = useState(100);
  const [rotation, setRotation] = useState(0);
  const [page, setPage] = useState(1);
  const totalPages = 1;

  const handleZoomIn = () => setZoom((prev) => Math.min(prev + 25, 200));
  const handleZoomOut = () => setZoom((prev) => Math.max(prev - 25, 50));
  const handleRotate = () => setRotation((prev) => (prev + 90) % 360);

  return (
    <div className="bg-surface-container-lowest border border-outline-variant/60 rounded-lg flex flex-col h-full overflow-hidden shadow-xs">
      {/* Toolbar */}
      <div className="bg-surface-container-low px-4 py-2.5 border-b border-outline-variant/50 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <FileCheck className="w-4 h-4 text-primary" />
          <span className="text-xs font-bold text-on-surface truncate max-w-[200px]">
            {doc?.name || "Document Preview"}
          </span>
          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-surface-container text-on-surface-variant">
            {doc?.type || "PDF"}
          </span>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-1">
          <button
            onClick={handleZoomOut}
            className="p-1.5 rounded hover:bg-surface-container text-on-surface-variant transition-colors"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <span className="text-xs font-mono text-on-surface-variant px-1">
            {zoom}%
          </span>
          <button
            onClick={handleZoomIn}
            className="p-1.5 rounded hover:bg-surface-container text-on-surface-variant transition-colors"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4" />
          </button>

          <div className="h-4 w-px bg-outline-variant/60 mx-1" />

          <button
            onClick={handleRotate}
            className="p-1.5 rounded hover:bg-surface-container text-on-surface-variant transition-colors"
            title="Rotate Clockwise"
          >
            <RotateCw className="w-4 h-4" />
          </button>

          <div className="h-4 w-px bg-outline-variant/60 mx-1" />

          <div className="flex items-center gap-1 text-xs text-on-surface-variant">
            <button
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
              className="p-1 rounded hover:bg-surface-container disabled:opacity-40"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
            </button>
            <span>
              {page} / {totalPages}
            </span>
            <button
              disabled={page >= totalPages}
              onClick={() => setPage((p) => p + 1)}
              className="p-1 rounded hover:bg-surface-container disabled:opacity-40"
            >
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Uploaded source file and the exact OCR transcription */}
      <div className="flex-1 bg-surface-container-high/50 p-6 overflow-auto flex items-center justify-center min-h-[420px]">
        <div
          style={{
            transform: `scale(${zoom / 100}) rotate(${rotation}deg)`,
            transformOrigin: "center center",
            transition: "transform 0.2s ease-out",
          }}
          className="w-full min-h-[620px] max-w-3xl bg-white border-2 border-slate-300 shadow-md rounded overflow-hidden"
        >
          {doc?.fileUrl ? <iframe title={`Uploaded ${doc.name}`} src={doc.fileUrl} className="w-full h-[430px] border-0" /> : null}
          <div className="border-t border-slate-200 p-4 text-xs text-slate-800">
            <h4 className="font-bold mb-2">OCR transcription</h4>
            {doc?.rawText ? <ol className="list-decimal list-inside space-y-1 font-mono whitespace-pre-wrap">{doc.rawText.split("\n").map((line, index) => <li key={index}>{line || " "}</li>)}</ol> : <p>No OCR text was recovered from this upload.</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
