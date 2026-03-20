"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { useCartStore } from "@/lib/store";
import { formatPrice } from "@/lib/format";
import { CheckCircle } from "lucide-react";

export default function CheckoutPage() {
  const { items, totalPrice, clearCart } = useCartStore();
  const router = useRouter();
  const [completed, setCompleted] = useState(false);

  if (items.length === 0 && !completed) {
    router.push("/cart");
    return null;
  }

  const shipping = totalPrice() >= 50000 ? 0 : 3000;
  const total = totalPrice() + shipping;

  const handleOrder = (e: React.FormEvent) => {
    e.preventDefault();
    // Mock order — just clear cart and show success
    clearCart();
    setCompleted(true);
  };

  if (completed) {
    return (
      <div className="max-w-lg mx-auto px-4 py-20 text-center">
        <CheckCircle className="w-16 h-16 mx-auto text-green-500 mb-4" />
        <h1 className="text-2xl font-bold mb-2">주문이 완료되었습니다!</h1>
        <p className="text-muted-foreground mb-2">
          주문번호: LUNA-{Date.now().toString().slice(-8)}
        </p>
        <p className="text-sm text-muted-foreground mb-8">
          포트폴리오용 가상 주문입니다.
        </p>
        <Button
          onClick={() => router.push("/products")}
          className="bg-[#2C3E6B] hover:bg-[#1e2d4f]"
        >
          쇼핑 계속하기
        </Button>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-8">주문/결제</h1>

      <form onSubmit={handleOrder} className="space-y-6">
        {/* Shipping Info */}
        <section>
          <h2 className="text-lg font-semibold mb-4">배송 정보</h2>
          <div className="grid gap-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-muted-foreground mb-1 block">
                  이름
                </label>
                <Input placeholder="홍길동" required />
              </div>
              <div>
                <label className="text-sm text-muted-foreground mb-1 block">
                  연락처
                </label>
                <Input placeholder="010-1234-5678" required />
              </div>
            </div>
            <div>
              <label className="text-sm text-muted-foreground mb-1 block">
                주소
              </label>
              <Input placeholder="서울시 강남구 테헤란로 123" required />
            </div>
          </div>
        </section>

        <Separator />

        {/* Order Summary */}
        <section>
          <h2 className="text-lg font-semibold mb-4">주문 상품</h2>
          <div className="space-y-2">
            {items.map((item) => (
              <div
                key={item.product.id}
                className="flex justify-between text-sm"
              >
                <span className="text-muted-foreground">
                  {item.product.name} x {item.quantity}
                </span>
                <span>
                  {formatPrice(
                    (item.product.sale_price ?? item.product.price) *
                      item.quantity
                  )}
                </span>
              </div>
            ))}
          </div>
        </section>

        <Separator />

        {/* Total */}
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">상품 합계</span>
            <span>{formatPrice(totalPrice())}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">배송비</span>
            <span>{shipping === 0 ? "무료" : formatPrice(shipping)}</span>
          </div>
          <Separator />
          <div className="flex justify-between text-base font-bold pt-2">
            <span>총 결제금액</span>
            <span className="text-[#2C3E6B]">{formatPrice(total)}</span>
          </div>
        </div>

        <Button
          type="submit"
          className="w-full bg-[#2C3E6B] hover:bg-[#1e2d4f] h-12 text-base"
        >
          {formatPrice(total)} 결제하기
        </Button>

        <p className="text-xs text-center text-muted-foreground">
          포트폴리오 프로젝트로, 실제 결제는 이루어지지 않습니다.
        </p>
      </form>
    </div>
  );
}
