// bidderStore.js
// -----------------
// REWRITTEN to pull from the real GeMGuard AI backend instead of a fake
// localStorage snapshot. Every page (BidderDashboard, BidderDocuments,
// BidderProfile, BidderStatus, BidderSidebar, BidderTopbar, OfficerDecision)
// calls getState() / subscribe() / uploadDocument() etc — those function
// NAMES are kept identical on purpose, so none of those pages needed to
// change. Only what happens INSIDE these functions changed: real fetch
// calls instead of reading/writing localStorage mock data.

import api, { API_BASE_URL } from "./api";
import documentService from "./documentService";
import bidderService from "./bidderService";

const AUTH_KEY = "gem_rakshak_bidder_auth";

// The 8 statutory document types from the problem statement. `type` is
// what the UI displays; `backendType` is what gets sent to/matched against
// your FastAPI backend's doc_type field.
const DOC_CHECKLIST = [
  { id: "DOC-001", type: "PAN", name: "PAN Card", required: true, backendType: "pan" },
  { id: "DOC-002", type: "GST", name: "GST Certificate", required: true, backendType: "gst" },
  { id: "DOC-003", type: "Udyam", name: "Udyam / MSME Certificate", required: true, backendType: "udyam" },
  { id: "DOC-004", type: "EPFO", name: "EPFO Registration", required: true, backendType: "epfo" },
  { id: "DOC-005", type: "ESIC", name: "ESIC Registration", required: true, backendType: "esic" },
  { id: "DOC-006", type: "Non-Blacklisting", name: "Non-Blacklisting Declaration", required: true, backendType: "non_blacklisting" },
  { id: "DOC-007", type: "StartupIndia", name: "Startup India Certificate", required: false, backendType: "startup_india" },
  { id: "DOC-008", type: "OEM", name: "OEM Authorization", required: true, backendType: "oem_auth" },
];

function getAuth() {
  try {
    return JSON.parse(localStorage.getItem(AUTH_KEY));
  } catch {
    return null;
  }
}

function blankDocs() {
  return DOC_CHECKLIST.map((def) => ({
    id: def.id,
    type: def.type,
    name: def.name,
    required: def.required,
    uploaded: false,
    fileName: null,
    fileSize: null,
    uploadDate: null,
    status: "Not Uploaded",
    finding: "Pending upload by bidder",
    ocrConfidence: null,
    verificationConfidence: null,
    clarificationMessage: null,
    extractedFields: {},
    verificationResult: null,
  }));
}

// In-memory current state (module-level, shared across every component
// that imports this store — mirrors the original design, just fed by
// real data now instead of localStorage).
let currentState = buildDefaultState();
const listeners = new Set();

function buildDefaultState() {
  const auth = getAuth();
  return {
    bidId: auth?.bidderRealId ? String(auth.bidderRealId) : null,
    bidderId: auth?.bidderRealId ? String(auth.bidderRealId) : null,
    tenderId: auth?.tenderId || "N/A",
    tenderName: auth?.tenderName || "N/A",
    department: auth?.department || "",
    submissionDeadline: auth?.submissionDeadline || "",
    bidderName: auth?.companyName || "",
    gstin: "",
    pan: "",
    udyamNumber: "",
    contactPerson: "",
    contactEmail: auth?.email || "",
    contactPhone: "",
    address: "",
    status: "Incomplete",
    submissionDate: null,
    documents: blankDocs(),
    clarifications: [],
  };
}

function notify() {
  listeners.forEach((fn) => fn(currentState));
}

// Pulls the real bidder + real documents from the backend and rebuilds
// currentState. Called automatically whenever a page subscribes (i.e. on
// mount), so no individual page needs to trigger this manually.
async function refreshFromBackend() {
  const auth = getAuth();
  if (!auth?.bidderRealId) return;

  try {
    const { data: bidder } = await api.get(`/bidders/${auth.bidderRealId}`);
    let backendDocs = [];
    try {
      const { data } = await api.get(`/documents/${auth.bidderRealId}`);
      backendDocs = data;
    } catch {
      backendDocs = [];
    }

    const documents = DOC_CHECKLIST.map((def) => {
      const match = backendDocs.find((d) => d.doc_type === def.backendType);
      if (!match) {
        return blankDocs().find((d) => d.id === def.id);
      }
      const mapped = documentService === documentService ? null : null; // no-op guard
      let extractedFields = {};
      let parseError = false;
      try {
        const parsed = JSON.parse(match.extracted_fields || "{}");
        if (parsed._parse_error) parseError = true;
        else extractedFields = parsed;
      } catch {
        parseError = true;
      }
      return {
        id: String(match.id),
        type: def.type,
        name: def.name,
        required: def.required,
        uploaded: true,
        fileName: extractedFields.file_name || null,
        fileSize: extractedFields.file_size || null,
        fileUrl: `${API_BASE_URL}/documents/${match.id}/file`,
        uploadDate: match.uploaded_at
          ? new Date(match.uploaded_at).toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" })
          : null,
        status: parseError ? "Pending Verification" : ({ pending: "Pending Verification", verified: "Verified", mismatch: "Clarification Required", invalid: "Non-Compliant" }[match.verification_status] || "Pending Verification"),
        finding: parseError
          ? "Automatic field extraction failed — please re-upload a clearer copy."
          : "Document processed by AI extraction pipeline",
        ocrConfidence: typeof extractedFields.confidence === "number" ? Math.round(extractedFields.confidence * 100) : null,
        verificationConfidence: null,
        clarificationMessage: null,
        extractedFields,
        rawText: match.extracted_text || "",
        verificationResult: parseError
          ? { valid: false, message: "Could not extract structured fields." }
          : { valid: true, message: "Fields extracted successfully." },
      };
    });

    const requiredDocs = documents.filter((d) => d.required);
    const uploadedRequired = requiredDocs.filter((d) => d.uploaded);
    let status = currentState.status;
    if (uploadedRequired.length === requiredDocs.length && (status === "Draft" || status === "Incomplete")) {
      status = "Ready for Submission";
    } else if (uploadedRequired.length < requiredDocs.length) {
      status = "Incomplete";
    }

    currentState = {
      ...currentState,
      bidId: String(bidder.id),
      bidderId: String(bidder.id),
      tenderId: bidder.tender_id || "N/A",
      bidderName: bidder.company_name,
      gstin: bidder.gstin || "",
      pan: bidder.pan_number || "",
      udyamNumber: bidder.udyam_number || "",
      status,
      documents,
    };
    notify();
  } catch (err) {
    console.error("bidderStore: failed to refresh from backend", err);
  }
}

export const bidderStore = {
  subscribe(fn) {
    listeners.add(fn);
    refreshFromBackend(); // pull real data as soon as any page mounts
    return () => listeners.delete(fn);
  },

  getState() {
    return currentState;
  },

  resetToDefault() {
    currentState = buildDefaultState();
    notify();
    return currentState;
  },

  // Real upload — sends the file to your backend (OCR + LLM extraction),
  // then refreshes state so the UI reflects the real extracted result.
  async uploadDocument(type, fileObj) {
    const auth = getAuth();
    if (!auth?.bidderRealId) {
      console.error("bidderStore.uploadDocument: no logged-in bidder with a real backend ID");
      return currentState;
    }
    const def = DOC_CHECKLIST.find((d) => d.type === type || d.id === type);
    const backendType = def?.backendType || type.toLowerCase();

    try {
      await documentService.upload(auth.bidderRealId, backendType, fileObj);
    } catch (err) {
      throw err;
    }
    await refreshFromBackend();
    return currentState;
  },

  // Backend has no "submit bid" endpoint — this just updates local UI
  // status. If you want this to be real, we'd add a backend endpoint.
  submitBid() {
    currentState = {
      ...currentState,
      status: "Under Verification",
      submissionDate: new Date().toLocaleDateString("en-GB", {
        day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit",
      }),
    };
    notify();
    return currentState;
  },

  // Backend has no clarification workflow yet — local-only, does not persist.
  requestClarification(docType, officerMessage) {
    console.warn("bidderStore.requestClarification: not persisted to backend yet — local UI only.");
    const documents = currentState.documents.map((doc) =>
      doc.type.toLowerCase().includes(docType.toLowerCase())
        ? { ...doc, status: "Clarification Required", clarificationMessage: officerMessage }
        : doc
    );
    currentState = {
      ...currentState,
      documents,
      status: "Clarification Required",
      clarifications: [
        { id: `CLR-${Date.now()}`, docType, message: officerMessage, requestedAt: "Just now", status: "Pending" },
        ...(currentState.clarifications || []),
      ],
    };
    notify();
    return currentState;
  },

  async updateProfile(profileData) {
    const auth = getAuth();
    if (!auth?.bidderRealId) throw new Error("No authenticated bidder record is available.");
    await bidderService.update(auth.bidderRealId, profileData);
    currentState = { ...currentState, ...profileData };
    await refreshFromBackend();
    notify();
    return currentState;
  },
};

export default bidderStore;
