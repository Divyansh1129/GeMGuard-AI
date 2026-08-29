import React from "react";

export default function RiskBadge({ risk = "Low", className = "" }) {
  const normRisk = (risk || "low").toLowerCase();

  const configs = {
    low: {
      bg: "bg-green-50 text-green-700 border-green-200",
      dot: "bg-green-600",
      label: "Low Risk",
    },
    medium: {
      bg: "bg-amber-50 text-amber-700 border-amber-200",
      dot: "bg-amber-600",
      label: "Medium Risk",
    },
    high: {
      bg: "bg-red-50 text-red-700 border-red-200",
      dot: "bg-red-600",
      label: "High Risk",
    },
  };

  const config = configs[normRisk] || configs.low;

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${config.bg} ${className}`}
    >
      <span className={`w-2 h-2 rounded-full ${config.dot}`} />
      <span>{config.label}</span>
    </span>
  );
}
