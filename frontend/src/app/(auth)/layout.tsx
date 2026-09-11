export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-muted/30 p-4">
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(30,58,138,0.08),transparent_50%),radial-gradient(circle_at_bottom_right,rgba(124,58,237,0.06),transparent_50%)]"
      />
      <div className="relative z-10">{children}</div>
    </div>
  );
}
