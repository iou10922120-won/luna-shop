"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { track, AnalyticsEvent } from '@/lib/analytics';
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { User, Package, LogIn } from "lucide-react";

export default function MyPage() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  if (!isLoggedIn) {
    return (
      <div className="max-w-md mx-auto px-4 py-20">
        <div className="text-center mb-8">
          <LogIn className="w-12 h-12 mx-auto text-muted-foreground/30 mb-4" />
          <h1 className="text-2xl font-bold mb-2">로그인</h1>
          <p className="text-sm text-muted-foreground">
            LUNA 계정으로 로그인하세요.
          </p>
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            setIsLoggedIn(true);
            track(AnalyticsEvent.LOGIN, { method: 'email' });
          }}
          className="space-y-4"
        >
          <div>
            <label className="text-sm text-muted-foreground mb-1 block">
              이메일
            </label>
            <Input type="email" placeholder="hello@luna-beauty.kr" required />
          </div>
          <div>
            <label className="text-sm text-muted-foreground mb-1 block">
              비밀번호
            </label>
            <Input type="password" placeholder="••••••••" required />
          </div>
          <Button
            type="submit"
            className="w-full bg-[#2C3E6B] hover:bg-[#1e2d4f] h-11"
          >
            로그인
          </Button>
          <p className="text-xs text-center text-muted-foreground">
            포트폴리오 프로젝트로, 아무 값이나 입력하면 로그인됩니다.
          </p>
        </form>
      </div>
    );
  }

  // Mock logged-in state
  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      <div className="flex items-center gap-4 mb-8">
        <div className="w-14 h-14 bg-[#B8A9C9]/30 rounded-full flex items-center justify-center">
          <User className="w-6 h-6 text-[#2C3E6B]" />
        </div>
        <div>
          <h1 className="text-xl font-bold">김서연 님</h1>
          <p className="text-sm text-muted-foreground">seoyeon@luna-beauty.kr</p>
        </div>
      </div>

      <Separator className="mb-8" />

      {/* Order History (Mock) */}
      <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <Package className="w-5 h-5" />
        주문 내역
      </h2>

      <div className="space-y-3">
        {[
          {
            number: "LUNA-20260327-0001",
            date: "2026.03.27",
            status: "배송완료",
            amount: 43000,
            items: "병풀 시카 클렌징 밀크 외 1건",
          },
          {
            number: "LUNA-20260316-0001",
            date: "2026.03.16",
            status: "배송완료",
            amount: 141000,
            items: "히알루론 리페어 세럼 외 2건",
          },
          {
            number: "LUNA-20260228-0001",
            date: "2026.02.28",
            status: "배송완료",
            amount: 68000,
            items: "캘린듈라 수딩 클렌징 젤 외 1건",
          },
        ].map((order) => (
          <div
            key={order.number}
            className="bg-white border border-border rounded-lg p-4"
          >
            <div className="flex justify-between items-start mb-2">
              <div>
                <p className="text-xs text-muted-foreground">{order.date}</p>
                <p className="text-sm font-medium">{order.items}</p>
              </div>
              <span className="text-xs px-2 py-1 bg-green-50 text-green-700 rounded-full">
                {order.status}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">{order.number}</span>
              <span className="font-bold">
                {order.amount.toLocaleString()}원
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-8">
        <Button
          variant="outline"
          onClick={() => setIsLoggedIn(false)}
          className="w-full"
        >
          로그아웃
        </Button>
      </div>
    </div>
  );
}
