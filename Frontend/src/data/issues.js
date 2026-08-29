export const issues = {
  "BID-2026-00428": [
    {
      id: "ISS-001",
      title: "Potential Entity Name Variation",
      description:
        "The ESIC entity name differs from the name appearing on the PAN, GST and Udyam documents.",
      affectedDocuments: ["PAN", "ESIC"],
      severity: "Medium",
      aiConfidence: 94,
      recommendedAction: "Request clarification from bidder",
      details: {
        comparison: [
          { document: "PAN", value: "ABC Technologies Pvt Ltd" },
          { document: "GST", value: "ABC Technologies Private Limited" },
          { document: "Udyam", value: "ABC Technologies Pvt Ltd" },
          { document: "EPFO", value: "ABC Technologies Pvt Ltd" },
          { document: "ESIC", value: "ABC Technology Solutions Pvt Ltd" },
        ],
        aiExplanation:
          "The ESIC entity name differs from the name appearing on the PAN, GST and Udyam documents. The difference may be a naming variation, but manual verification is recommended.",
      },
      reviewed: false,
    },
    {
      id: "ISS-002",
      title: "OEM Authorization Mismatch",
      description:
        "The OEM authorization letter names a different entity than the bidder's registered name.",
      affectedDocuments: ["Bidder Profile", "OEM Authorization"],
      severity: "High",
      aiConfidence: 98,
      recommendedAction: "Manual verification required",
      details: {
        comparison: [
          { document: "Bidder Registration", value: "ABC Technologies Pvt Ltd" },
          { document: "OEM Authorization", value: "ABC Tech Solutions" },
        ],
        aiExplanation:
          "The OEM authorization letter issued by Grundfos India names 'ABC Tech Solutions' as the authorized dealer. This does not match the bidder's registered entity name 'ABC Technologies Pvt Ltd'. The bidder should provide a corrected OEM authorization letter or clarify the relationship between these entities.",
      },
      reviewed: false,
    },
  ],
};

export const getIssuesByBidder = (bidderId) => issues[bidderId] || [];
