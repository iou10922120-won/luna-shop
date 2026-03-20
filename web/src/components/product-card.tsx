"use client";

import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { formatPrice, discountRate } from "@/lib/format";
import type { Product } from "@/lib/types";

export function ProductCard({ product }: { product: Product }) {
  const hasDiscount = product.sale_price && product.sale_price < product.price;

  return (
    <Link
      href={`/products/${product.slug}`}
      className="group block bg-white rounded-xl overflow-hidden border border-border hover:shadow-lg transition-shadow"
    >
      {/* Image placeholder */}
      <div className="aspect-square bg-gradient-to-br from-[#f0ece6] to-[#e8e0f0] flex items-center justify-center relative">
        <span className="text-4xl opacity-30">🌙</span>
        {hasDiscount && (
          <Badge className="absolute top-3 left-3 bg-[#2C3E6B] text-white text-xs">
            {discountRate(product.price, product.sale_price!)}
          </Badge>
        )}
        {product.is_vegan_certified && (
          <Badge
            variant="outline"
            className="absolute top-3 right-3 text-[10px] border-green-500 text-green-700 bg-white/80"
          >
            VEGAN
          </Badge>
        )}
      </div>

      {/* Info */}
      <div className="p-4">
        <p className="text-xs text-muted-foreground mb-1">
          {product.category?.name}
        </p>
        <h3 className="text-sm font-medium leading-snug group-hover:text-[#2C3E6B] transition-colors line-clamp-2">
          {product.name}
        </h3>
        <div className="mt-2 flex items-baseline gap-2">
          {hasDiscount ? (
            <>
              <span className="text-base font-bold text-[#2C3E6B]">
                {formatPrice(product.sale_price!)}
              </span>
              <span className="text-xs text-muted-foreground line-through">
                {formatPrice(product.price)}
              </span>
            </>
          ) : (
            <span className="text-base font-bold">
              {formatPrice(product.price)}
            </span>
          )}
        </div>
      </div>
    </Link>
  );
}
