// bidderService.js
// -------------------
// Talks to the REAL GeM Rakshak backend now (was 100% mocked before).
// This file is an ADAPTER: your backend returns snake_case fields like
// `company_name`, `compliance_score`, `risk_level` — but the existing UI
// components expect camelCase-ish fields like `name`, `complianceScore`,
// `risk` (copied from the old mock data shape in data/bidders.js).
// Rather than rewrite every component, we translate the shape HERE, once,
// so the rest of the app doesn't need to change at all.

import api from "./api";

// Cache of the last compliance check per bidder, so getAll() doesn't have
// to re-run a compliance check (slow — calls an LLM) just to build a list.
// getById() will fetch/refresh this on demand.
const complianceCache = new Map();

function mapBidder(backendBidder, complianceResult, docCount) {
  return {
    id: String(backendBidder.id), // backend uses int IDs; UI expects a string
    name: backendBidder.company_name,
    tenderId: backendBidder.tender_id || "N/A",
    tenderName: backendBidder.tender_id || "N/A", // backend has no tender names yet
    complianceScore: complianceResult?.compliance_score ?? null,
    status: mapRiskToStatus(complianceResult?.risk_level),
    risk: complianceResult?.risk_level || "Unknown",
    documentsSubmitted: docCount ?? 0,
    documentsTotal: 8, // matches the 8 statutory document types in your problem statement
    issueCount: complianceResult
      ? Object.values(complianceResult.rule_engine_result || {}).filter((c) => !c.pass).length
      : 0,
    pan: backendBidder.pan_number,
    gstin: backendBidder.gstin,
    udyamNumber: backendBidder.udyam_number,
    address: "", // not collected by backend yet
    contactPerson: "",
    contactEmail: "",
    registrationDate: backendBidder.created_at
      ? new Date(backendBidder.created_at).toLocaleDateString("en-GB", {
          day: "2-digit", month: "short", year: "numeric",
        })
      : "",
    aiRecommendation: complianceResult?.ai_recommendation || null,
    officerRemarks: null,
  };
}

// Backend doesn't have a "status" field like "Review Required" / "Verified" —
// we derive a reasonable one from risk_level so the existing status badges
// in the UI still make sense.
function mapRiskToStatus(riskLevel) {
  if (!riskLevel) return "Incomplete";
  if (riskLevel === "Low") return "Verified";
  if (riskLevel === "Medium") return "Review Required";
  if (riskLevel === "High") return "Non-Compliant";
  return "Incomplete";
}

export const bidderService = {
  async getAll() {
    const { data: bidders } = await api.get("/bidders/");
    const results = await Promise.all(
      bidders.map(async (b) => {
        let compliance = complianceCache.get(b.id);
        if (!compliance) {
          try {
            const { data } = await api.get(`/compliance/${b.id}/latest`);
            compliance = data;
            complianceCache.set(b.id, data);
          } catch {
            compliance = null; // no compliance check run yet for this bidder
          }
        }
        let docCount = 0;
        try {
          const { data: docs } = await api.get(`/documents/${b.id}`);
          docCount = docs.length;
        } catch {
          docCount = 0;
        }
        return mapBidder(b, compliance, docCount);
      })
    );
    return results;
  },

  async getById(id) {
    const { data: b } = await api.get(`/bidders/${id}`);
    if (!b) return null;

    let compliance = null;
    try {
      const { data } = await api.get(`/compliance/${id}/latest`);
      compliance = data;
      complianceCache.set(id, data);
    } catch {
      compliance = null;
    }

    let docCount = 0;
    try {
      const { data: docs } = await api.get(`/documents/${id}`);
      docCount = docs.length;
    } catch {
      docCount = 0;
    }

    return mapBidder(b, compliance, docCount);
  },

  // Backend has no tender concept yet, so this filters the full bidder list
  // by the tender_id string stored on each bidder record.
  async getByTender(tenderId) {
    const all = await this.getAll();
    return all.filter((b) => b.tenderId === tenderId);
  },

  // Runs a FRESH compliance check (calls rules + ML + LLM on the backend)
  // and updates the cache. Call this explicitly from a "Run Check" button —
  // don't call it from getAll()/getById(), it's slower (hits an LLM).
  async runComplianceCheck(id) {
    const { data } = await api.post(`/compliance/run/${id}`);
    complianceCache.set(id, data);
    return data;
  },

  async updateStatus(bidderId, status, remarks) {
    const decision = status === "Non-Compliant" ? "disqualified" : "qualified";
    const { data } = await api.post(`/compliance/${bidderId}/decision`, {
      decision,
      remarks,
    });
    return data;
  },

  // Create a new bidder (used by the bidder registration flow, if present)
  async create(bidderData) {
    const { data } = await api.post("/bidders/", {
      company_name: bidderData.name,
      company_type: bidderData.companyType || "MSME",
      pan_number: bidderData.pan,
      gstin: bidderData.gstin,
      udyam_number: bidderData.udyamNumber,
      tender_id: bidderData.tenderId,
    });
    return mapBidder(data, null, 0);
  },
};

export default bidderService;
