import React from "react";
import { Clock, CheckCircle, AlertTriangle, Bot, Shield, User } from "lucide-react";

export default function AuditTrail({ logs = [] }) {
  return (
    <div className="bg-surface-container-lowest border border-outline-variant/60 rounded-lg p-5">
      <div className="flex items-center justify-between mb-4 border-b border-outline-variant/40 pb-3">
        <div>
          <h3 className="text-sm font-bold text-on-surface uppercase tracking-wide">
            Audit Trail & Timeline
          </h3>
          <p className="text-xs text-on-surface-variant">
            Immutable log of all automated verification and human officer actions
          </p>
        </div>
        <span className="text-xs font-semibold px-2 py-0.5 rounded bg-surface-container text-on-surface-variant">
          {logs.length} Events
        </span>
      </div>

      <div className="relative pl-6 space-y-4 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-outline-variant/50">
        {logs.map((log, idx) => {
          const isAI = log.type === "ai";
          const isWarning = log.type === "warning";
          const isOfficer = log.actor?.toLowerCase().includes("officer");

          return (
            <div key={log.id || idx} className="relative group">
              {/* Dot */}
              <div
                className={`absolute -left-[23px] top-1 w-3.5 h-3.5 rounded-full border-2 border-surface-container-lowest flex items-center justify-center ${
                  isOfficer
                    ? "bg-primary text-white"
                    : isWarning
                    ? "bg-amber-500 text-white"
                    : isAI
                    ? "bg-primary-container text-white"
                    : "bg-secondary text-white"
                }`}
              />

              <div className="bg-surface-container-low/40 hover:bg-surface-container-low border border-outline-variant/30 rounded p-2.5 transition-colors">
                <div className="flex items-center justify-between text-[11px] mb-1">
                  <div className="flex items-center gap-1.5">
                    {isOfficer ? (
                      <User className="w-3 h-3 text-primary" />
                    ) : isAI ? (
                      <Bot className="w-3 h-3 text-primary" />
                    ) : (
                      <Shield className="w-3 h-3 text-secondary" />
                    )}
                    <span className="font-bold text-on-surface">{log.actor}</span>
                  </div>
                  <span className="text-on-surface-variant font-mono text-[10px]">
                    {log.timestamp}
                  </span>
                </div>
                <p className="text-xs text-on-surface font-medium leading-relaxed">
                  {log.action}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
