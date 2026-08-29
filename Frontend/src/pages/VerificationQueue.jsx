import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  ClipboardCheck,
  AlertTriangle,
  Search,
  Filter,
  ArrowRight,
  ShieldAlert,
} from "lucide-react";
import StatusBadge from "../components/common/StatusBadge";
import RiskBadge from "../components/common/RiskBadge";
import Button from "../components/common/Button";
import bidderService from "../services/bidderService";
import { issues } from "../data/issues";

export default function VerificationQueue() {
  const navigate = useNavigate();
  const [bidders, setBidders] = useState([]);
  const [filterType, setFilterType] = useState("All");
  const [search, setSearch] = useState("");

  useEffect(() => {
    async function load() {
      const data = await bidderService.getAll();
      setBidders(data);
    }
    load();
  }, []);

  const queueItems = [
    {
      id: "Q-001",
      bidderId: "BID-2026-00428",
      bidderName: "ABC Technologies Pvt Ltd",
      tenderName: "Industrial Pump Procurement",
      issue: "ESIC Entity Name Variation",
      category: "Entity Mismatch",
      severity: "Medium",
      confidence: 94,
      status: "Review Required",
      risk: "Medium",
    },
    {
      id: "Q-002",
      bidderId: "BID-2026-00428",
      bidderName: "ABC Technologies Pvt Ltd",
      tenderName: "Industrial Pump Procurement",
      issue: "OEM Authorization Mismatch",
      category: "OEM Issue",
      severity: "High",
      confidence: 98,
      status: "Review Required",
      risk: "Medium",
    },
    {
      id: "Q-003",
      bidderId: "BID-2026-00429",
      bidderName: "XYZ Industries Ltd",
      tenderName: "Industrial Pump Procurement",
      issue: "GST Certificate Validity Period Flag",
      category: "Expired Document",
      severity: "Medium",
      confidence: 91,
      status: "Review Required",
      risk: "Medium",
    },
    {
      id: "Q-004",
      bidderId: "BID-2026-00430",
      bidderName: "PQR Enterprises",
      tenderName: "Industrial Pump Procurement",
      issue: "Missing Startup India / Non-Blacklisting Attestation",
      category: "Missing Document",
      severity: "High",
      confidence: 99,
      status: "Non-Compliant",
      risk: "High",
    },
  ];

  const filteredQueue = queueItems.filter((item) => {
    const matchSearch =
      item.bidderName.toLowerCase().includes(search.toLowerCase()) ||
      item.issue.toLowerCase().includes(search.toLowerCase()) ||
      item.bidderId.toLowerCase().includes(search.toLowerCase());

    const matchFilter =
      filterType === "All" ||
      (filterType === "High Priority" && item.severity === "High") ||
      item.category === filterType;

    return matchSearch && matchFilter;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline-variant/40 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-on-surface">
            Verification Queue
          </h1>
          <p className="text-xs text-on-surface-variant mt-0.5">
            Focused triage queue for high-priority compliance anomalies requiring officer resolution.
          </p>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="w-3.5 h-3.5 text-outline absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search queue item or bidder..."
            className="pl-8 pr-3 py-1.5 text-xs rounded border border-outline-variant bg-surface-container-lowest text-on-surface focus:outline-none focus:border-primary w-60"
          />
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1">
        {[
          "All",
          "High Priority",
          "Entity Mismatch",
          "OEM Issue",
          "Expired Document",
          "Missing Document",
        ].map((tab) => (
          <button
            key={tab}
            onClick={() => setFilterType(tab)}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors shrink-0 ${
              filterType === tab
                ? "bg-primary text-on-primary shadow-xs"
                : "bg-surface-container text-on-surface-variant hover:bg-surface-container-high"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Queue Table */}
      <div className="bg-surface-container-lowest border border-outline-variant/60 rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead className="bg-[#F1F5F9] text-xs font-semibold text-on-surface-variant uppercase tracking-wider border-b border-outline-variant/50">
              <tr>
                <th className="px-5 py-3.5">Bidder Entity</th>
                <th className="px-5 py-3.5">Flagged Compliance Issue</th>
                <th className="px-5 py-3.5">Severity</th>
                <th className="px-5 py-3.5">AI Confidence</th>
                <th className="px-5 py-3.5">Status</th>
                <th className="px-5 py-3.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="text-xs divide-y divide-outline-variant/30 bg-surface-container-lowest">
              {filteredQueue.map((item) => (
                <tr
                  key={item.id}
                  onClick={() => navigate(`/bids/${item.bidderId}`)}
                  className="hover:bg-surface-container-low transition-colors group cursor-pointer"
                >
                  <td className="px-5 py-4">
                    <div className="font-bold text-on-surface group-hover:text-primary transition-colors">
                      {item.bidderName}
                    </div>
                    <div className="text-[11px] text-on-surface-variant font-mono">
                      {item.bidderId}
                    </div>
                  </td>
                  <td className="px-5 py-4">
                    <div className="font-semibold text-on-surface">
                      {item.issue}
                    </div>
                    <div className="text-[11px] text-on-surface-variant">
                      Category: {item.category}
                    </div>
                  </td>
                  <td className="px-5 py-4">
                    <span
                      className={`px-2 py-0.5 rounded-full font-bold text-[10px] uppercase ${
                        item.severity === "High"
                          ? "bg-red-100 text-red-800"
                          : "bg-amber-100 text-amber-800"
                      }`}
                    >
                      {item.severity}
                    </span>
                  </td>
                  <td className="px-5 py-4">
                    <span className="font-bold text-primary">
                      {item.confidence}%
                    </span>
                  </td>
                  <td className="px-5 py-4">
                    <StatusBadge status={item.status} size="sm" />
                  </td>
                  <td className="px-5 py-4 text-right">
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/bids/${item.bidderId}`);
                      }}
                      icon={ArrowRight}
                    >
                      Review
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
