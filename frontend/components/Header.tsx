"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { isAuthenticated } from "@/lib/api-client";

export default function Header() {
  const pathname = usePathname();
  const [authenticated, setAuthenticated] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    // Only check auth on client side after mount
    setMounted(true);
    setAuthenticated(isAuthenticated());
  }, []);

  return (
    <header className="bg-white/80 backdrop-blur-sm border-b border-slate-200 shadow-sm sticky top-0 z-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="text-xl font-semibold text-slate-900">
              Todo App
            </Link>
          </div>
          {mounted && authenticated && (
            <nav className="flex space-x-4">
              <Link
                href="/tasks"
                className={`px-3 py-2 rounded-md text-sm font-medium ${
                  pathname === "/tasks"
                    ? "bg-slate-100 text-slate-900"
                    : "text-slate-700 hover:bg-slate-50"
                }`}
              >
                Tasks
              </Link>
              <Link
                href="/chat"
                className={`px-3 py-2 rounded-md text-sm font-medium ${
                  pathname === "/chat"
                    ? "bg-slate-100 text-slate-900"
                    : "text-slate-700 hover:bg-slate-50"
                }`}
              >
                Chat
              </Link>
            </nav>
          )}
        </div>
      </div>
    </header>
  );
}
