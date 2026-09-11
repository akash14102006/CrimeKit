"use client";

import { useTheme } from "next-themes";
import { useState } from "react";
import { Sun, Moon, Monitor } from "lucide-react";

const themes = [
  { value: "light", label: "Light", icon: Sun },
  { value: "dark", label: "Dark", icon: Moon },
  { value: "system", label: "System", icon: Monitor },
];

const fontSizes = [
  { value: "small", label: "Small" },
  { value: "medium", label: "Medium (Default)" },
  { value: "large", label: "Large" },
];

const densities = [
  { value: "compact", label: "Compact" },
  { value: "normal", label: "Normal" },
  { value: "relaxed", label: "Relaxed" },
];

function readLocalStorage(key: string, fallback: string): string {
  try {
    return localStorage.getItem(key) || fallback;
  } catch {
    return fallback;
  }
}

function readLocalStorageBool(key: string, fallback: boolean): boolean {
  try {
    const val = localStorage.getItem(key);
    return val !== null ? val === "true" : fallback;
  } catch {
    return fallback;
  }
}

export function AppearancePanel() {
  const { theme, setTheme } = useTheme();
  const [fontSize, setFontSize] = useState(() => readLocalStorage("crimekit-font-size", "medium"));
  const [density, setDensity] = useState(() => readLocalStorage("crimekit-density", "normal"));
  const [animations, setAnimations] = useState(() => readLocalStorageBool("crimekit-animations", true));

  const savePref = (key: string, value: string) => {
    try {
      localStorage.setItem(key, value);
    } catch {
      // ignore
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold">Appearance</h2>
        <p className="text-sm text-muted-foreground">
          Customize how CrimeKit looks and feels.
        </p>
      </div>

      <div className="rounded-lg border bg-card p-6 space-y-6">
        <div className="space-y-3">
          <label className="text-sm font-medium">Theme</label>
          <div className="grid grid-cols-3 gap-3">
            {themes.map(({ value, label, icon: Icon }) => (
              <button
                key={value}
                onClick={() => setTheme(value)}
                className={`flex flex-col items-center gap-2 rounded-lg border p-4 transition-colors ${
                  theme === value
                    ? "border-primary bg-primary/5 text-primary"
                    : "hover:bg-muted"
                }`}
              >
                <Icon className="h-5 w-5" />
                <span className="text-sm">{label}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-3">
          <label className="text-sm font-medium">Font Size</label>
          <div className="grid grid-cols-3 gap-3">
            {fontSizes.map(({ value, label }) => (
              <button
                key={value}
                onClick={() => {
                  setFontSize(value);
                  savePref("crimekit-font-size", value);
                }}
                className={`rounded-lg border p-3 text-sm transition-colors ${
                  fontSize === value
                    ? "border-primary bg-primary/5 text-primary"
                    : "hover:bg-muted"
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-3">
          <label className="text-sm font-medium">Density</label>
          <div className="grid grid-cols-3 gap-3">
            {densities.map(({ value, label }) => (
              <button
                key={value}
                onClick={() => {
                  setDensity(value);
                  savePref("crimekit-density", value);
                }}
                className={`rounded-lg border p-3 text-sm transition-colors ${
                  density === value
                    ? "border-primary bg-primary/5 text-primary"
                    : "hover:bg-muted"
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center justify-between rounded-lg border p-4">
          <div>
            <p className="text-sm font-medium">Animations</p>
            <p className="text-xs text-muted-foreground">
              Enable smooth transitions and animations
            </p>
          </div>
          <button
            onClick={() => {
              const next = !animations;
              setAnimations(next);
              savePref("crimekit-animations", String(next));
            }}
            className={`relative h-6 w-11 rounded-full transition-colors ${
              animations ? "bg-primary" : "bg-muted"
            }`}
          >
            <span
              className={`absolute top-0.5 h-5 w-5 rounded-full bg-white transition-transform ${
                animations ? "translate-x-5" : "translate-x-0.5"
              }`}
            />
          </button>
        </div>
      </div>
    </div>
  );
}
