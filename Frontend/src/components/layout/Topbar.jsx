import { Bell, Search, Menu } from "lucide-react";

export default function Topbar({ onMenuClick }) {
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
        <div className="hidden md:flex items-center relative">
          <Search className="w-4 h-4 absolute left-3 text-outline" />
          <input
            type="text"
            placeholder="Search tenders, bidders..."
            className="pl-9 pr-4 py-2 w-72 rounded-lg border border-outline-variant bg-surface-container-lowest text-sm text-on-surface placeholder:text-outline focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all"
          />
        </div>
      </div>

      <div className="flex items-center gap-2">
        <button
          className="relative p-2 rounded-lg hover:bg-surface-container-high text-on-surface-variant transition-colors"
          aria-label="Notifications"
        >
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-error rounded-full" />
        </button>
        <div className="hidden md:flex items-center gap-2 bg-surface-container-low rounded-full px-3 py-1.5 border border-outline-variant ml-1">
          <div className="w-7 h-7 rounded-full bg-primary-container flex items-center justify-center text-on-primary-container font-bold text-xs">
            OP
          </div>
          <div className="flex flex-col">
            <span className="text-xs font-semibold text-on-surface leading-tight">
              Officer Profile
            </span>
            <span className="text-[10px] text-on-surface-variant leading-tight">
              Procurement
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
