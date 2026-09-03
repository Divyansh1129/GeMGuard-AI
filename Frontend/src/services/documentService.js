// documentService.js
// ---------------------
// Real backend calls now. Same adapter approach as bidderService.js:
// backend gives you `extracted_fields` as a JSON STRING and a reconciled
// `verification_result` object (with field_checks, overall_status, overall_score,
// extraction_confidence). We map these to the richer shape the UI expects,
// keeping OCR/extraction confidence SEPARATE from compliance score.

import api, { API_BASE_URL } from "./api";

function mapDocument(backendDoc) {
  let extractedFields = {};
  let parseError = false;
  try {
    const parsed = JSON.parse(backendDoc.extracted_fields || "{}");
    if (parsed._parse_error) {
      parseError = true;
    } else {
      extractedFields = parsed;
    }
  } catch {
    parseError = true;
  }

  // The backend now returns a reconciled verification_result object per document.
  // It contains: document_id, document_type, extraction_confidence, extracted_fields,
  // field_checks[], overall_status (pass|fail|needs_review), overall_score (0-100).
  const vr = backendDoc.verification_result || null;

  // Extraction confidence = how well OCR/LLM could read the document (0-100%)
  const extractionConfidence = vr?.extraction_confidence != null
    ? Math.round(vr.extraction_confidence * 100)
    : (typeof extractedFields.confidence === "number" ? Math.round(extractedFields.confidence * 100) : null);

  // Compliance score = derived ONLY from field_checks pass/fail (0-100)
  const overallScore = vr?.overall_score ?? null;
  const overallStatus = vr?.overall_status ?? null;
  const fieldChecks = vr?.field_checks ?? [];

  return {
    id: String(backendDoc.id),
    type: backendDoc.doc_type,
    name: backendDoc.doc_type, // backend doesn't store a separate display name
    required: true,
    uploaded: true,
    fileName: extractedFields.file_name || null,
    fileSize: extractedFields.file_size || null,
    fileUrl: `${API_BASE_URL}/documents/${backendDoc.id}/file`,
    uploadDate: backendDoc.uploaded_at
      ? new Date(backendDoc.uploaded_at).toLocaleDateString("en-GB", {
          day: "2-digit", month: "short", year: "numeric",
        })
      : null,
    status: parseError ? "Pending Verification" : mapVerificationStatus(backendDoc.verification_status),
    finding: parseError
      ? "Automatic field extraction failed — document may need re-upload or manual review."
      : "Document evidence extracted. Official registry verification is not configured.",

    // SEPARATE metrics — never conflate these two
    ocrConfidence: extractionConfidence,           // OCR/extraction quality (%)
    extractionConfidence: extractionConfidence,     // alias for clarity
    overallScore: overallScore,                     // compliance score from field_checks
    overallStatus: overallStatus,                   // pass | fail | needs_review
    fieldChecks: fieldChecks,                       // backend field_checks array

    // verificationConfidence is the compliance-derived score, NOT OCR confidence
    verificationConfidence: overallScore,

    extractedFields,
    verificationResult: parseError || backendDoc.verification_status === "invalid"
      ? { valid: false, message: extractedFields.error || "No reliable text could be extracted from this document." }
      : { valid: backendDoc.verification_status === "verified", message: backendDoc.verification_status === "pending" ? "Awaiting evidence-based compliance check; no official registry query has been made." : "Document-evidence checks completed. Official registry status is unavailable until an authorised adapter is configured." },
    rawText: backendDoc.extracted_text || "",
  };
}

function mapVerificationStatus(status) {
  const map = {
    pending: "Pending Verification",
    verified: "Verified",
    mismatch: "Clarification Required",
    invalid: "Non-Compliant",
  };
  return map[status] || "Pending Verification";
}

export const documentService = {
  async getByBidder(bidderId) {
    const { data } = await api.get(`/documents/${bidderId}`);
    return data.map(mapDocument);
  },

  async getById(bidderId, docId) {
    const docs = await this.getByBidder(bidderId);
    return docs.find((d) => d.id === docId || d.type === docId) || null;
  },

  // Uploads a real file to the backend — triggers OCR + LLM extraction server-side.
  // `docType` should be one of: udyam, gst, pan, epfo, esic, startup_india, nsic, oem_auth
  async upload(bidderId, docType, file) {
    const formData = new FormData();
    formData.append("doc_type", docType);
    formData.append("file", file);
    const { data } = await api.post(`/documents/upload/${bidderId}`, formData, true);
    return mapDocument(data);
  },

  async updateField(bidderId, docId, fieldName, newValue) {
    const { data } = await api.patch(`/documents/${docId}/fields`, { field_name: fieldName, value: newValue });
    return mapDocument(data);
  },
};

export default documentService;
