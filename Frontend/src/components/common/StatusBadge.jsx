import React from "react";
import { CheckCircle, AlertTriangle, XCircle, Clock, ShieldAlert } from "lucide-react";

export default function StatusBadge({ status, className = "", size = "md" }) {
  const normStatus = (status || "").toLowerCase().trim();

  let styles = "bg-surface-container text-on-surface-variant border-outline-variant";
  let Icon = Clock;
  let label = status || "Pending";

  if (normStatus === "verified" || normStatus === "approved" || normStatus === "active") {
    styles = "bg-green-50 text-green-700 border-green-200";
    Icon = CheckCircle;
    label = normStatus === "active" ? "Active" : "Verified";
  } else if (
    normStatus === "review required" ||
    normStatus === "review" ||
    normStatus === "under review" ||
    normStatus === "evaluation"
  ) {
    styles = "bg-amber-50 text-amber-700 border-amber-200";
    Icon = AlertTriangle;
    label = normStatus === "evaluation" ? "Evaluation" : "Review Required";
  } else if (
    normStatus === "non-compliant" ||
    normStatus === "flagged" ||
    normStatus === "rejected" ||
    normStatus === "closed"
  ) {
    styles = "bg-red-50 text-red-700 border-red-200";
    Icon = normStatus === "closed" ? Clock : XCircle;
    label = normStatus === "closed" ? "Closed" : normStatus === "flagged" ? "Flagged" : "Non-Compliant";
  }

  const sizeClass = size === "sm" ? "px-2 py-0.5 text-xs gap-1" : "px-2.5 py-1 text-xs gap-1.5";

  return (
    <span
      className={`inline-flex items-center font-semibold rounded-full border ${styles} ${sizeClass} ${className}`}
    >
      <Icon className="w-3.5 h-3.5 shrink-0" />
      <span>{label}</span>
    </span>
  );
}
