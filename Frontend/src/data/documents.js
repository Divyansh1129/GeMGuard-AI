export const documents = {
  "BID-2026-00428": [
    {
      id: "DOC-001",
      type: "PAN",
      name: "PAN Card",
      status: "Verified",
      finding: "Entity matched",
      ocrConfidence: 98,
      verificationConfidence: 99,
      extractedFields: {
        "PAN Number": "AABCA1234F",
        "Name on PAN": "ABC Technologies Pvt Ltd",
        "Date of Incorporation": "15 Mar 2018",
        "PAN Status": "Active",
      },
      verificationResult: {
        valid: true,
        message:
          "PAN is valid and active. Entity name matches the bidder registration.",
      },
    },
    {
      id: "DOC-002",
      type: "GST",
      name: "GST Certificate",
      status: "Verified",
      finding: "Active",
      ocrConfidence: 96,
      verificationConfidence: 98,
      extractedFields: {
        GSTIN: "09ABCDE1234F1Z5",
        "Legal Name": "ABC Technologies Private Limited",
        "Trade Name": "ABC Tech",
        "Registration Date": "12 Apr 2022",
        Status: "Active",
      },
      verificationResult: {
        valid: true,
        message:
          "GST registration is active and the entity matches the bidder's PAN.",
      },
    },
    {
      id: "DOC-003",
      type: "Udyam",
      name: "Udyam / MSME Certificate",
      status: "Review Required",
      finding: "Minor name variation",
      ocrConfidence: 94,
      verificationConfidence: 88,
      extractedFields: {
        "Udyam Number": "UDYAM-UP-09-0012345",
        "Enterprise Name": "ABC Technologies Pvt Ltd",
        Type: "Medium",
        "Date of Registration": "20 Jun 2022",
        "NIC Code": "28132",
        Activity: "Manufacture of pumps",
      },
      verificationResult: {
        valid: true,
        message:
          "Udyam registration is valid. Entity name matches PAN records.",
        warning: "Minor name variation detected across documents.",
      },
    },
    {
      id: "DOC-004",
      type: "EPFO",
      name: "EPFO Registration",
      status: "Verified",
      finding: "Matched",
      ocrConfidence: 95,
      verificationConfidence: 97,
      extractedFields: {
        "Establishment Code": "UPNOI0012345000",
        "Establishment Name": "ABC Technologies Pvt Ltd",
        "Registration Date": "01 May 2019",
        "Total Employees": "142",
        "Compliance Status": "Regular",
      },
      verificationResult: {
        valid: true,
        message:
          "EPFO registration is active and entity name matches bidder PAN.",
      },
    },
    {
      id: "DOC-005",
      type: "ESIC",
      name: "ESIC Registration",
      status: "Review Required",
      finding: "Entity name mismatch",
      ocrConfidence: 93,
      verificationConfidence: 72,
      extractedFields: {
        "ESIC Code": "12345678901234567",
        "Employer Name": "ABC Technology Solutions Pvt Ltd",
        "Registration Date": "15 Aug 2019",
        "Compliance Period": "Apr 2026 - Jun 2026",
        Status: "Active",
      },
      verificationResult: {
        valid: false,
        message:
          "ESIC entity name differs from PAN, GST and Udyam. The name on ESIC is 'ABC Technology Solutions Pvt Ltd' while other documents show 'ABC Technologies Pvt Ltd'.",
        warning: "Potential entity name mismatch detected.",
      },
    },
    {
      id: "DOC-006",
      type: "OEM",
      name: "OEM Authorization",
      status: "Review Required",
      finding: "Authorization mismatch",
      ocrConfidence: 91,
      verificationConfidence: 68,
      extractedFields: {
        "OEM Name": "Grundfos India Pvt Ltd",
        "Authorized Dealer": "ABC Tech Solutions",
        "Authorization Date": "01 Jan 2026",
        "Valid Until": "31 Dec 2026",
        "Product Category": "Centrifugal Pumps",
        Territory: "Pan India",
      },
      verificationResult: {
        valid: false,
        message:
          "OEM authorization letter names 'ABC Tech Solutions' as the authorized dealer, which does not exactly match the bidder entity 'ABC Technologies Pvt Ltd'.",
        warning: "Authorization entity name mismatch requires clarification.",
      },
    },
    {
      id: "DOC-007",
      type: "Blacklisting",
      name: "Non-Blacklisting Declaration",
      status: "Verified",
      finding: "No issues found",
      ocrConfidence: 97,
      verificationConfidence: 99,
      extractedFields: {
        "Declaration Date": "15 Aug 2026",
        "Declaring Entity": "ABC Technologies Pvt Ltd",
        "Declaration": "Not blacklisted by any Central/State Government",
        "Signatory": "Rajesh Kumar, Director",
      },
      verificationResult: {
        valid: true,
        message:
          "Non-blacklisting declaration is valid. No records found in central blacklisting database.",
      },
    },
    {
      id: "DOC-008",
      type: "StartupIndia",
      name: "Startup India Certificate",
      status: "Verified",
      finding: "Valid registration",
      ocrConfidence: 96,
      verificationConfidence: 98,
      extractedFields: {
        "DPIIT Number": "DIPP12345",
        "Entity Name": "ABC Technologies Pvt Ltd",
        "Recognition Date": "10 Sep 2022",
        "Valid Until": "09 Sep 2032",
        Sector: "Manufacturing",
      },
      verificationResult: {
        valid: true,
        message:
          "Startup India recognition is valid and entity name matches PAN.",
      },
    },
  ],
};

export const getDocumentsByBidder = (bidderId) =>
  documents[bidderId] || [];

export const getDocumentById = (bidderId, docId) =>
  (documents[bidderId] || []).find((d) => d.id === docId);
