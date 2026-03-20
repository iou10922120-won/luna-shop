import Link from "next/link";
import { supabase } from "@/lib/supabase";
import { ProductCard } from "@/components/product-card";
import type { Product } from "@/lib/types";

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

export const revalidate = 3600;

export default async function HomePage() {
  const [featured, newest] = await Promise.all([
    getFeaturedProducts(),
    getNewProducts(),
  ]);

  return (
    <>
      {/* Hero */}
      <section className="relative bg-gradient-to-br from-[#2C3E6B] to-[#4a5a8a] text-white">
        <div className="max-w-7xl mx-auto px-4 py-24 md:py-32">
          <p className="text-sm font-light tracking-widest text-[#B8A9C9] mb-4">
            VEGAN SKINCARE
          </p>
          <h1 className="text-4xl md:text-6xl font-bold leading-tight mb-6">
            달빛처럼,
            <br />
            투명하게.
          </h1>
          <p className="text-lg md:text-xl text-white/70 max-w-md mb-8 leading-relaxed">
            모든 성분을 투명하게 공개합니다.
            <br />
            자연 유래 원료로 만든 비건 스킨케어, LUNA.
          </p>
          <Link
            href="/products"
            className="inline-block bg-white text-[#2C3E6B] font-semibold px-8 py-3 rounded-full hover:bg-[#B8A9C9] hover:text-white transition-colors"
          >
            제품 보러가기
          </Link>
        </div>
      </section>

      {/* Brand Values */}
      <section className="max-w-7xl mx-auto px-4 py-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
          {[
            {
              icon: "🌿",
              title: "100% 비건",
              desc: "동물 실험 없이, 식물 유래 성분만 사용합니다.",
            },
            {
              icon: "🔍",
              title: "투명한 성분",
              desc: "모든 성분의 원산지, 등급, 역할을 공개합니다.",
            },
            {
              icon: "💜",
              title: "피부 과학",
              desc: "피부에 필요한 것만, 불필요한 것은 빼는 설계.",
            },
          ].map((v) => (
            <div key={v.title} className="p-6">
              <div className="text-3xl mb-3">{v.icon}</div>
              <h3 className="font-semibold text-lg mb-2">{v.title}</h3>
              <p className="text-sm text-muted-foreground">{v.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Featured (Sale) Products */}
      {featured.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 py-12">
          <div className="flex items-baseline justify-between mb-8">
            <h2 className="text-2xl font-bold">지금 할인 중</h2>
            <Link
              href="/products"
              className="text-sm text-[#2C3E6B] hover:underline"
            >
              전체 보기 →
            </Link>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
            {featured.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        </section>
      )}

      {/* New Products */}
      {newest.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 py-12 pb-20">
          <div className="flex items-baseline justify-between mb-8">
            <h2 className="text-2xl font-bold">신제품</h2>
            <Link
              href="/products"
              className="text-sm text-[#2C3E6B] hover:underline"
            >
              전체 보기 →
            </Link>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
            {newest.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        </section>
      )}
    </>
  );
}
