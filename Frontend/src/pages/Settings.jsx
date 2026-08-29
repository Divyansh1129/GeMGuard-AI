import React, { useState } from "react";
import { User, Shield, Bell, CheckCircle, Save, Sliders, AlertCircle, FileCheck, Key } from "lucide-react";
import Button from "../components/common/Button";
import { showToast } from "../components/common/Toast";

export default function Settings() {
  const [officerName, setOfficerName] = useState("Rajesh Varma");
  const [department, setDepartment] = useState("Ministry of Petroleum & Natural Gas");
  const [officerId, setOfficerId] = useState("88294-GOV");
  const [email, setEmail] = useState("officer@gem.gov.in");

  // Officer Verification Threshold Settings
  const [minOcrConfidence, setMinOcrConfidence] = useState(85);
  const [strictNameMatching, setStrictNameMatching] = useState(true);
  const [autoFlagBlacklist, setAutoFlagBlacklist] = useState(true);
  const [emailAlerts, setEmailAlerts] = useState(true);
  const [clarificationSlaHours, setClarificationSlaHours] = useState(48);

  const handleSave = (e) => {
    e.preventDefault();
    showToast("✓ Officer settings saved successfully", "success");
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div className="border-b border-outline-variant/40 pb-4">
        <h1 className="text-2xl font-bold text-on-surface">
          Platform Settings & Configuration
        </h1>
        <p className="text-xs text-on-surface-variant mt-0.5">
          Manage officer credentials, compliance verification thresholds, and notification rules.
        </p>
      </div>

      {/* Officer Profile Form */}
      <div className="bg-surface-container-lowest border border-outline-variant/60 rounded-lg p-6 space-y-4">
        <div className="flex items-center gap-2.5 pb-2 border-b border-outline-variant/40">
          <User className="w-5 h-5 text-primary" />
          <h3 className="text-sm font-bold text-on-surface uppercase tracking-wide">
            Officer Profile Details
          </h3>
        </div>

        <form onSubmit={handleSave} className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div>
            <label className="block font-bold text-on-surface-variant uppercase mb-1">
              Officer Full Name
            </label>
            <input
              type="text"
              value={officerName}
              onChange={(e) => setOfficerName(e.target.value)}
              className="w-full px-3 py-2 rounded border border-outline-variant bg-surface-container-lowest text-on-surface focus:outline-none focus:border-primary"
            />
          </div>

          <div>
            <label className="block font-bold text-on-surface-variant uppercase mb-1">
              Government Officer ID
            </label>
            <input
              type="text"
              disabled
              value={officerId}
              className="w-full px-3 py-2 rounded border border-outline-variant bg-surface-container text-on-surface-variant cursor-not-allowed font-mono"
            />
          </div>

          <div>
            <label className="block font-bold text-on-surface-variant uppercase mb-1">
              Official Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 rounded border border-outline-variant bg-surface-container-lowest text-on-surface focus:outline-none focus:border-primary"
            />
          </div>

          <div>
            <label className="block font-bold text-on-surface-variant uppercase mb-1">
              Designated Ministry / Department
            </label>
            <input
              type="text"
              value={department}
              onChange={(e) => setDepartment(e.target.value)}
              className="w-full px-3 py-2 rounded border border-outline-variant bg-surface-container-lowest text-on-surface focus:outline-none focus:border-primary"
            />
          </div>

          <div className="sm:col-span-2 pt-2">
            <Button type="submit" variant="primary" size="sm" icon={Save}>
              Save Profile Changes
            </Button>
          </div>
        </form>
      </div>

      {/* Compliance Rule & Verification Engine Thresholds */}
      <div className="bg-surface-container-lowest border border-outline-variant/60 rounded-lg p-6 space-y-4">
        <div className="flex items-center gap-2.5 pb-2 border-b border-outline-variant/40">
          <Sliders className="w-5 h-5 text-primary" />
          <h3 className="text-sm font-bold text-on-surface uppercase tracking-wide">
            Automated Rule Engine Thresholds
          </h3>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="p-4 rounded-lg bg-surface-container-low border border-outline-variant/50 space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-bold text-on-surface">Min OCR Extraction Confidence</span>
              <span className="font-mono font-bold text-primary">{minOcrConfidence}%</span>
            </div>
            <input
              type="range"
              min="70"
              max="99"
              value={minOcrConfidence}
              onChange={(e) => setMinOcrConfidence(Number(e.target.value))}
              className="w-full accent-primary"
            />
            <p className="text-[11px] text-on-surface-variant">
              Documents below this score will trigger mandatory manual officer review.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-surface-container-low border border-outline-variant/50 space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-bold text-on-surface">Clarification Response SLA</span>
              <span className="font-mono font-bold text-primary">{clarificationSlaHours} Hours</span>
            </div>
            <select
              value={clarificationSlaHours}
              onChange={(e) => setClarificationSlaHours(Number(e.target.value))}
              className="w-full px-2 py-1.5 rounded border border-outline-variant bg-surface-container-lowest text-xs text-on-surface"
            >
              <option value={24}>24 Hours (Fast track)</option>
              <option value={48}>48 Hours (Standard)</option>
              <option value={72}>72 Hours (Extended)</option>
            </select>
            <p className="text-[11px] text-on-surface-variant">
              Default window given to bidders for responding to clarification requests.
            </p>
          </div>

          <div className="sm:col-span-2 space-y-3 pt-2">
            <label className="flex items-center gap-3 p-3 rounded-lg bg-surface-container-low border border-outline-variant/50 cursor-pointer">
              <input
                type="checkbox"
                checked={strictNameMatching}
                onChange={(e) => setStrictNameMatching(e.target.checked)}
                className="w-4 h-4 rounded text-primary accent-primary"
              />
              <div>
                <span className="font-bold text-on-surface block">Strict Multi-Registry Name Verification</span>
                <span className="text-[11px] text-on-surface-variant">
                  Flag any character or entity suffix discrepancy between PAN, GSTIN, and EPFO as Medium Risk.
                </span>
              </div>
            </label>

            <label className="flex items-center gap-3 p-3 rounded-lg bg-surface-container-low border border-outline-variant/50 cursor-pointer">
              <input
                type="checkbox"
                checked={autoFlagBlacklist}
                onChange={(e) => setAutoFlagBlacklist(e.target.checked)}
                className="w-4 h-4 rounded text-primary accent-primary"
              />
              <div>
                <span className="font-bold text-on-surface block">Automatic Central Blacklist Lookup</span>
                <span className="text-[11px] text-on-surface-variant">
                  Auto-cross check directors and PAN numbers against Ministry debarment databases.
                </span>
              </div>
            </label>

            <label className="flex items-center gap-3 p-3 rounded-lg bg-surface-container-low border border-outline-variant/50 cursor-pointer">
              <input
                type="checkbox"
                checked={emailAlerts}
                onChange={(e) => setEmailAlerts(e.target.checked)}
                className="w-4 h-4 rounded text-primary accent-primary"
              />
              <div>
                <span className="font-bold text-on-surface block">Immediate Officer Notifications</span>
                <span className="text-[11px] text-on-surface-variant">
                  Receive email alerts when a bidder submits corrected clarification documents.
                </span>
              </div>
            </label>
          </div>
        </div>
      </div>
    </div>
  );
}
