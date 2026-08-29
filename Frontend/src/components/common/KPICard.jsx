import React from "react";

export default function KPICard({
  label,
  value,
  subtitle,
  icon: Icon,
  iconColor = "text-primary",
  trend,
  progress,
  className = "",
  onClick,
}) {
  return (
    <div
      onClick={onClick}
      className={`bg-surface-container-lowest border border-outline-variant/60 rounded-lg p-5 flex flex-col justify-between hover:border-primary/40 hover:shadow-sm transition-all duration-200 ${
        onClick ? "cursor-pointer" : ""
      } ${className}`}
    >
      <div className="flex items-start justify-between mb-2">
        <span className="text-xs font-semibold text-on-surface-variant uppercase tracking-wider">
          {label}
        </span>
        {Icon && (
          <div className={`p-2 rounded-lg bg-surface-container-low ${iconColor}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>

      <div>
        <div className="text-2xl lg:text-3xl font-bold text-on-surface tracking-tight">
          {value}
        </div>
        {subtitle && (
          <p className="text-xs text-on-surface-variant mt-1.5">{subtitle}</p>
        )}
      </div>

      {progress !== undefined && (
        <div className="w-full bg-surface-container rounded-full h-1.5 mt-3 overflow-hidden">
          <div
            className="bg-primary h-1.5 rounded-full transition-all duration-500"
            style={{ width: `${Math.min(Math.max(progress, 0), 100)}%` }}
          />
        </div>
      )}
    </div>
  );
}
