import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Search, Gavel, Calendar, ArrowRight, Filter, Upload } from "lucide-react";
import StatusBadge from "../components/common/StatusBadge";
import Button from "../components/common/Button";
import tenderService from "../services/tenderService";

export default function Tenders() {
  const navigate = useNavigate();
  const [tenders, setTenders] = useState([]);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");
  const [uploading, setUploading] = useState(false);

  const uploadTender = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const tender = await tenderService.upload({ name: file.name.replace(/\.[^.]+$/, ""), file });
      setTenders((current) => [tender, ...current]);
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  };

  useEffect(() => {
    async function load() {
      const data = await tenderService.getAll();
      setTenders(data);
    }
    load();
  }, []);

  const filtered = tenders.filter((t) => {
    const matchSearch =
      t.name.toLowerCase().includes(search.toLowerCase()) ||
      t.id.toLowerCase().includes(search.toLowerCase()) ||
      t.department.toLowerCase().includes(search.toLowerCase());
    const matchStatus = statusFilter === "All" || t.status === statusFilter;
    return matchSearch && matchStatus;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline-variant/40 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-on-surface">Tenders</h1>
          <p className="text-xs text-on-surface-variant mt-0.5">
            Active GeM procurement tenders undergoing compliance verification.
          </p>
        </div>

        {/* Search & Filter */}
        <div className="flex flex-wrap items-center gap-2">
          <label className="px-3 py-1.5 text-xs font-semibold rounded border border-outline-variant bg-surface-container-lowest text-on-surface cursor-pointer flex items-center gap-1">
            <Upload className="w-3.5 h-3.5" /> {uploading ? "Extracting…" : "Upload Tender"}
            <input type="file" accept=".pdf,.png,.jpg,.jpeg" onChange={uploadTender} disabled={uploading} className="hidden" />
          </label>
          <div className="relative">
            <Search className="w-4 h-4 text-outline absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search tender ID or name..."
              className="pl-9 pr-3 py-1.5 text-xs rounded border border-outline-variant bg-surface-container-lowest text-on-surface placeholder:text-outline focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary w-48 sm:w-64"
            />
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-1.5 text-xs rounded border border-outline-variant bg-surface-container-lowest text-on-surface focus:outline-none focus:border-primary cursor-pointer"
          >
            <option value="All">All Statuses</option>
            <option value="Active">Active</option>
            <option value="Evaluation">Evaluation</option>
            <option value="Closed">Closed</option>
          </select>
        </div>
      </div>

      {/* Tenders Table */}
      <div className="bg-surface-container-lowest border border-outline-variant/60 rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead className="bg-[#F1F5F9] text-xs font-semibold text-on-surface-variant uppercase tracking-wider border-b border-outline-variant/50">
              <tr>
                <th className="px-5 py-3.5">Tender Details</th>
                <th className="px-5 py-3.5">Department</th>
                <th className="px-5 py-3.5">Est. Value</th>
                <th className="px-5 py-3.5">Deadline</th>
                <th className="px-5 py-3.5">Bids Summary</th>
                <th className="px-5 py-3.5">Status</th>
                <th className="px-5 py-3.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="text-xs divide-y divide-outline-variant/30 bg-surface-container-lowest">
              {filtered.map((t) => (
                <tr
                  key={t.id}
                  onClick={() => navigate(`/tenders/${encodeURIComponent(t.id)}`)}
                  className="hover:bg-surface-container-low transition-colors group cursor-pointer"
                >
                  <td className="px-5 py-4">
                    <div className="font-bold text-on-surface group-hover:text-primary transition-colors">
                      {t.name}
                    </div>
                    <div className="text-[11px] text-on-surface-variant font-mono mt-0.5">
                      {t.id}
                    </div>
                  </td>
                  <td className="px-5 py-4 text-on-surface-variant font-medium">
                    {t.department}
                  </td>
                  <td className="px-5 py-4 font-bold text-on-surface">
                    {t.value}
                  </td>
                  <td className="px-5 py-4 text-on-surface-variant font-mono">
                    {t.deadline}
                  </td>
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-1.5 text-[11px]">
                      <span className="font-bold text-on-surface">
                        {t.totalBids} total
                      </span>
                      <span className="text-on-surface-variant">·</span>
                      <span className="text-green-700 font-semibold">
                        {t.verified} ok
                      </span>
                      <span className="text-on-surface-variant">·</span>
                      <span className="text-amber-700 font-semibold">
                        {t.underReview} rev
                      </span>
                    </div>
                  </td>
                  <td className="px-5 py-4">
                    <StatusBadge status={t.status} size="sm" />
                  </td>
                  <td className="px-5 py-4 text-right">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/tenders/${encodeURIComponent(t.id)}`);
                      }}
                      icon={ArrowRight}
                    >
                      Open
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
