import { LoadingState } from "@/components/shared/LoadingState";

export default function DashboardLoading() {
  return (
    <div className="flex h-[60vh] items-center justify-center">
      <LoadingState label="Loading..." />
    </div>
  );
}
