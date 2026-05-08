"use client";

import { Waves } from "lucide-react";

interface AIDramaBrandingProps {
  size?: "sm" | "md";
  showSlogan?: boolean;
}

export default function AIDramaBranding({ size = "md", showSlogan = true }: AIDramaBrandingProps) {
  const markSize = size === "sm" ? "h-9 w-9" : "h-14 w-14";
  const titleSize = size === "sm" ? "text-xl" : "text-3xl";
  const subtitleSize = size === "sm" ? "text-[10px]" : "text-xs";

  return (
    <div>
      <div className="flex items-center gap-3">
        <div className={`${markSize} flex-shrink-0 rounded-lg border border-cyan-400/30 bg-cyan-400/10 flex items-center justify-center`}>
          <Waves size={size === "sm" ? 19 : 28} className="text-cyan-300" />
        </div>
        <div className="min-w-0">
          <div className={`font-display ${titleSize} font-bold tracking-normal text-white leading-none`}>
            AIDrama
          </div>
          <div className={`${subtitleSize} mt-1 text-cyan-200/70 font-medium tracking-normal`}>
            Jellyfish Film Engine
          </div>
        </div>
      </div>
      {showSlogan && (
        <p className="text-[9px] text-gray-500 tracking-normal mt-3">
          Continuity-first AI Film Studio
        </p>
      )}
    </div>
  );
}
