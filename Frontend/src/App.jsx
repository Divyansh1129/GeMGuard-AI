import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import AppLayout from "./components/layout/AppLayout";
import BidderLayout from "./components/bidder/BidderLayout";
import Toast from "./components/common/Toast";

// Officer Portal Pages
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Tenders from "./pages/Tenders";
import TenderDetails from "./pages/TenderDetails";
import BidderVerification from "./pages/BidderVerification";
import DocumentReview from "./pages/DocumentReview";
import VerificationQueue from "./pages/VerificationQueue";
import Reports from "./pages/Reports";
import Settings from "./pages/Settings";

// Bidder Portal Pages
import BidderLogin from "./pages/bidder/BidderLogin";
import BidderDashboard from "./pages/bidder/BidderDashboard";
import BidderDocuments from "./pages/bidder/BidderDocuments";
import BidderStatus from "./pages/bidder/BidderStatus";
import BidderProfile from "./pages/bidder/BidderProfile";

export default function App() {
  return (
    <BrowserRouter>
      <Toast />
      <Routes>
        {/* Public Officer Login */}
        <Route path="/login" element={<Login />} />
        <Route path="/officer/login" element={<Login />} />

        {/* Public Bidder Login */}
        <Route path="/bidder/login" element={<BidderLogin />} />

        {/* Protected Bidder Portal Routes */}
        <Route path="/bidder" element={<BidderLayout />}>
          <Route index element={<Navigate to="/bidder/dashboard" replace />} />
          <Route path="dashboard" element={<BidderDashboard />} />
          <Route path="documents" element={<BidderDocuments />} />
          <Route path="status" element={<BidderStatus />} />
          <Route path="profile" element={<BidderProfile />} />
        </Route>

        {/* Protected Officer App Routes */}
        <Route element={<AppLayout />}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/tenders" element={<Tenders />} />
          <Route path="/tenders/:tenderId" element={<TenderDetails />} />
          <Route path="/bids/:bidderId" element={<BidderVerification />} />
          <Route
            path="/bids/:bidderId/documents/:documentId"
            element={<DocumentReview />}
          />
          <Route path="/verification" element={<VerificationQueue />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/settings" element={<Settings />} />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
