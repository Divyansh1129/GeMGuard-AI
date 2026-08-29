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

      {/* Realistic Government Certificate Canvas / Document Canvas */}
      <div className="flex-1 bg-surface-container-high/50 p-6 overflow-auto flex items-center justify-center min-h-[420px]">
        <div
          style={{
            transform: `scale(${zoom / 100}) rotate(${rotation}deg)`,
            transformOrigin: "center center",
            transition: "transform 0.2s ease-out",
          }}
          className="w-[480px] min-h-[620px] bg-white border-2 border-slate-300 shadow-md p-8 rounded flex flex-col justify-between select-none relative"
        >
          {/* Government Watermark / Header */}
          <div className="text-center border-b-2 border-slate-800 pb-4">
            <div className="text-[10px] uppercase font-bold tracking-widest text-slate-500 mb-1">
              Government of India / Procurement Compliance Record
            </div>
            <div className="text-base font-bold text-slate-900 tracking-tight">
              {doc?.name?.toUpperCase() || "OFFICIAL CERTIFICATE"}
            </div>
            <div className="text-[11px] text-slate-600 font-mono mt-0.5">
              Verified via National e-Governance Directory
            </div>
          </div>

          {/* Document Content Rendered Cleanly */}
          <div className="my-6 space-y-4 text-xs text-slate-800">
            <div className="bg-slate-50 p-3 rounded border border-slate-200">
              <div className="text-[10px] uppercase font-semibold text-slate-500 mb-1">
                Registered Legal Entity
              </div>
              <div className="text-sm font-bold text-slate-900">
                {doc?.extractedFields?.["Legal Name"] ||
                  doc?.extractedFields?.["Name on PAN"] ||
                  doc?.extractedFields?.["Enterprise Name"] ||
                  doc?.extractedFields?.["Employer Name"] ||
                  doc?.extractedFields?.["Declaring Entity"] ||
                  "ABC Technologies Pvt Ltd"}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              {doc?.extractedFields &&
                Object.entries(doc.extractedFields).map(([k, v]) => (
                  <div key={k} className="p-2 border-b border-slate-200">
                    <span className="text-[10px] text-slate-500 block uppercase font-medium">
                      {k}
                    </span>
                    <span className="font-semibold text-slate-900 font-mono text-[11px]">
                      {v}
                    </span>
                  </div>
                ))}
            </div>
          </div>

          {/* Official Stamp & Security QR */}
          <div className="pt-4 border-t-2 border-dashed border-slate-300 flex items-center justify-between">
            <div className="space-y-0.5">
              <div className="text-[9px] text-slate-500 uppercase">
                Digital Verification Hash
              </div>
              <div className="font-mono text-[10px] text-slate-700">
                SHA256: 8f9b...a42e-GOV-CERT
              </div>
            </div>
            <div className="w-12 h-12 border-2 border-primary/40 rounded flex items-center justify-center text-[9px] text-primary font-bold text-center leading-tight bg-primary/5">
              SEAL
              <br />
              VALID
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
