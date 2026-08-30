import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Shield, Lock, Mail, ArrowRight, ClipboardCheck, UserCheck, CheckCircle, ExternalLink } from "lucide-react";
import Button from "../components/common/Button";

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("officer@gem.gov.in");
  const [password, setPassword] = useState("password123");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (email.trim() && password.trim()) {
      localStorage.setItem(
        "gem_rakshak_auth",
        JSON.stringify({
          email,
          role: "officer",
          name: "Rajesh Varma",
          id: "88294-GOV",
        })
      );
      navigate("/dashboard");
    }
  };

  return (
    <div className="bg-surface-container-lowest text-on-surface min-h-screen flex antialiased">
      {/* Left Split: Branding and Context (Hidden on Mobile) */}
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
                GeMGuard AI
              </span>
              <span className="text-[11px] font-semibold text-on-surface-variant uppercase tracking-wider">
                Officer Portal
              </span>
            </div>
          </div>

          {/* Value Proposition */}
          <div className="my-auto max-w-lg">
            <h1 className="text-4xl font-extrabold text-on-surface mb-4 leading-tight">
              Verify bids with confidence.
            </h1>
            <p className="text-base text-on-surface-variant leading-relaxed">
              AI-assisted compliance verification for transparent, automated, and legally resilient government e-procurement.
            </p>
          </div>

          {/* Trust Indicators */}
          <div className="space-y-4 pt-8 border-t border-outline-variant/60">
            <div className="flex items-center gap-3.5">
              <div className="w-10 h-10 rounded-lg bg-surface-container-lowest border border-outline-variant flex items-center justify-center text-primary shrink-0 shadow-xs">
                <Shield className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-on-surface uppercase tracking-wider">
                  Security Standard
                </h4>
                <span className="text-xs text-on-surface-variant">
                  Encrypted & ISO 27001 Document Processing
                </span>
              </div>
            </div>

            <div className="flex items-center gap-3.5">
              <div className="w-10 h-10 rounded-lg bg-surface-container-lowest border border-outline-variant flex items-center justify-center text-primary shrink-0 shadow-xs">
                <ClipboardCheck className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-on-surface uppercase tracking-wider">
                  Verification Method
                </h4>
                <span className="text-xs text-on-surface-variant">
                  Rule Engine & Multi-Registry Cross Checking
                </span>
              </div>
            </div>

            <div className="flex items-center gap-3.5">
              <div className="w-10 h-10 rounded-lg bg-surface-container-lowest border border-outline-variant flex items-center justify-center text-primary shrink-0 shadow-xs">
                <UserCheck className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-on-surface uppercase tracking-wider">
                  Operational Model
                </h4>
                <span className="text-xs text-on-surface-variant">
                  Human-in-the-Loop Advisory Intelligence
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Split: Authentication Form */}
      <div className="w-full lg:w-[45%] flex items-center justify-center p-8 lg:p-16 bg-surface-container-lowest">
        <div className="w-full max-w-[400px]">
          {/* Mobile Header */}
          <div className="flex items-center justify-center gap-2 mb-8 lg:hidden">
            <div className="w-8 h-8 rounded bg-primary flex items-center justify-center">
              <Shield className="w-5 h-5 text-on-primary" />
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-bold text-primary">GeMGuard AI</span>
              <span className="text-[10px] text-on-surface-variant uppercase font-semibold">Officer Portal</span>
            </div>
          </div>

          <div className="mb-8 text-center lg:text-left">
            <div className="inline-block px-2.5 py-0.5 rounded-full bg-primary-fixed text-on-primary-fixed font-bold text-[11px] uppercase tracking-wider mb-2">
              Procurement Officer Workspace
            </div>
            <h2 className="text-2xl font-bold text-on-surface mb-1.5">Sign In</h2>
            <p className="text-xs text-on-surface-variant">
              Access the official GeM compliance verification and audit portal.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-on-surface-variant uppercase tracking-wider mb-1.5">
                Official Email
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-outline absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="officer@gem.gov.in"
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
                  Forgot password?
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

            <div className="pt-2">
              <Button
                type="submit"
                variant="primary"
                className="w-full py-2.5 text-sm font-semibold"
                icon={ArrowRight}
              >
                Sign In to Officer Portal
              </Button>
            </div>
          </form>

          {/* Switch to Bidder Portal Banner */}
          <div className="mt-6 pt-5 border-t border-outline-variant/60 text-center">
            <p className="text-xs text-on-surface-variant mb-2">
              Are you a Bidder looking to submit compliance documents?
            </p>
            <Link
              to="/bidder/login"
              className="inline-flex items-center gap-1.5 text-xs font-bold text-primary hover:text-primary/80 transition-colors bg-primary-fixed/40 px-3.5 py-2 rounded-lg border border-primary/20"
            >
              <span>Go to Bidder Portal</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </Link>
          </div>

          {/* Government Warning */}
          <div className="mt-6 p-3.5 bg-surface-container rounded-lg border border-outline-variant/60">
            <p className="text-[11px] text-on-surface-variant leading-relaxed">
              <strong>Official Notice:</strong> This is a restricted Government of India procurement portal. All actions and sessions are authenticated and audited.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
