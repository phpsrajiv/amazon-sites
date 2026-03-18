import React from "react";
import { Zap } from "lucide-react";
import { Link, useLocation } from "wouter";
import { useTrial } from "./TrialContext";
import { useAuth } from "./AuthContext";
import { Button } from "@/components/ui/button";

function smoothScrollTo(id: string) {
  const el = document.querySelector(id);
  if (el) {
    el.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

export function Layout({ children }: { children: React.ReactNode }) {
  const { openTrialModal } = useTrial();
  const { isLoggedIn, user, openLoginModal, logout } = useAuth();

  const [location] = useLocation();

  const navLinks = [
    { label: "Features", href: "#features" },
    { label: "How it Works", href: "#how-it-works" },
    { label: "Testimonials", href: "#testimonials" },
    { label: "Pricing", href: "#pricing" },
    { label: "Blog", href: "/blog" },
  ];

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col font-sans selection:bg-[#FF9900]/30 selection:text-[#0F1111]">
      {/* Navbar */}
      <header className="fixed top-0 z-50 w-full border-b border-white/10 bg-[#131921]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-[#FF9900] flex items-center justify-center shadow-lg">
              <Zap className="w-4 h-4 text-[#0F1111] fill-[#0F1111]/20" />
            </div>
            <span className="font-display font-bold text-xl tracking-tight text-white">SellerBuddy</span>
          </div>

          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-white/80">
            {navLinks.map((link) =>
              link.href.startsWith("#") ? (
                <a
                  key={link.href}
                  href={link.href}
                  onClick={(e) => {
                    e.preventDefault();
                    smoothScrollTo(link.href);
                  }}
                  className="hover:text-white transition-colors cursor-pointer"
                >
                  {link.label}
                </a>
              ) : (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`hover:text-white transition-colors cursor-pointer ${location === link.href ? "text-white" : ""}`}
                >
                  {link.label}
                </Link>
              )
            )}
          </nav>

          <div className="flex items-center gap-4">
            {isLoggedIn ? (
              <>
                <span className="hidden sm:flex text-sm text-white/80">
                  {user?.name}
                </span>
                <Button
                  variant="ghost"
                  className="hidden sm:flex hover:bg-white/10 text-white"
                  onClick={logout}
                >
                  Log out
                </Button>
              </>
            ) : (
              <Button
                variant="ghost"
                className="hidden sm:flex hover:bg-white/10 text-white"
                onClick={openLoginModal}
              >
                Log in
              </Button>
            )}
            <Button
              onClick={openTrialModal}
              className="bg-[#FF9900] text-[#0F1111] font-bold hover:bg-[#FA8900] shadow-md hover:-translate-y-0.5 transition-all rounded-md"
            >
              Start Free Trial
            </Button>
          </div>
        </div>
      </header>

      <main className="flex-1 pt-16">
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t-4 border-[#FF9900] bg-[#131921] py-12 md:py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div className="col-span-2">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-6 h-6 rounded bg-[#FF9900] flex items-center justify-center">
                  <Zap className="w-3 h-3 text-[#0F1111] fill-[#0F1111]/20" />
                </div>
                <span className="font-display font-bold text-xl text-white">SellerBuddy</span>
              </div>
              <p className="text-gray-400 text-sm max-w-sm mb-6">
                Automate your entire Amazon business with intelligent AI agents. Increase rankings, lower ACOS, and scale effortlessly.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-white">Product</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#features" onClick={(e) => { e.preventDefault(); smoothScrollTo("#features"); }} className="hover:text-white transition-colors cursor-pointer">Features</a></li>
                <li><a href="#pricing" onClick={(e) => { e.preventDefault(); smoothScrollTo("#pricing"); }} className="hover:text-white transition-colors cursor-pointer">Pricing</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Case Studies</a></li>
                <li><a href="#" className="hover:text-white transition-colors">API Docs</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-white">Company</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">About Us</a></li>
                <li><Link href="/blog" className="hover:text-white transition-colors">Blog</Link></li>
                <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Contact Support</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-white/10 mt-12 pt-8 flex flex-col md:flex-row items-center justify-between text-sm text-gray-400">
            <p>© {new Date().getFullYear()} SellerBuddy. All rights reserved.</p>
            <div className="flex gap-4 mt-4 md:mt-0">
              <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
              <a href="#" className="hover:text-white transition-colors">Terms of Service</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
