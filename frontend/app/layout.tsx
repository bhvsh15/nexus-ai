import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "NexusAI",
  description: "Local-first AI engineering platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased dark`}
    >
      <body className="min-h-full flex bg-background text-foreground">
        {/* Sidebar */}
        <aside className="w-52 min-h-screen border-r border-border flex flex-col py-5 shrink-0 bg-card/40 backdrop-blur-sm">
          {/* Logo */}
          <div className="px-5 mb-6">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded bg-primary flex items-center justify-center">
                <span className="text-primary-foreground text-xs font-black">N</span>
              </div>
              <span className="text-sm font-semibold tracking-tight">NexusAI</span>
            </div>
            <p className="text-[10px] text-muted-foreground mt-1 pl-8">Local AI Platform</p>
          </div>

          {/* Nav */}
          <nav className="flex flex-col gap-0.5 px-2">
            {[
              { href: "/prompt-lab", label: "Prompt Lab", icon: "✦" },
              { href: "/rag-studio", label: "RAG Studio", icon: "◈" },
              { href: "/agent-builder", label: "Agent Builder", icon: "⬡" },
              { href: "/crew-studio", label: "Crew Studio", icon: "◎" },
              { href: "/observability", label: "Observability", icon: "◉" },
            ].map(({ href, label, icon }) => (
              <a
                key={href}
                href={href}
                className="flex items-center gap-2.5 px-3 py-2 rounded-md text-xs text-muted-foreground hover:text-foreground hover:bg-accent transition-all duration-150 group"
              >
                <span className="text-[10px] text-muted-foreground group-hover:text-primary transition-colors">{icon}</span>
                {label}
              </a>
            ))}
          </nav>

          {/* Footer */}
          <div className="mt-auto px-5">
            <div className="text-[10px] text-muted-foreground/50 font-mono">v0.1.0-alpha</div>
          </div>
        </aside>

        {/* Main content */}
        <main className="flex-1 overflow-auto min-h-screen">{children}</main>
      </body>
    </html>
  );
}
