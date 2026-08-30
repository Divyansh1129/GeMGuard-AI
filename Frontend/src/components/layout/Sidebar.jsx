import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  Gavel,
  ClipboardCheck,
  FileText,
  Settings,
  LogOut,
  ChevronLeft,
  Shield,
  X,
} from "lucide-react";

const navItems = [
  { to: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/tenders", icon: Gavel, label: "Tenders" },
  { to: "/verification", icon: ClipboardCheck, label: "Verification Queue" },
  { to: "/reports", icon: FileText, label: "Reports" },
];

const bottomItems = [
  { to: "/settings", icon: Settings, label: "Settings" },
];

export default function Sidebar({ isOpen, onClose }) {
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem("gem_rakshak_auth");
    navigate("/login");
  };

  const sidebarWidth = collapsed ? "w-[72px]" : "w-[280px]";

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

        {/* Officer Profile */}
        {!collapsed && (
          <div className="flex items-center gap-3 p-4 mx-3 mt-3 rounded-lg bg-surface-container">
            <div className="w-10 h-10 rounded-full bg-primary-container flex items-center justify-center text-on-primary-container font-bold text-sm shrink-0">
              OP
            </div>
            <div className="flex flex-col min-w-0">
              <span className="text-sm font-semibold text-on-surface truncate">
                Compliance Officer
              </span>
            </div>
          </div>
        )}

        {/* Navigation */}
        <nav className="flex-1 flex flex-col gap-1 p-3 mt-2">
          <span className="text-[11px] font-semibold text-on-surface-variant uppercase tracking-wider px-3 mb-1">
            {!collapsed && "Navigation"}
          </span>
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${isActive
                  ? "bg-primary-container text-on-primary-container font-bold"
                  : "text-on-surface-variant hover:bg-surface-container-high"
                }`
              }
            >
              <item.icon className="w-5 h-5 shrink-0" />
              {!collapsed && <span>{item.label}</span>}
            </NavLink>
          ))}
        </nav>

        {/* Bottom */}
        <div className="p-3 border-t border-outline-variant space-y-1.5">
          {bottomItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${isActive
                  ? "bg-primary-container text-on-primary-container font-bold"
                  : "text-on-surface-variant hover:bg-surface-container-high"
                }`
              }
            >
              <item.icon className="w-5 h-5 shrink-0" />
              {!collapsed && <span>{item.label}</span>}
            </NavLink>
          ))}

          <button
            onClick={() => navigate("/bidder/dashboard")}
            className="flex items-center justify-between px-3 py-2 rounded-lg text-xs font-semibold text-on-surface-variant bg-surface-container-low hover:bg-surface-container border border-outline-variant/60 w-full transition-colors"
          >
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-primary shrink-0" />
              {!collapsed && <span>Bidder Portal</span>}
            </div>
          </button>

          <button
            onClick={handleLogout}
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-error hover:bg-error-container/30 w-full transition-all duration-200"
          >
            <LogOut className="w-5 h-5 shrink-0" />
            {!collapsed && <span>Logout</span>}
          </button>
        </div>
      </aside>
    </>
  );
}
