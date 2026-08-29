import { Bell, Menu, Shield, ArrowRight } from "lucide-react";
import { useNavigate } from "react-router-dom";
import bidderStore from "../../services/bidderStore";

export default function BidderTopbar({ onMenuClick }) {
  const navigate = useNavigate();
  const state = bidderStore.getState();
  const hasClarification = state.documents?.some(
    (d) => d.status === "Clarification Required"
  );

  return (
    <header className="sticky top-0 z-30 h-16 bg-surface-container-lowest border-b border-outline-variant flex items-center justify-between px-4 lg:px-6">
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuClick}
          className="lg:hidden p-2 rounded-lg hover:bg-surface-container-high text-on-surface-variant transition-colors"
          aria-label="Toggle menu"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div>
          <div className="flex items-center gap-2">
            <span className="text-sm font-bold text-on-surface">
              {state.bidderName}
            </span>
            <span className="hidden sm:inline-block text-[11px] font-mono px-2 py-0.5 rounded bg-surface-container text-on-surface-variant">
              {state.bidId}
            </span>
          </div>
          <span className="text-[11px] text-on-surface-variant hidden sm:block">
            {state.tenderName} ({state.tenderId})
          </span>
        </div>
      </div>

      <div className="flex items-center gap-2.5">
        {/* Switch Portal Button (Convenient for SIH live evaluation) */}
        <button
          onClick={() => navigate("/dashboard")}
          className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-outline-variant bg-surface-container text-xs font-semibold text-on-surface hover:bg-surface-container-high transition-colors"
        >
          <Shield className="w-3.5 h-3.5 text-primary" />
          <span>Officer View</span>
        </button>

        {/* Notifications */}
        <button
          onClick={() => {
            if (hasClarification) {
              navigate("/bidder/documents");
            }
          }}
          className="relative p-2 rounded-lg hover:bg-surface-container-high text-on-surface-variant transition-colors"
          aria-label="Notifications"
        >
          <Bell className="w-5 h-5" />
          {hasClarification && (
            <span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-amber-500 rounded-full animate-ping" />
          )}
        </button>

        <div className="flex items-center gap-2 bg-surface-container-low rounded-full px-3 py-1.5 border border-outline-variant">
          <div className="w-7 h-7 rounded-full bg-primary-container flex items-center justify-center text-on-primary-container font-bold text-xs">
            AT
          </div>
          <div className="hidden sm:flex flex-col">
            <span className="text-xs font-semibold text-on-surface leading-tight">
              Bidder Profile
            </span>
            <span className="text-[10px] text-on-surface-variant leading-tight">
              ABC Technologies
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
