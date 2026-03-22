import Link from "next/link";
import Image from "next/image";
import { supabase } from "@/lib/supabase";
import { ProductCard } from "@/components/product-card";
import type { Product } from "@/lib/types";
import { HERO_IMAGE } from "@/lib/images";

async function getFeaturedProducts(): Promise<Product[]> {
  const { data } = await supabase
    .from("products")
    .select("*, category:categories(*)")
    .not("sale_price", "is", null)
    .order("created_at", { ascending: false })
    .limit(8);
  return data ?? [];
}

async function getNewProducts(): Promise<Product[]> {
  const { data } = await supabase
    .from("products")
    .select("*, category:categories(*)")
    .order("created_at", { ascending: false })
    .limit(4);
  return data ?? [];
}

async function getBestProducts(): Promise<Product[]> {
  const { data } = await supabase
    .from("products")
    .select("*, category:categories(*)")
    .order("stock_quantity", { ascending: true })
    .limit(4);
  return data ?? [];
}

export const revalidate = 3600;

export default async function HomePage() {
  const [featured, newest, best] = await Promise.all([
    getFeaturedProducts(),
    getNewProducts(),
    getBestProducts(),
  ]);

  return (
    <>
      {/* Hero Banner — SK-II 스타일: 밝은 배경 + 제품 이미지 왼쪽 + 텍스트 오른쪽 */}
      <section className="relative bg-gradient-to-br from-[#faf8f5] via-white to-[#f0ecf5] overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 py-8 md:py-12 grid grid-cols-1 md:grid-cols-2 gap-4 items-center min-h-[280px] md:min-h-[340px]">
          {/* 제품 이미지 */}
          <div className="relative h-48 md:h-72">
            <Image
              src={HERO_IMAGE}
              alt="LUNA 비건 스킨케어 제품"
              fill
              className="object-contain"
              priority
              sizes="(max-width: 768px) 100vw, 50vw"
            />
          </div>
          {/* 텍스트 */}
          <div className="text-center md:text-left">
            <p className="text-xs tracking-widest text-[#B8A9C9] font-medium mb-2">
              VEGAN SKINCARE
            </p>
            <h1 className="text-2xl md:text-4xl font-bold leading-tight text-[#2C3E6B] mb-2">
              LUNA
            </h1>
            <h2 className="text-lg md:text-2xl font-bold text-[#333] mb-1">
              달빛처럼, 투명하게.
            </h2>
            <p className="text-sm text-muted-foreground mb-5">
              자연 유래 원료 · 투명한 성분 · 비건 인증
            </p>
            <div className="flex gap-3 justify-center md:justify-start">
              <Link
                href="/products"
                className="bg-[#2C3E6B] text-white text-sm font-semibold px-6 py-2.5 rounded-full hover:bg-[#1e2d4f] transition-colors"
              >
                제품 보러가기
              </Link>
              <Link
                href="/about"
                className="border border-[#2C3E6B] text-[#2C3E6B] text-sm font-semibold px-6 py-2.5 rounded-full hover:bg-[#2C3E6B] hover:text-white transition-colors"
              >
                더 알아보기
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* 브랜드 가치 — 한 줄 컴팩트 */}
      <section className="border-b border-border">
        <div className="max-w-7xl mx-auto px-4 py-5">
          <div className="grid grid-cols-3 gap-4 text-center">
            {[
              { icon: "🌿", title: "100% 비건", desc: "식물 유래 성분만 사용" },
              { icon: "🔍", title: "성분 투명 공개", desc: "원산지·등급 모두 공개" },
              { icon: "🧪", title: "피부 과학 설계", desc: "필요한 것만 담은 처방" },
            ].map((v) => (
              <div key={v.title} className="flex items-center justify-center gap-2.5">
                <span className="text-xl">{v.icon}</span>
                <div className="text-left">
                  <p className="text-sm font-semibold">{v.title}</p>
                  <p className="text-xs text-muted-foreground">{v.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 메인 컨텐츠 영역 */}
      <div className="max-w-7xl mx-auto px-4 py-8 space-y-10">

        {/* 베스트 상품 + 할인 상품 — 2단 레이아웃 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 베스트 */}
          {best.length > 0 && (
            <section>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-bold">베스트 상품</h2>
                <Link href="/products" className="text-xs text-muted-foreground hover:text-[#2C3E6B]">
                  더보기 &gt;
                </Link>
              </div>
              <div className="grid grid-cols-2 gap-3">
                {best.map((product) => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>
            </section>
          )}

          {/* 추천 (신제품) */}
          {newest.length > 0 && (
            <section>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-bold">신제품</h2>
                <Link href="/products" className="text-xs text-muted-foreground hover:text-[#2C3E6B]">
                  더보기 &gt;
                </Link>
              </div>
              <div className="grid grid-cols-2 gap-3">
                {newest.map((product) => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>
            </section>
          )}
        </div>

        {/* 할인 상품 — 풀 와이드 */}
        {featured.length > 0 && (
          <section>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold">지금 할인 중 🔥</h2>
              <Link href="/products" className="text-xs text-muted-foreground hover:text-[#2C3E6B]">
                더보기 &gt;
              </Link>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
              {featured.map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          </section>
        )}

        {/* 브랜드 배너 */}
        <section className="bg-gradient-to-r from-[#f0ece6] to-[#e8e0f0] rounded-xl p-6 md:p-8 flex items-center justify-between">
          <div>
            <p className="text-xs text-muted-foreground mb-1">LUNA STORY</p>
            <h3 className="text-base md:text-lg font-bold mb-1">
              투명한 성분, 투명한 가격
            </h3>
            <p className="text-sm text-muted-foreground">
              LUNA가 추구하는 비건 스킨케어 철학을 만나보세요.
            </p>
          </div>
          <Link
            href="/about"
            className="shrink-0 text-sm font-medium text-[#2C3E6B] border border-[#2C3E6B] px-4 py-2 rounded-full hover:bg-[#2C3E6B] hover:text-white transition-colors"
          >
            브랜드 스토리
          </Link>
        </section>
      </div>
    </>
  );
}
