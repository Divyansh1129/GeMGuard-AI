import React from "react";

export default function VerificationChart({
  verified = 76,
  review = 17,
  nonCompliant = 7,
}) {
  return (
    <div className="bg-surface-container-lowest border border-outline-variant/60 rounded-lg p-6 flex flex-col h-full">
      <h3 className="text-base font-bold text-on-surface mb-6 border-b border-outline-variant/50 pb-3">
        Verification Overview
      </h3>

      <div className="flex-1 flex flex-col items-center justify-center py-2">
        {/* CSS Donut Chart matching Stitch design */}
        <div
          className="relative w-44 h-44 rounded-full border-12 border-surface-container flex items-center justify-center mb-6 shadow-inner"
          style={{
            background: `conic-gradient(from 0deg, #15803d 0% ${verified}%, #ea580c ${verified}% ${
              verified + review
            }%, #b91c1c ${verified + review}% 100%)`,
          }}
        >
          <div className="absolute inset-0 bg-surface-container-lowest rounded-full m-3.5 flex flex-col items-center justify-center shadow-xs">
            <span className="text-xs text-on-surface-variant font-medium">
              Verified
            </span>
            <span className="text-2xl font-bold text-on-surface">
              {verified}%
            </span>
          </div>
        </div>

        {/* Legend */}
        <div className="w-full space-y-2.5 px-2">
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center">
              <div className="w-2.5 h-2.5 rounded-full bg-[#15803d] mr-2" />
              <span className="text-on-surface font-medium">Verified</span>
            </div>
            <span className="font-bold text-on-surface">{verified}%</span>
          </div>

          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center">
              <div className="w-2.5 h-2.5 rounded-full bg-[#ea580c] mr-2" />
              <span className="text-on-surface font-medium">Review Required</span>
            </div>
            <span className="font-bold text-on-surface">{review}%</span>
          </div>

          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center">
              <div className="w-2.5 h-2.5 rounded-full bg-[#b91c1c] mr-2" />
              <span className="text-on-surface font-medium">Non-Compliant</span>
            </div>
            <span className="font-bold text-on-surface">{nonCompliant}%</span>
          </div>
        </div>
      </div>
    </div>
  );
}
