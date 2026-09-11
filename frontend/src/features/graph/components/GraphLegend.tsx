"use client";

import { Users, MapPin, Smartphone, Building, FileText, Globe, Cpu, Shield, Clock, Database } from "lucide-react";

const LEGEND_ITEMS = [
  { icon: Users, color: "text-blue-600", bg: "bg-blue-100", label: "Person" },
  { icon: MapPin, color: "text-green-600", bg: "bg-green-100", label: "Location" },
  { icon: Smartphone, color: "text-purple-600", bg: "bg-purple-100", label: "Device" },
  { icon: Building, color: "text-orange-600", bg: "bg-orange-100", label: "Organization" },
  { icon: FileText, color: "text-emerald-600", bg: "bg-emerald-100", label: "Evidence" },
  { icon: Globe, color: "text-cyan-600", bg: "bg-cyan-100", label: "URL" },
  { icon: Cpu, color: "text-indigo-600", bg: "bg-indigo-100", label: "Process" },
  { icon: Shield, color: "text-amber-600", bg: "bg-amber-100", label: "Case" },
  { icon: Clock, color: "text-pink-600", bg: "bg-pink-100", label: "Timeline" },
  { icon: Database, color: "text-gray-600", bg: "bg-gray-100", label: "Entity" },
];

export function GraphLegend() {
  return (
    <div className="flex items-center gap-2 flex-wrap px-1">
      {LEGEND_ITEMS.map((item) => {
        const Icon = item.icon;
        return (
          <div key={item.label} className="flex items-center gap-1">
            <div className={`h-3 w-3 rounded ${item.bg} flex items-center justify-center`}>
              <Icon className={`h-2 w-2 ${item.color}`} />
            </div>
            <span className="text-[10px] text-muted-foreground">{item.label}</span>
          </div>
        );
      })}
    </div>
  );
}
