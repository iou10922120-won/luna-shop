"use client";

import Link from "next/link";
import { Trash2, Minus, Plus, ShoppingBag } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { useCartStore } from "@/lib/store";
import { formatPrice } from "@/lib/format";

export default function CartPage() {
  const { items, removeItem, updateQuantity, totalPrice, clearCart } =
    useCartStore();

  if (items.length === 0) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-20 text-center">
        <ShoppingBag className="w-16 h-16 mx-auto text-muted-foreground/30 mb-4" />
        <h1 className="text-2xl font-bold mb-2">장바구니가 비어있습니다</h1>
        <p className="text-muted-foreground mb-6">
          마음에 드는 제품을 담아보세요.
        </p>
        <Link href="/products">
          <Button className="bg-[#2C3E6B] hover:bg-[#1e2d4f]">
            쇼핑 계속하기
          </Button>
        </Link>
      </div>
    );
  }

  const shipping = totalPrice() >= 50000 ? 0 : 3000;
  const total = totalPrice() + shipping;

  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-8">장바구니</h1>

      {/* Items */}
      <div className="space-y-4">
        {items.map((item) => {
          const price = item.product.sale_price ?? item.product.price;
          return (
            <div
              key={item.product.id}
              className="flex gap-4 bg-white border border-border rounded-lg p-4"
            >
              {/* Thumbnail placeholder */}
              <div className="w-20 h-20 bg-gradient-to-br from-[#f0ece6] to-[#e8e0f0] rounded-lg flex items-center justify-center shrink-0">
                <span className="text-2xl opacity-20">🌙</span>
              </div>

              <div className="flex-1 min-w-0">
                <Link
                  href={`/products/${item.product.slug}`}
                  className="text-sm font-medium hover:text-[#2C3E6B] line-clamp-1"
                >
                  {item.product.name}
                </Link>
                <p className="text-sm font-bold mt-1">{formatPrice(price)}</p>

                {/* Quantity controls */}
                <div className="flex items-center gap-2 mt-2">
                  <button
                    onClick={() =>
                      updateQuantity(item.product.id, item.quantity - 1)
                    }
                    className="p-1 hover:bg-muted rounded"
                  >
                    <Minus className="w-3.5 h-3.5" />
                  </button>
                  <span className="text-sm w-6 text-center">
                    {item.quantity}
                  </span>
                  <button
                    onClick={() =>
                      updateQuantity(item.product.id, item.quantity + 1)
                    }
                    className="p-1 hover:bg-muted rounded"
                  >
                    <Plus className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              <div className="flex flex-col items-end justify-between">
                <button
                  onClick={() => removeItem(item.product.id)}
                  className="p-1 text-muted-foreground hover:text-destructive"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
                <span className="text-sm font-bold">
                  {formatPrice(price * item.quantity)}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      <Separator className="my-6" />

      {/* Summary */}
      <div className="space-y-3 text-sm">
        <div className="flex justify-between">
          <span className="text-muted-foreground">상품 합계</span>
          <span>{formatPrice(totalPrice())}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">배송비</span>
          <span>
            {shipping === 0 ? (
              <span className="text-green-600">무료</span>
            ) : (
              formatPrice(shipping)
            )}
          </span>
        </div>
        {shipping > 0 && (
          <p className="text-xs text-muted-foreground">
            {formatPrice(50000 - totalPrice())} 더 담으면 무료배송!
          </p>
        )}
        <Separator />
        <div className="flex justify-between text-base font-bold">
          <span>총 결제금액</span>
          <span className="text-[#2C3E6B]">{formatPrice(total)}</span>
        </div>
      </div>

      {/* Actions */}
      <div className="mt-8 flex gap-3">
        <Button
          variant="outline"
          onClick={clearCart}
          className="flex-1"
        >
          전체 삭제
        </Button>
        <Link href="/checkout" className="flex-[2]">
          <Button className="w-full bg-[#2C3E6B] hover:bg-[#1e2d4f] h-12 text-base">
            주문하기
          </Button>
        </Link>
      </div>
    </div>
  );
}
