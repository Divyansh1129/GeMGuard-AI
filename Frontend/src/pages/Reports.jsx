import React from "react";
import { FileText, Download, BarChart3, PieChart, ShieldCheck, Printer } from "lucide-react";
import Button from "../components/common/Button";
import KPICard from "../components/common/KPICard";
import { showToast } from "../components/common/Toast";

export default function Reports() {
  const handleExport = (format) => {
    showToast(`✓ Official Compliance Report (${format}) generated successfully.`, "success");
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-outline-variant/40 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-on-surface">
            Compliance & Audit Reports
          </h1>
          <p className="text-xs text-on-surface-variant mt-0.5">
            Official executive intelligence and audit dossiers for GeM procurement oversight.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleExport("Excel")}
            icon={Download}
          >
            Export Excel
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={() => handleExport("PDF")}
            icon={Printer}
          >
            Generate Official PDF
          </Button>
        </div>
      </div>

      {/* KPI Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <KPICard
          label="Total Bids Evaluated"
          value="186"
          subtitle="FY 2026-27"
          icon={FileText}
          iconColor="text-primary"
        />
        <KPICard
          label="Automated Pass Rate"
          value="76.3%"
          subtitle="142 verified compliant"
          icon={ShieldCheck}
          iconColor="text-green-700"
        />
        <KPICard
          label="Avg Verification Time"
          value="2.4 min"
          subtitle="Down from 4.5 days manual"
          icon={BarChart3}
          iconColor="text-primary"
        />
        <KPICard
          label="Discrepancy Catch Rate"
          value="99.4%"
          subtitle="Central database cross-checked"
          icon={PieChart}
          iconColor="text-amber-600"
        />
      </div>

      {/* Report Visualizations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Compliance Distribution Card */}
        <div className="bg-surface-container-lowest border border-outline-variant/60 rounded-lg p-5 space-y-4">
          <h3 className="text-sm font-bold text-on-surface uppercase tracking-wide border-b border-outline-variant/40 pb-2">
            Compliance Score Distribution
          </h3>
          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-xs font-medium mb-1">
                <span>High Compliance (90 - 100)</span>
                <span className="font-bold">142 bids (76%)</span>
              </div>
              <div className="w-full bg-surface-container rounded-full h-2">
                <div className="bg-green-600 h-2 rounded-full w-[76%]" />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-medium mb-1">
                <span>Moderate Compliance (75 - 89)</span>
                <span className="font-bold">31 bids (17%)</span>
              </div>
              <div className="w-full bg-surface-container rounded-full h-2">
                <div className="bg-amber-500 h-2 rounded-full w-[17%]" />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-medium mb-1">
                <span>Non-Compliant (&lt; 75)</span>
                <span className="font-bold">13 bids (7%)</span>
              </div>
              <div className="w-full bg-surface-container rounded-full h-2">
                <div className="bg-red-600 h-2 rounded-full w-[7%]" />
              </div>
            </div>
          </div>
        </div>

        {/* Common Issue Types */}
        <div className="bg-surface-container-lowest border border-outline-variant/60 rounded-lg p-5 space-y-4">
          <h3 className="text-sm font-bold text-on-surface uppercase tracking-wide border-b border-outline-variant/40 pb-2">
            Most Common Verification Flags
          </h3>
          <div className="space-y-3 text-xs">
            <div className="flex items-center justify-between p-2 rounded bg-surface-container-low">
              <span className="font-medium">Entity Legal Name Variation (ESIC/EPFO vs PAN)</span>
              <span className="font-bold text-amber-800">42% of flags</span>
            </div>
            <div className="flex items-center justify-between p-2 rounded bg-surface-container-low">
              <span className="font-medium">OEM Authorization Letter Mismatch</span>
              <span className="font-bold text-red-800">28% of flags</span>
            </div>
            <div className="flex items-center justify-between p-2 rounded bg-surface-container-low">
              <span className="font-medium">GST Validity or Tax Filing Gap</span>
              <span className="font-bold text-amber-800">18% of flags</span>
            </div>
            <div className="flex items-center justify-between p-2 rounded bg-surface-container-low">
              <span className="font-medium">Expired Udyam / MSME Registration</span>
              <span className="font-bold text-on-surface-variant">12% of flags</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
