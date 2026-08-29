import React, { useState, useEffect } from "react";
import { CheckCircle2, AlertCircle, X, Info } from "lucide-react";

let toastTrigger = null;

export const showToast = (message, type = "success") => {
  if (toastTrigger) {
    toastTrigger(message, type);
  }
};

export default function Toast() {
  const [toast, setToast] = useState(null);

  useEffect(() => {
    toastTrigger = (message, type) => {
      setToast({ message, type, id: Date.now() });
    };
    return () => {
      toastTrigger = null;
    };
  }, []);

  useEffect(() => {
    if (!toast) return;
    const timer = setTimeout(() => {
      setToast(null);
    }, 4000);
    return () => clearTimeout(timer);
  }, [toast]);

  if (!toast) return null;

  const isSuccess = toast.type === "success";
  const isError = toast.type === "error";

  return (
    <div className="fixed bottom-6 right-6 z-50 max-w-md toast-enter">
      <div
        className={`flex items-center gap-3 px-4 py-3 rounded-lg border shadow-md ${
          isSuccess
            ? "bg-green-50 border-green-200 text-green-900"
            : isError
            ? "bg-red-50 border-red-200 text-red-900"
            : "bg-surface-container-lowest border-outline-variant text-on-surface"
        }`}
      >
        {isSuccess && <CheckCircle2 className="w-5 h-5 text-green-600 shrink-0" />}
        {isError && <AlertCircle className="w-5 h-5 text-red-600 shrink-0" />}
        {!isSuccess && !isError && <Info className="w-5 h-5 text-primary shrink-0" />}
        <span className="text-sm font-medium">{toast.message}</span>
        <button
          onClick={() => setToast(null)}
          className="ml-auto p-1 rounded hover:bg-black/5 text-on-surface-variant transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
