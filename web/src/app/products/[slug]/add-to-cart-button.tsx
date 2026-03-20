"use client";

import { useState } from "react";
import { ShoppingBag, Minus, Plus, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useCartStore } from "@/lib/store";
import type { Product } from "@/lib/types";

export function AddToCartButton({ product }: { product: Product }) {
  const [quantity, setQuantity] = useState(1);
  const [added, setAdded] = useState(false);
  const addItem = useCartStore((s) => s.addItem);

  const handleAdd = () => {
    addItem(product, quantity);
    setAdded(true);
    setTimeout(() => setAdded(false), 2000);
  };

  const outOfStock = product.stock_quantity <= 0;

  return (
    <div className="flex gap-3">
      {/* Quantity */}
      <div className="flex items-center border border-border rounded-lg">
        <button
          className="px-3 py-2 hover:bg-muted transition-colors"
          onClick={() => setQuantity(Math.max(1, quantity - 1))}
        >
          <Minus className="w-4 h-4" />
        </button>
        <span className="px-4 text-sm font-medium min-w-[40px] text-center">
          {quantity}
        </span>
        <button
          className="px-3 py-2 hover:bg-muted transition-colors"
          onClick={() => setQuantity(quantity + 1)}
        >
          <Plus className="w-4 h-4" />
        </button>
      </div>

      {/* Add Button */}
      <Button
        onClick={handleAdd}
        disabled={outOfStock}
        className="flex-1 bg-[#2C3E6B] hover:bg-[#1e2d4f] text-white rounded-lg h-11"
      >
        {outOfStock ? (
          "품절"
        ) : added ? (
          <>
            <Check className="w-4 h-4 mr-2" />
            담았습니다
          </>
        ) : (
          <>
            <ShoppingBag className="w-4 h-4 mr-2" />
            장바구니 담기
          </>
        )}
      </Button>
    </div>
  );
}
