import { Metadata } from "next";
import { SettingsContent } from "./SettingsContent";

export const metadata: Metadata = {
  title: "Settings - CrimeKit Enterprise",
};

export default function Page() {
  return <SettingsContent />;
}
