import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  UploadCloud,
  FileCheck2,
  Building2,
  LogOut,
  Shield,
  X,
  ExternalLink,
  AlertCircle,
} from "lucide-react";
import bidderStore from "../../services/bidderStore";

const navItems = [
  { to: "/bidder/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/bidder/documents", icon: UploadCloud, label: "Documents" },
  { to: "/bidder/status", icon: FileCheck2, label: "Submission Status" },
  { to: "/bidder/profile", icon: Building2, label: "Company Profile" },
];

export default function BidderSidebar({ isOpen, onClose }) {
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);
  const state = bidderStore.getState();

  const handleLogout = () => {
    localStorage.removeItem("gem_rakshak_bidder_auth");
    navigate("/bidder/login");
  };

  const sidebarWidth = collapsed ? "w-[72px]" : "w-[280px]";

  const hasClarification = state.documents?.some(
    (d) => d.status === "Clarification Required"
  );

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/30 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-50 flex flex-col bg-surface-container-lowest border-r border-outline-variant transition-all duration-300 ${sidebarWidth} ${isOpen ? "translate-x-0" : "-translate-x-full"
          } lg:translate-x-0`}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-outline-variant">
          <div className="flex items-center gap-3 min-w-0">
            <img src="/gemguard-logo.png" alt="GemGuard AI" className="w-10 h-10 object-contain shrink-0" />
            {!collapsed && (
              <div className="flex flex-col min-w-0">
                <span className="text-base font-bold text-primary tracking-tight truncate">
                  GeMGuard AI
                </span>
              </div>
            )}
          </div>
          <button
            onClick={onClose}
            className="lg:hidden p-1 rounded hover:bg-surface-container-high"
          >
            <X className="w-5 h-5 text-on-surface-variant" />
          </button>
        </div>

        {/* Bidder Profile Card */}
        {!collapsed && (
          <div className="p-3 mx-3 mt-3 rounded-lg bg-surface-container border border-outline-variant/60">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-full bg-primary-container flex items-center justify-center text-on-primary-container font-bold text-xs shrink-0">
                AT
              </div>
              <div className="flex flex-col min-w-0">
                <span className="text-xs font-bold text-on-surface truncate">
                  {state.bidderName}
                </span>
                <span className="text-[11px] font-mono text-on-surface-variant truncate">
                  Bid ID: {state.bidId}
                </span>
              </div>
            </div>
            <div className="mt-2 pt-2 border-t border-outline-variant/40 flex items-center justify-between text-[10px]">
              <span className="text-on-surface-variant truncate">Tender: {state.tenderId || "Not linked"}</span>
            </div>
          </div>
        )}

        {/* Navigation */}
        <nav className="flex-1 flex flex-col gap-1 p-3 mt-1">
          <span className="text-[11px] font-semibold text-on-surface-variant uppercase tracking-wider px-3 mb-1">
            {!collapsed && "Bidder Workspace"}
          </span>
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${isActive
                  ? "bg-primary-container text-on-primary-container font-bold"
                  : "text-on-surface-variant hover:bg-surface-container-high"
                }`
              }
            >
              <div className="flex items-center gap-3">
                <item.icon className="w-5 h-5 shrink-0" />
                {!collapsed && <span>{item.label}</span>}
              </div>
              {!collapsed && item.to === "/bidder/documents" && hasClarification && (
                <span className="w-2 h-2 rounded-full bg-amber-500 animate-ping" />
              )}
            </NavLink>
          ))}
        </nav>

        {/* Clarification notification pill if active */}
        {!collapsed && hasClarification && (
          <div className="mx-3 mb-3 p-2.5 rounded-lg bg-amber-50 border border-amber-200 text-amber-900 text-xs">
            <div className="flex items-center gap-1.5 font-bold mb-1">
              <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
              <span>Action Required</span>
            </div>
            <p className="text-[11px] text-amber-800 leading-tight">
              Officer requested clarification on OEM authorization.
            </p>
          </div>
        )}

        {/* Bottom Switch Portal & Logout */}
        <div className="p-3 border-t border-outline-variant space-y-1.5">
          <button
            onClick={() => navigate("/login")}
            className="flex items-center justify-between px-3 py-2 rounded-lg text-xs font-semibold text-on-surface-variant bg-surface-container-low hover:bg-surface-container border border-outline-variant/60 w-full transition-colors"
          >
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-primary shrink-0" />
              {!collapsed && <span>Officer Portal</span>}
            </div>
            {!collapsed && <ExternalLink className="w-3.5 h-3.5 opacity-60" />}
          </button>

          <button
            onClick={handleLogout}
            className="flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium text-error hover:bg-error-container/30 w-full transition-all duration-200"
          >
            <LogOut className="w-4 h-4 shrink-0" />
            {!collapsed && <span>Sign Out</span>}
          </button>
        </div>
      </aside>
    </>
  );
}
