import { notFound } from "next/navigation";
import { supabase } from "@/lib/supabase";
import type { Product, Review } from "@/lib/types";
import { AddToCartButton } from "./add-to-cart-button";
import { formatPrice, discountRate } from "@/lib/format";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";

interface Props {
  params: Promise<{ slug: string }>;
}

async function getProduct(slug: string): Promise<Product | null> {
  const { data } = await supabase
    .from("products")
    .select("*, category:categories(*)")
    .eq("slug", slug)
    .single();
  return data;
}

async function getReviews(productId: string): Promise<Review[]> {
  const { data } = await supabase
    .from("reviews")
    .select("*")
    .eq("product_id", productId)
    .order("created_at", { ascending: false })
    .limit(10);
  return data ?? [];
}

export const revalidate = 3600;

export default async function ProductDetailPage({ params }: Props) {
  const { slug } = await params;
  const product = await getProduct(slug);
  if (!product) notFound();

  const reviews = await getReviews(product.id);
  const avgRating =
    reviews.length > 0
      ? (reviews.reduce((s, r) => s + r.rating, 0) / reviews.length).toFixed(1)
      : null;

  const hasDiscount = product.sale_price && product.sale_price < product.price;

  return (
    <div className="max-w-7xl mx-auto px-4 py-10">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
        {/* Image */}
        <div className="aspect-square bg-gradient-to-br from-[#f0ece6] to-[#e8e0f0] rounded-2xl flex items-center justify-center">
          <span className="text-8xl opacity-20">🌙</span>
        </div>

        {/* Info */}
        <div>
          <p className="text-sm text-muted-foreground mb-1">
            {product.category?.name}
          </p>
          <h1 className="text-2xl md:text-3xl font-bold mb-4">
            {product.name}
          </h1>

          {/* Rating */}
          {avgRating && (
            <div className="flex items-center gap-2 mb-4">
              <span className="text-yellow-500">{"★".repeat(Math.round(Number(avgRating)))}</span>
              <span className="text-sm text-muted-foreground">
                {avgRating} ({reviews.length}개 리뷰)
              </span>
            </div>
          )}

          {/* Price */}
          <div className="flex items-baseline gap-3 mb-6">
            {hasDiscount ? (
              <>
                <span className="text-sm font-semibold text-red-500">
                  {discountRate(product.price, product.sale_price!)}
                </span>
                <span className="text-3xl font-bold text-[#2C3E6B]">
                  {formatPrice(product.sale_price!)}
                </span>
                <span className="text-lg text-muted-foreground line-through">
                  {formatPrice(product.price)}
                </span>
              </>
            ) : (
              <span className="text-3xl font-bold">
                {formatPrice(product.price)}
              </span>
            )}
          </div>

          {/* Badges */}
          <div className="flex gap-2 mb-6">
            {product.is_vegan_certified && (
              <Badge variant="outline" className="border-green-500 text-green-700">
                비건 인증
              </Badge>
            )}
            <Badge variant="outline">
              {product.stock_quantity > 0
                ? `재고 ${product.stock_quantity}개`
                : "품절"}
            </Badge>
          </div>

          {/* Description */}
          <p className="text-sm text-muted-foreground leading-relaxed mb-6">
            {product.description}
          </p>

          {/* Add to Cart */}
          <AddToCartButton product={product} />

          <Separator className="my-8" />

          {/* Ingredients */}
          {product.ingredient_details && product.ingredient_details.length > 0 && (
            <div>
              <h2 className="text-lg font-semibold mb-4">성분 정보</h2>
              <div className="space-y-3">
                {product.ingredient_details.map((ing) => (
                  <div
                    key={ing.name}
                    className="flex items-center justify-between text-sm bg-muted/50 rounded-lg p-3"
                  >
                    <div>
                      <span className="font-medium">{ing.name}</span>
                      <span className="text-muted-foreground ml-2">
                        {ing.role}
                      </span>
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {ing.origin} · {ing.grade}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Reviews */}
      {reviews.length > 0 && (
        <section className="mt-16">
          <h2 className="text-xl font-bold mb-6">
            리뷰 ({reviews.length})
          </h2>
          <div className="space-y-4">
            {reviews.map((review) => (
              <div
                key={review.id}
                className="bg-white border border-border rounded-lg p-4"
              >
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-yellow-500 text-sm">
                    {"★".repeat(review.rating)}
                    {"☆".repeat(5 - review.rating)}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {new Date(review.created_at).toLocaleDateString("ko-KR")}
                  </span>
                </div>
                <p className="text-sm">{review.content}</p>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
