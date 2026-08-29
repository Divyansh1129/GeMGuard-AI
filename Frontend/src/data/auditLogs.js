export const auditLogs = {
  "BID-2026-00428": [
    {
      id: "AUD-001",
      timestamp: "28 Aug 2026 — 10:30",
      actor: "System",
      action: "Bid submission received",
      type: "system",
    },
    {
      id: "AUD-002",
      timestamp: "28 Aug 2026 — 10:32",
      actor: "System",
      action: "8 documents uploaded successfully",
      type: "system",
    },
    {
      id: "AUD-003",
      timestamp: "28 Aug 2026 — 10:33",
      actor: "AI Engine",
      action: "Document classification completed — 8 types identified",
      type: "ai",
    },
    {
      id: "AUD-004",
      timestamp: "28 Aug 2026 — 10:35",
      actor: "AI Engine",
      action: "OCR extraction completed for all documents",
      type: "ai",
    },
    {
      id: "AUD-005",
      timestamp: "28 Aug 2026 — 10:36",
      actor: "AI Engine",
      action: "Rule-based validation completed — 6 passed, 2 flagged",
      type: "ai",
    },
    {
      id: "AUD-006",
      timestamp: "28 Aug 2026 — 10:37",
      actor: "AI Engine",
      action: "Cross-document verification completed",
      type: "ai",
    },
    {
      id: "AUD-007",
      timestamp: "28 Aug 2026 — 10:38",
      actor: "AI Engine",
      action: "Entity name mismatch detected — ESIC vs PAN",
      type: "warning",
    },
    {
      id: "AUD-008",
      timestamp: "28 Aug 2026 — 10:38",
      actor: "AI Engine",
      action: "OEM authorization entity mismatch detected",
      type: "warning",
    },
    {
      id: "AUD-009",
      timestamp: "28 Aug 2026 — 10:39",
      actor: "AI Engine",
      action: "Compliance score calculated — 94/100",
      type: "ai",
    },
    {
      id: "AUD-010",
      timestamp: "28 Aug 2026 — 10:40",
      actor: "AI Engine",
      action: "AI assessment: Review Required (Confidence: 92%)",
      type: "ai",
    },
    {
      id: "AUD-011",
      timestamp: "28 Aug 2026 — 10:42",
      actor: "System",
      action: "Bid queued for officer review",
      type: "system",
    },
  ],
};

export const getAuditLogsByBidder = (bidderId) =>
  auditLogs[bidderId] || [];
