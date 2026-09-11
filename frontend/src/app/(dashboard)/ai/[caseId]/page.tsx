import AIWorkspacePage from "@/features/ai/components/AIWorkspacePage";

export function generateStaticParams() {
  return [{ caseId: "_" }];
}

export default function AIWorkspaceRoute() {
  return <AIWorkspacePage />;
}
