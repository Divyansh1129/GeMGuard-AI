import React, { useState, useEffect } from "react";
import { Building2, Shield, Save, CheckCircle2, Phone, Mail, MapPin, Hash, FileText } from "lucide-react";
import Button from "../../components/common/Button";
import { showToast } from "../../components/common/Toast";
import bidderStore from "../../services/bidderStore";

export default function BidderProfile() {
  const [state, setState] = useState(bidderStore.getState());
  const [companyName, setCompanyName] = useState(state.bidderName);
  const [gstin, setGstin] = useState(state.gstin);
  const [pan, setPan] = useState(state.pan);
  const [udyamNumber, setUdyamNumber] = useState(state.udyamNumber);
  const [tenderId, setTenderId] = useState(state.tenderId === "N/A" ? "" : state.tenderId);
  const [contactPerson, setContactPerson] = useState(state.contactPerson);
  const [contactEmail, setContactEmail] = useState(state.contactEmail);
  const [contactPhone, setContactPhone] = useState(state.contactPhone);
  const [address, setAddress] = useState(state.address);

  useEffect(() => {
    const unsubscribe = bidderStore.subscribe((newState) => {
      setState(newState);
      setCompanyName(newState.bidderName || "");
      setGstin(newState.gstin || "");
      setPan(newState.pan || "");
      setUdyamNumber(newState.udyamNumber || "");
      setTenderId(newState.tenderId === "N/A" ? "" : (newState.tenderId || ""));
      setContactPerson(newState.contactPerson || "");
      setContactEmail(newState.contactEmail || "");
      setContactPhone(newState.contactPhone || "");
      setAddress(newState.address || "");
    });
    return unsubscribe;
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    try {
      await bidderStore.updateProfile({
        bidderName: companyName,
        gstin,
        pan,
        udyamNumber,
        tenderId,
        contactPerson,
        contactEmail,
        contactPhone,
        address,
      });
      showToast("Bidder profile updated successfully", "success");
    } catch (error) {
      showToast(error.message || "Unable to save the bidder profile.", "error");
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div className="border-b border-outline-variant/40 pb-4">
        <div className="text-[10px] font-bold tracking-wider text-secondary uppercase">
          BIDDER SETTINGS
        </div>
        <h1 className="text-2xl font-bold text-on-surface mt-0.5">
          Company Profile & Registrations
        </h1>
        <p className="text-xs text-on-surface-variant mt-0.5">
          Manage your statutory enterprise identifiers and official contact details for GeM bidding.
        </p>
      </div>

      {/* Profile Form Card */}
      <div className="bg-surface-container-lowest border border-outline-variant/60 rounded-xl p-6 shadow-xs space-y-6">
        <div className="flex items-center gap-3 pb-3 border-b border-outline-variant/40">
          <div className="w-10 h-10 rounded-lg bg-primary-fixed flex items-center justify-center text-primary">
            <Building2 className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-on-surface uppercase tracking-wide">
              Entity Information
            </h3>
            <p className="text-[11px] text-on-surface-variant">
              Enterprise identifiers used by AI rule engine to cross-validate submitted documents.
            </p>
          </div>
        </div>

        <form onSubmit={handleSave} className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="sm:col-span-2">
            <label className="block font-bold text-on-surface-variant uppercase mb-1">
              Registered Company Name *
            </label>
            <input
              type="text"
              required
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-outline-variant bg-surface-container-lowest text-on-surface font-semibold focus:outline-none focus:border-primary"
            />
          </div>

          <div>
            <label className="block font-bold text-on-surface-variant uppercase mb-1">
              Tender ID
            </label>
            <input
              type="text"
              value={tenderId}
              onChange={(e) => setTenderId(e.target.value)}
              placeholder="TENDER-XXXXXXXXXX"
              className="w-full px-3 py-2 rounded-lg border border-outline-variant bg-surface-container-lowest text-on-surface font-mono focus:outline-none focus:border-primary"
            />
          </div>

          <div>
            <label className="block font-bold text-on-surface-variant uppercase mb-1">
              PAN Number (10 Digits) *
            </label>
            <input
              type="text"
              required
              value={pan}
              onChange={(e) => setPan(e.target.value.toUpperCase())}
              className="w-full px-3 py-2 rounded-lg border border-outline-variant bg-surface-container-lowest text-on-surface font-mono uppercase focus:outline-none focus:border-primary"
            />
          </div>

          <div>
            <label className="block font-bold text-on-surface-variant uppercase mb-1">
              GSTIN (15 Digits) *
            </label>
            <input
              type="text"
              required
              value={gstin}
              onChange={(e) => setGstin(e.target.value.toUpperCase())}
              className="w-full px-3 py-2 rounded-lg border border-outline-variant bg-surface-container-lowest text-on-surface font-mono uppercase focus:outline-none focus:border-primary"
            />
          </div>

          <div>
            <label className="block font-bold text-on-surface-variant uppercase mb-1">
              Udyam / MSME Registration Number
            </label>
            <input
              type="text"
              value={udyamNumber}
              onChange={(e) => setUdyamNumber(e.target.value.toUpperCase())}
              className="w-full px-3 py-2 rounded-lg border border-outline-variant bg-surface-container-lowest text-on-surface font-mono uppercase focus:outline-none focus:border-primary"
            />
          </div>

          <div>
            <label className="block font-bold text-on-surface-variant uppercase mb-1">
              Bidder Registration ID
            </label>
            <input
              type="text"
              disabled
              value={state.bidderId}
              className="w-full px-3 py-2 rounded-lg border border-outline-variant bg-surface-container text-on-surface-variant font-mono cursor-not-allowed"
            />
          </div>

          <div className="sm:col-span-2 pt-2 border-t border-outline-variant/40">
            <h4 className="text-xs font-bold text-on-surface uppercase tracking-wider mb-3">
              Contact Person & Official Communications
            </h4>
          </div>

          <div>
            <label className="block font-bold text-on-surface-variant uppercase mb-1">
              Authorized Signatory Name
            </label>
            <input
              type="text"
              value={contactPerson}
              onChange={(e) => setContactPerson(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-outline-variant bg-surface-container-lowest text-on-surface focus:outline-none focus:border-primary"
            />
          </div>

          <div>
            <label className="block font-bold text-on-surface-variant uppercase mb-1">
              Official Email
            </label>
            <input
              type="email"
              value={contactEmail}
              onChange={(e) => setContactEmail(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-outline-variant bg-surface-container-lowest text-on-surface focus:outline-none focus:border-primary"
            />
          </div>

          <div>
            <label className="block font-bold text-on-surface-variant uppercase mb-1">
              Contact Phone
            </label>
            <input
              type="text"
              value={contactPhone}
              onChange={(e) => setContactPhone(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-outline-variant bg-surface-container-lowest text-on-surface focus:outline-none focus:border-primary"
            />
          </div>

          <div className="sm:col-span-2">
            <label className="block font-bold text-on-surface-variant uppercase mb-1">
              Registered Office Address
            </label>
            <textarea
              rows={2}
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-outline-variant bg-surface-container-lowest text-on-surface focus:outline-none focus:border-primary"
            />
          </div>

          <div className="sm:col-span-2 pt-2 flex items-center justify-between">
            <span className="text-[11px] text-on-surface-variant">
              Changes will be synchronized with all active tender submissions.
            </span>
            <Button type="submit" variant="primary" size="sm" icon={Save}>
              Save Profile Details
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
