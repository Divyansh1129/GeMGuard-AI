import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Gavel,
  FileCheck,
  AlertTriangle,
  Shield,
  ArrowLeft,
  ChevronRight,
  Search,
  RefreshCw,
} from "lucide-react";
import KPICard from "../components/common/KPICard";
import StatusBadge from "../components/common/StatusBadge";
import RiskBadge from "../components/common/RiskBadge";
import Button from "../components/common/Button";
import tenderService from "../services/tenderService";
import bidderService from "../services/bidderService";
import { showToast } from "../components/common/Toast";

export default function TenderDetails() {
  const { tenderId } = useParams();
  const navigate = useNavigate();
  const decodedId = decodeURIComponent(tenderId || "GEM/2026/MPNG/001");

  const [tender, setTender] = useState(null);
  const [bidders, setBidders] = useState([]);
  const [availableBidders, setAvailableBidders] = useState([]);
  const [selectedBidderId, setSelectedBidderId] = useState("");
  const [linking, setLinking] = useState(false);
  const [search, setSearch] = useState("");
  const [rechecking, setRechecking] = useState(false);

  const loadTenderData = async () => {
    const [t, b, allBidders] = await Promise.all([
      tenderService.getById(decodedId),
      bidderService.getByTender(decodedId),
      bidderService.getAll(),
    ]);
    setTender(t);
    setBidders(b);
    setAvailableBidders(allBidders);
  };

  const handleLinkBidder = async () => {
    if (!selectedBidderId) return;
    setLinking(true);
    try {
      await bidderService.linkToTender(selectedBidderId, decodedId);
      await bidderService.runComplianceCheck(selectedBidderId);
      await loadTenderData();
      setSelectedBidderId("");
      showToast("Bidder linked and compared against this tender.", "success");
    } catch (error) {
      showToast(error.message || "Unable to link bidder to this tender.", "error");
    } finally {
      setLinking(false);
    }
  };

  useEffect(() => {
    loadTenderData();
  }, [decodedId]);

  const handleRefreshAndRecheck = async () => {
    setRechecking(true);
    try {
      const linkedBidders = await bidderService.getByTender(decodedId);
      await Promise.all(linkedBidders.map((bidder) => bidderService.runComplianceCheck(bidder.id)));
      await loadTenderData();
      showToast(
        linkedBidders.length
          ? `Rechecked ${linkedBidders.length} linked bidder(s) against this tender.`
          : "Tender refreshed. Link a bidder to this tender to run its compliance check.",
        "success"
      );
    } catch (error) {
      showToast(error.message || "Unable to refresh tender compliance.", "error");
    } finally {
      setRechecking(false);
    }
  };

  if (!tender) {
    return (
      <div className="text-center py-12">
        <h2 className="text-lg font-bold text-on-surface">Tender Not Found</h2>
        <Button
          variant="outline"
          size="sm"
          onClick={() => navigate("/tenders")}
          className="mt-4"
        >
          Return to Tenders
        </Button>
      </div>
    );
  }

  const filteredBidders = bidders.filter((b) =>
    b.name.toLowerCase().includes(search.toLowerCase()) ||
    b.id.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Back button & Title */}
      <div className="space-y-2 border-b border-outline-variant/40 pb-4">
        <button
          onClick={() => navigate("/tenders")}
          className="inline-flex items-center gap-1 text-xs text-primary font-semibold hover:underline"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Tenders
        </button>

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div>
            <div className="text-xs font-mono text-on-surface-variant">
              {tender.id}
            </div>
            <h1 className="text-2xl font-bold text-on-surface">{tender.name}</h1>
            <p className="text-xs text-on-surface-variant mt-0.5">
              {tender.department || "Department not supplied"} · {tender.requirements?.length || 0} extracted requirements
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <select
              value={selectedBidderId}
              onChange={(event) => setSelectedBidderId(event.target.value)}
              disabled={linking}
              className="px-2.5 py-1.5 text-xs rounded border border-outline-variant bg-surface-container-lowest text-on-surface focus:outline-none focus:border-primary max-w-52"
            >
              <option value="">Link uploaded bidder…</option>
              {availableBidders
                .filter((bidder) => bidder.tenderId === "N/A" || bidder.tenderId === decodedId)
                .map((bidder) => (
                  <option key={bidder.id} value={bidder.id}>{bidder.name} (#{bidder.id})</option>
                ))}
            </select>
            <Button variant="primary" size="sm" disabled={!selectedBidderId || linking} onClick={handleLinkBidder}>
              {linking ? "Linking…" : "Link & Compare"}
            </Button>
            <Button
              variant="outline"
              size="sm"
              icon={RefreshCw}
              disabled={rechecking}
              onClick={handleRefreshAndRecheck}
            >
              {rechecking ? "Rechecking…" : "Refresh & Recheck"}
            </Button>
            <StatusBadge status={tender.status} />
          </div>
        </div>
      </div>

      {/* Summary KPIs */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <KPICard
          label="Total Bids"
          value={tender.totalBids}
          icon={FileCheck}
          iconColor="text-primary"
        />
        <KPICard
          label="Verified"
          value={tender.verified}
          icon={FileCheck}
          iconColor="text-green-700"
        />
        <KPICard
          label="Under Review"
          value={tender.underReview}
          icon={AlertTriangle}
          iconColor="text-amber-600"
        />
        <KPICard
          label="Flagged"
          value={tender.flagged}
          icon={Shield}
          iconColor="text-red-600"
        />
      </div>

      {/* Bidders Table */}
      <div className="bg-surface-container-lowest border border-outline-variant/60 rounded-lg overflow-hidden">
        <div className="p-4 border-b border-outline-variant/50 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-surface-container-low">
          <div>
            <h3 className="text-base font-bold text-on-surface">
              Participating Bidders
            </h3>
            <p className="text-xs text-on-surface-variant">
              Click on any bidder to open the dedicated Bid Verification Workspace
            </p>
          </div>

          <div className="relative">
            <Search className="w-3.5 h-3.5 text-outline absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search bidder..."
              className="pl-8 pr-3 py-1.5 text-xs rounded border border-outline-variant bg-surface-container-lowest text-on-surface focus:outline-none focus:border-primary w-48"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead className="bg-[#F1F5F9] text-xs font-semibold text-on-surface-variant uppercase tracking-wider border-b border-outline-variant/50">
              <tr>
                <th className="px-5 py-3">Bidder Entity</th>
                <th className="px-5 py-3">Documents</th>
                <th className="px-5 py-3">Compliance Score</th>
                <th className="px-5 py-3">Issues</th>
                <th className="px-5 py-3">Risk Level</th>
                <th className="px-5 py-3">Status</th>
                <th className="px-5 py-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="text-xs divide-y divide-outline-variant/30 bg-surface-container-lowest">
              {filteredBidders.map((b) => (
                <tr
                  key={b.id}
                  onClick={() => navigate(`/bids/${b.id}`)}
                  className="hover:bg-surface-container-low transition-colors group cursor-pointer"
                >
                  <td className="px-5 py-3.5">
                    <div className="font-bold text-on-surface group-hover:text-primary transition-colors">
                      {b.name}
                    </div>
                    <div className="text-[11px] text-on-surface-variant font-mono">
                      {b.id}
                    </div>
                  </td>
                  <td className="px-5 py-3.5 text-on-surface-variant font-medium">
                    {b.documentsSubmitted}/{b.documentsTotal}
                  </td>
                  <td className="px-5 py-3.5">
                    <span className="font-bold text-on-surface">
                      {b.complianceScore}
                    </span>
                    <span className="text-[10px] text-on-surface-variant">/100</span>
                  </td>
                  <td className="px-5 py-3.5 font-medium">
                    {b.issueCount > 0 ? (
                      <span className="text-amber-800 font-bold">
                        {b.issueCount} {b.issueCount === 1 ? "issue" : "issues"}
                      </span>
                    ) : (
                      <span className="text-green-700 font-semibold">0 issues</span>
                    )}
                  </td>
                  <td className="px-5 py-3.5">
                    <RiskBadge risk={b.risk} />
                  </td>
                  <td className="px-5 py-3.5">
                    <StatusBadge status={b.status} size="sm" />
                  </td>
                  <td className="px-5 py-3.5 text-right">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/bids/${b.id}`);
                      }}
                      icon={ChevronRight}
                    >
                      Verify
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
