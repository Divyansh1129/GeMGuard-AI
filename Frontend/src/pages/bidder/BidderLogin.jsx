import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Shield, Lock, Mail, ArrowRight, UploadCloud, CheckCircle2, FileText, ExternalLink, HelpCircle } from "lucide-react";
import Button from "../../components/common/Button";
import api from "../../services/api";

// NOTE: this is a hackathon-simple login — it does not check the password
// against anything real. What it DOES do now: create (or reuse) a REAL
// bidder row in your backend, so every other bidder-side page has an
// actual database record to read/write instead of fake data.
const REAL_BIDDER_STORAGE_KEY = "gem_rakshak_real_bidder_id";

export default function BidderLogin() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("rajesh.kumar@abctech.in");
  const [password, setPassword] = useState("password123");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email.trim() || !password.trim()) return;

    setLoading(true);
    setError("");
    try {
      // Reuse the same real bidder across logins (so uploaded docs persist)
      let bidderRealId = localStorage.getItem(REAL_BIDDER_STORAGE_KEY);

      if (!bidderRealId) {
        // First login on this browser — create a real bidder in the backend.
        const { data } = await api.post("/bidders/", {
          company_name: "ABC Technologies Pvt Ltd",
          company_type: "MSME",
          pan_number: "AABCA1234F",
          gstin: "09ABCDE1234F1Z5",
          udyam_number: "UDYAM-UP-09-0012345",
          tender_id: "GEM/2026/MPNG/001",
        });
        bidderRealId = data.id;
        localStorage.setItem(REAL_BIDDER_STORAGE_KEY, String(bidderRealId));
      }

      localStorage.setItem(
        "gem_rakshak_bidder_auth",
        JSON.stringify({
          email,
          role: "bidder",
          companyName: "ABC Technologies Pvt Ltd",
          bidderRealId: Number(bidderRealId),
          tenderId: "GEM/2026/MPNG/001",
        })
      );
      navigate("/bidder/dashboard");
    } catch (err) {
      setError(err.message || "Could not connect to backend. Is it running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-surface-container-lowest text-on-surface min-h-screen flex antialiased">
      {/* Left Split: Bidder Context (Hidden on Mobile) */}
      <div className="hidden lg:flex lg:w-[55%] flex-col justify-between p-12 relative overflow-hidden bg-surface-container-high border-r border-outline-variant">
        {/* Background Overlay */}
        <div className="absolute inset-0 bg-gradient-to-b from-primary/10 via-surface-container-high/80 to-surface-container-high z-0" />

        {/* Content */}
        <div className="relative z-10 flex flex-col h-full justify-between">
          {/* Brand Identity */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-primary flex items-center justify-center">
              <Shield className="w-6 h-6 text-on-primary" />
            </div>
            <div className="flex flex-col">
              <span className="text-2xl font-bold text-primary tracking-tight leading-tight">
                Gem Rakshak
              </span>
              <span className="text-[11px] font-semibold text-secondary uppercase tracking-wider">
                Bidder Portal
              </span>
            </div>
          </div>

          {/* Value Proposition for Bidders */}
          <div className="my-auto max-w-lg">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-container/20 text-primary font-bold text-xs uppercase tracking-wider mb-4 border border-primary/20">
              <UploadCloud className="w-4 h-4" />
              <span>GeM Bid Compliance Submission</span>
            </div>
            <h1 className="text-4xl font-extrabold text-on-surface mb-4 leading-tight">
              Submit compliance documents with zero friction.
            </h1>
            <p className="text-base text-on-surface-variant leading-relaxed">
              Upload your statutory and technical documents securely for rapid automated verification and real-time bid validation.
            </p>
          </div>

          {/* Bidder Trust Indicators */}
          <div className="space-y-4 pt-8 border-t border-outline-variant/60">
            <div className="flex items-center gap-3.5">
              <div className="w-10 h-10 rounded-lg bg-surface-container-lowest border border-outline-variant flex items-center justify-center text-primary shrink-0 shadow-xs">
                <UploadCloud className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-on-surface uppercase tracking-wider">
                  Instant OCR & Completeness Check
                </h4>
                <span className="text-xs text-on-surface-variant">
                  Get real-time feedback on document readability and missing fields
                </span>
              </div>
            </div>

            <div className="flex items-center gap-3.5">
              <div className="w-10 h-10 rounded-lg bg-surface-container-lowest border border-outline-variant flex items-center justify-center text-primary shrink-0 shadow-xs">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-on-surface uppercase tracking-wider">
                  Direct Clarification Channel
                </h4>
                <span className="text-xs text-on-surface-variant">
                  Receive targeted requests and replace flagged documents seamlessly
                </span>
              </div>
            </div>

            <div className="flex items-center gap-3.5">
              <div className="w-10 h-10 rounded-lg bg-surface-container-lowest border border-outline-variant flex items-center justify-center text-primary shrink-0 shadow-xs">
                <Shield className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-on-surface uppercase tracking-wider">
                  Encrypted & Regulated Storage
                </h4>
                <span className="text-xs text-on-surface-variant">
                  Full data privacy adhering to Government of India security standards
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Split: Bidder Login Form */}
      <div className="w-full lg:w-[45%] flex items-center justify-center p-8 lg:p-16 bg-surface-container-lowest">
        <div className="w-full max-w-[400px]">
          {/* Mobile Header */}
          <div className="flex items-center justify-center gap-2 mb-8 lg:hidden">
            <div className="w-8 h-8 rounded bg-primary flex items-center justify-center">
              <Shield className="w-5 h-5 text-on-primary" />
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-bold text-primary">Gem Rakshak</span>
              <span className="text-[10px] text-on-surface-variant uppercase font-semibold">Bidder Portal</span>
            </div>
          </div>

          <div className="mb-8 text-center lg:text-left">
            <div className="inline-block px-2.5 py-0.5 rounded-full bg-secondary-fixed text-on-secondary-fixed font-bold text-[11px] uppercase tracking-wider mb-2">
              Bidder Portal
            </div>
            <h2 className="text-2xl font-bold text-on-surface mb-1.5">Bidder Sign In</h2>
            <p className="text-xs text-on-surface-variant">
              Submit your compliance documents securely for GeM bid verification.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-on-surface-variant uppercase tracking-wider mb-1.5">
                Bidder Registered Email
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-outline absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="rajesh.kumar@abctech.in"
                  className="w-full pl-9 pr-3 py-2.5 rounded-lg border border-outline-variant bg-surface-container-lowest text-xs text-on-surface placeholder:text-outline focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary"
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label className="block text-xs font-bold text-on-surface-variant uppercase tracking-wider">
                  Password
                </label>
                <a
                  href="#"
                  onClick={(e) => e.preventDefault()}
                  className="text-xs text-primary hover:underline"
                >
                  Forgot Password?
                </a>
              </div>
              <div className="relative">
                <Lock className="w-4 h-4 text-outline absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-9 pr-3 py-2.5 rounded-lg border border-outline-variant bg-surface-container-lowest text-xs text-on-surface placeholder:text-outline focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary"
                />
              </div>
            </div>

            {error && (
              <div className="text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                {error}
              </div>
            )}

            <div className="pt-2">
              <Button
                type="submit"
                variant="primary"
                className="w-full py-2.5 text-sm font-semibold"
                icon={ArrowRight}
                disabled={loading}
              >
                {loading ? "Signing in..." : "Sign In"}
              </Button>
            </div>
          </form>

          {/* Need Help Link */}
          <div className="mt-4 flex items-center justify-between text-xs text-on-surface-variant">
            <span className="flex items-center gap-1">
              <HelpCircle className="w-3.5 h-3.5" />
              <span>Need submission assistance?</span>
            </span>
            <a href="#" onClick={(e) => e.preventDefault()} className="text-primary font-semibold hover:underline">
              Bidder Helpdesk
            </a>
          </div>

          {/* Switch to Officer Portal Banner */}
          <div className="mt-6 pt-5 border-t border-outline-variant/60 text-center">
            <p className="text-xs text-on-surface-variant mb-2">
              Are you a Government Procurement Officer?
            </p>
            <Link
              to="/login"
              className="inline-flex items-center gap-1.5 text-xs font-bold text-primary hover:text-primary/80 transition-colors bg-primary-fixed/40 px-3.5 py-2 rounded-lg border border-primary/20"
            >
              <span>Officer Login</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
