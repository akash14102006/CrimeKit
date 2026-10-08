import { redirect } from "next/navigation";
import { env } from "@/config/env";

export default function Home() {
  if (env.devAuthDisabled) {
    redirect("/cases");
  }
  redirect("/login");
}
