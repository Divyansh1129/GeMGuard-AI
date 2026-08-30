import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Gavel, FileText, CheckCircle2, AlertTriangle, ArrowUpRight } from "lucide-react";
import KPICard from "../components/common/KPICard";
import VerificationChart from "../components/dashboard/VerificationChart";
import RecentBidsTable from "../components/dashboard/RecentBidsTable";
import tenderService from "../services/tenderService";
import bidderService from "../services/bidderService";

export default function Dashboard() {
  const navigate = useNavigate();
  const [tenders, setTenders] = useState([]);
  const [bids, setBids] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      const allTenders = await tenderService.getAll();
      const allBids = await bidderService.getAll();
      setTenders(allTenders);
      setBids(allBids);
      setLoading(false);
    }
    loadData();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline-variant/40 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-on-surface">
            Procurement Dashboard
          </h1>
          <p className="text-xs text-on-surface-variant mt-0.5">
            Real-time compliance monitoring and bid verification queue overview.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => navigate("/tenders")}
            className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-primary-container text-on-primary-container hover:bg-primary-container/80 transition-colors flex items-center gap-1"
          >
            <span>View All Tenders</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* KPI Cards Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          label="Active Tenders"
          value={tenders.length}
          subtitle="Live backend records"
          icon={Gavel}
          iconColor="text-primary"
          onClick={() => navigate("/tenders")}
        />
        <KPICard
          label="Total Bids"
          value={bids.length}
          subtitle="Live bidder records"
          icon={FileText}
          iconColor="text-secondary"
        />
        <KPICard
          label="Verified Bids"
          value={bids.filter((bid) => bid.status === "Verified").length}
          subtitle="Evidence checks passed"
          icon={CheckCircle2}
          iconColor="text-green-700"
        />
        <KPICard
          label="Needs Review"
          value={bids.filter((bid) => bid.status === "Review Required" || bid.status === "Non-Compliant").length}
          subtitle="Requires officer action"
          icon={AlertTriangle}
          iconColor="text-amber-600"
          onClick={() => navigate("/verification")}
        />
      </div>

      {/* Main Grid: Chart + Recent Bids */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
        <div className="lg:col-span-4">
          <VerificationChart verified={bids.filter((bid) => bid.status === "Verified").length} review={bids.filter((bid) => bid.status === "Review Required").length} nonCompliant={bids.filter((bid) => bid.status === "Non-Compliant").length} />
        </div>
        <div className="lg:col-span-8">
          <RecentBidsTable bids={bids} />
        </div>
      </div>
    </div>
  );
}
