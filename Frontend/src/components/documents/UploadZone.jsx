import React, { useState } from "react";
import { Upload, FileText, CheckCircle2, Clock, Loader2 } from "lucide-react";
import Button from "../common/Button";
import { showToast } from "../common/Toast";

export default function UploadZone({ onUploadComplete }) {
  const [files, setFiles] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);

  const pipelineSteps = [
    "Upload completed",
    "Document classification",
    "OCR extraction",
    "Cross-document verification",
    "AI compliance analysis",
  ];

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files || []);
    if (selectedFiles.length === 0) return;

    const fileList = selectedFiles.map((f) => ({
      name: f.name,
      size: (f.size / (1024 * 1024)).toFixed(2) + " MB",
      status: "Queued",
    }));

    setFiles(fileList);
    processUploads(selectedFiles, fileList);
  };

  const processUploads = async (selectedFiles, fileList) => {
    setIsProcessing(true);
    setCurrentStep(0);
    try {
      await onUploadComplete?.(selectedFiles);
      setCurrentStep(pipelineSteps.length - 1);
      setFiles(fileList.map((file) => ({ ...file, status: "Complete" })));
      showToast("Documents were sent to the verification pipeline.", "success");
    } catch (error) {
      setFiles(fileList.map((file) => ({ ...file, status: "Failed" })));
      showToast(error.message || "Upload failed", "error");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="bg-surface-container-lowest border border-outline-variant/60 rounded-lg p-6 space-y-4">
      <div>
        <h3 className="text-base font-bold text-on-surface">
          Upload Bid Documents
        </h3>
        <p className="text-xs text-on-surface-variant">
          Upload PDF, JPG, or PNG compliance files for OCR extraction and automated rule checks.
        </p>
      </div>

      {/* Drag & Drop Zone */}
      <label className="border-2 border-dashed border-outline-variant hover:border-primary rounded-xl p-8 flex flex-col items-center justify-center text-center cursor-pointer bg-surface-container-low/30 hover:bg-surface-container-low transition-colors">
        <input
          type="file"
          multiple
          accept=".pdf,.png,.jpg,.jpeg"
          onChange={handleFileChange}
          className="hidden"
          disabled={isProcessing}
        />
        <div className="w-12 h-12 rounded-full bg-primary/10 text-primary flex items-center justify-center mb-3">
          <Upload className="w-6 h-6" />
        </div>
        <p className="text-sm font-semibold text-on-surface">
          Drag & drop files here, or <span className="text-primary underline">Browse</span>
        </p>
        <p className="text-xs text-on-surface-variant mt-1">
          Supports PAN, GST, Udyam, EPFO, ESIC, OEM Letters (Max 25MB per document)
        </p>
      </label>

      {/* Pipeline Status */}
      {isProcessing && (
        <div className="bg-primary-fixed/20 border border-primary/30 rounded-lg p-4 space-y-2.5">
          <div className="flex items-center gap-2 text-xs font-bold text-primary">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>Processing Documents via Compliance AI Pipeline...</span>
          </div>

          <div className="space-y-1.5 text-xs">
            {pipelineSteps.map((step, idx) => (
              <div
                key={step}
                className={`flex items-center gap-2 transition-colors ${
                  idx < currentStep
                    ? "text-green-700 font-semibold"
                    : idx === currentStep
                    ? "text-primary font-bold animate-pulse"
                    : "text-on-surface-variant/60"
                }`}
              >
                {idx < currentStep ? (
                  <CheckCircle2 className="w-3.5 h-3.5 text-green-600" />
                ) : idx === currentStep ? (
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

      {/* Selected / Uploaded Files List */}
      {files.length > 0 && (
        <div className="space-y-2">
          <span className="text-xs font-bold text-on-surface-variant uppercase tracking-wider block">
            Uploaded Files ({files.length})
          </span>
          <div className="grid gap-2">
            {files.map((file, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-2.5 rounded border border-outline-variant/50 bg-surface-container-low/40 text-xs"
              >
                <div className="flex items-center gap-2 truncate">
                  <FileText className="w-4 h-4 text-primary shrink-0" />
                  <span className="font-semibold text-on-surface truncate">
                    {file.name}
                  </span>
                  <span className="text-on-surface-variant text-[11px]">
                    ({file.size})
                  </span>
                </div>
                <div className="flex items-center gap-1.5 font-semibold shrink-0">
                  {file.status === "Complete" ? (
                    <span className="text-green-700 flex items-center gap-1">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Complete
                    </span>
                  ) : (
                    <span className="text-primary flex items-center gap-1">
                      <Loader2 className="w-3.5 h-3.5 animate-spin" /> Processing
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
