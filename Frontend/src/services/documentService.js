// documentService.js
// ---------------------
// Real backend calls now. Same adapter approach as bidderService.js:
// backend gives you `extracted_fields` as a JSON STRING and a simple
// `verification_status`; the UI expects a richer object shape (with
// ocrConfidence, finding, verificationResult, etc. — copied from the old
// mock data). We map what we genuinely have, and fill the rest with
// sensible defaults since your current backend doesn't compute those yet.

import api from "./api";

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

  return {
    id: String(backendDoc.id),
    type: backendDoc.doc_type,
    name: backendDoc.doc_type, // backend doesn't store a separate display name
    required: true,
    uploaded: true,
    fileName: null, // backend doesn't return the original filename in this endpoint
    fileSize: null,
    uploadDate: backendDoc.uploaded_at
      ? new Date(backendDoc.uploaded_at).toLocaleDateString("en-GB", {
          day: "2-digit", month: "short", year: "numeric",
        })
      : null,
    status: parseError ? "Pending Verification" : mapVerificationStatus(backendDoc.verification_status),
    finding: parseError
      ? "Automatic field extraction failed — document may need re-upload or manual review."
      : "Document processed by AI extraction pipeline",
    ocrConfidence: null, // not computed by current backend — add later if needed
    verificationConfidence: null,
    extractedFields,
    verificationResult: parseError
      ? { valid: false, message: "Could not extract structured fields from this document." }
      : { valid: true, message: "Fields extracted successfully." },
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

  // NOTE: backend does not currently support editing an extracted field
  // after the fact. This is a local-only stub so the DocumentReview page
  // doesn't crash — the edit will NOT persist to the backend on refresh.
  async updateField(bidderId, docId, fieldName, newValue) {
    console.warn(
      "documentService.updateField: backend has no endpoint for this yet — change is local-only and will not persist."
    );
    const doc = await this.getById(bidderId, docId);
    if (doc) doc.extractedFields[fieldName] = newValue;
    return doc;
  },
};

export default documentService;
