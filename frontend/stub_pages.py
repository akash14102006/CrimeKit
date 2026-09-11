import os

pages = [
    ("cases", "Case Management"),
    ("evidence", "Evidence Library"),
    ("graph", "Knowledge Graph"),
    ("timeline", "Investigation Timeline"),
    ("admin", "Administration"),
    ("settings", "Settings")
]

base_path = "src/app/(dashboard)"

for folder, title in pages:
    content = f'''import {{ Metadata }} from "next";

export const metadata: Metadata = {{
  title: "{title} - CrimeKit Enterprise",
}};

export default function Page() {{
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">{title}</h1>
        <p className="text-muted-foreground">This module is currently under development (Phase {5 + pages.index((folder, title))} or later).</p>
      </div>
      <div className="flex h-[400px] items-center justify-center rounded-lg border border-dashed">
        <p className="text-muted-foreground">Coming Soon</p>
      </div>
    </div>
  );
}}
'''
    filepath = os.path.join(base_path, folder, "page.tsx")
    with open(filepath, "w") as f:
        f.write(content)

print("Created 6 stub pages successfully.")
