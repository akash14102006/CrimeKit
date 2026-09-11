import { Sidebar } from "@/components/shared/Sidebar";
import { Header } from "@/components/shared/Header";
import { Metadata } from "next";
import { AuthGuard } from "@/components/shared/AuthGuard";
import { CurrentUserLoader } from "@/components/shared/CurrentUserLoader";

export const metadata: Metadata = {
  title: "Dashboard - CrimeKit Enterprise",
  description: "CrimeKit Investigation Workspace",
};

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthGuard>
      <CurrentUserLoader />
      <div className="flex h-screen overflow-hidden bg-background">
        <Sidebar />
        <div className="flex flex-1 flex-col overflow-hidden">
          <Header />
          <main className="flex-1 overflow-y-auto bg-muted/20 p-6">
            {children}
          </main>
        </div>
      </div>
    </AuthGuard>
  );
}
