import { useState } from "react";
import { Navigate, Outlet } from "react-router-dom";
import BidderSidebar from "./BidderSidebar";
import BidderTopbar from "./BidderTopbar";

export default function BidderLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Check bidder auth
  const isBidderAuth = localStorage.getItem("gem_rakshak_bidder_auth");

  if (!isBidderAuth) {
    return <Navigate to="/bidder/login" replace />;
  }

  return (
    <div className="min-h-dvh bg-surface flex">
      <BidderSidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <div className="flex-1 flex flex-col lg:ml-[280px] min-h-dvh">
        <BidderTopbar onMenuClick={() => setSidebarOpen(true)} />

        <main className="flex-1 overflow-y-auto p-4 lg:p-6 max-w-[1440px] mx-auto w-full">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
