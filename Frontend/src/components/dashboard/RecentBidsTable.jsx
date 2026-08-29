import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Search, ChevronRight, Filter } from "lucide-react";
import StatusBadge from "../common/StatusBadge";

export default function RecentBidsTable({ bids = [] }) {
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");

  const filteredBids = bids.filter((bid) => {
    const matchesSearch =
      bid.name.toLowerCase().includes(search.toLowerCase()) ||
      bid.tenderName.toLowerCase().includes(search.toLowerCase()) ||
      bid.id.toLowerCase().includes(search.toLowerCase());

    const matchesStatus =
      statusFilter === "All" ||
      bid.status.toLowerCase() === statusFilter.toLowerCase();

    return matchesSearch && matchesStatus;
  });

  return (
    <div className="bg-surface-container-lowest border border-outline-variant/60 rounded-lg flex flex-col h-full overflow-hidden">
      <div className="p-5 border-b border-outline-variant/50 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h3 className="text-base font-bold text-on-surface">Recent Bids</h3>
          <p className="text-xs text-on-surface-variant">
            Recently submitted compliance packets requiring action
          </p>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-outline" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search bidder..."
              className="pl-8 pr-3 py-1.5 text-xs rounded border border-outline-variant bg-surface-container-lowest text-on-surface placeholder:text-outline focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary w-32 sm:w-44"
            />
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-2.5 py-1.5 text-xs rounded border border-outline-variant bg-surface-container-lowest text-on-surface focus:outline-none focus:border-primary cursor-pointer"
          >
            <option value="All">All Status</option>
            <option value="Verified">Verified</option>
            <option value="Review Required">Review</option>
            <option value="Non-Compliant">Non-Compliant</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto flex-1">
        <table className="w-full text-left border-collapse">
          <thead className="bg-[#F1F5F9] text-xs font-semibold text-on-surface-variant uppercase tracking-wider border-b border-outline-variant/50">
            <tr>
              <th className="px-5 py-3">Bidder</th>
              <th className="px-5 py-3">Tender</th>
              <th className="px-5 py-3">Documents</th>
              <th className="px-5 py-3">Score</th>
              <th className="px-5 py-3">Status</th>
              <th className="px-5 py-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="text-xs divide-y divide-outline-variant/30 bg-surface-container-lowest">
            {filteredBids.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-5 py-8 text-center text-on-surface-variant">
                  No bids match your search criteria.
                </td>
              </tr>
            ) : (
              filteredBids.map((bid) => (
                <tr
                  key={bid.id}
                  onClick={() => navigate(`/bids/${bid.id}`)}
                  className="hover:bg-surface-container-low transition-colors group cursor-pointer"
                >
                  <td className="px-5 py-3.5">
                    <div className="font-semibold text-on-surface">
                      {bid.name}
                    </div>
                    <div className="text-[11px] text-on-surface-variant font-mono">
                      {bid.id}
                    </div>
                  </td>
                  <td className="px-5 py-3.5 text-on-surface-variant max-w-[180px] truncate">
                    {bid.tenderName}
                  </td>
                  <td className="px-5 py-3.5 text-on-surface-variant font-medium">
                    {bid.documentsSubmitted}/{bid.documentsTotal}
                  </td>
                  <td className="px-5 py-3.5">
                    <span className="font-bold text-on-surface">
                      {bid.complianceScore}
                    </span>
                    <span className="text-on-surface-variant text-[11px]">/100</span>
                  </td>
                  <td className="px-5 py-3.5">
                    <StatusBadge status={bid.status} size="sm" />
                  </td>
                  <td className="px-5 py-3.5 text-right">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/bids/${bid.id}`);
                      }}
                      className="text-primary hover:text-primary-container font-semibold inline-flex items-center gap-0.5 text-xs group-hover:translate-x-0.5 transition-transform"
                    >
                      View
                      <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
