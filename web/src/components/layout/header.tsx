"use client";

import Link from "next/link";
import { ShoppingBag, User, Menu, X } from "lucide-react";
import { useState } from "react";
import { useCartStore } from "@/lib/store";

const NAV_LINKS = [
  { href: "/products", label: "전체 상품" },
  { href: "/products?category=skincare", label: "스킨케어" },
  { href: "/products?category=serum", label: "세럼" },
  { href: "/products?category=cream", label: "크림" },
  { href: "/about", label: "브랜드 스토리" },
];

export function Header() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const totalItems = useCartStore((s) => s.totalItems());

  return (
    <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-border">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2">
          <span className="text-2xl font-bold tracking-wider text-[#2C3E6B]">
            LUNA
          </span>
        </Link>

        {/* Desktop Nav */}
        <nav className="hidden md:flex items-center gap-8">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        {/* Actions */}
        <div className="flex items-center gap-4">
          <Link
            href="/cart"
            className="relative p-2 hover:bg-muted rounded-full transition-colors"
          >
            <ShoppingBag className="w-5 h-5" />
            {totalItems > 0 && (
              <span className="absolute -top-0.5 -right-0.5 bg-[#2C3E6B] text-white text-[10px] font-bold w-4.5 h-4.5 rounded-full flex items-center justify-center">
                {totalItems}
              </span>
            )}
          </Link>
          <Link
            href="/mypage"
            className="p-2 hover:bg-muted rounded-full transition-colors hidden md:flex"
          >
            <User className="w-5 h-5" />
          </Link>
          <button
            className="p-2 md:hidden"
            onClick={() => setMobileOpen(!mobileOpen)}
          >
            {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Nav */}
      {mobileOpen && (
        <div className="md:hidden border-t border-border bg-white">
          <nav className="flex flex-col p-4 gap-3">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setMobileOpen(false)}
                className="text-sm py-2 text-muted-foreground hover:text-foreground"
              >
                {link.label}
              </Link>
            ))}
            <Link
              href="/mypage"
              onClick={() => setMobileOpen(false)}
              className="text-sm py-2 text-muted-foreground hover:text-foreground"
            >
              마이페이지
            </Link>
          </nav>
        </div>
      )}
    </header>
  );
}
