import { supabase } from "@/lib/supabase";
import { ProductCard } from "@/components/product-card";
import type { Product, Category } from "@/lib/types";
import { ProductListTracker } from "./product-list-tracker";

interface Props {
  searchParams: Promise<{ category?: string }>;
}

async function getCategories(): Promise<Category[]> {
  const { data } = await supabase
    .from("categories")
    .select("*")
    .order("display_order");
  return data ?? [];
}

async function getProducts(categorySlug?: string): Promise<Product[]> {
  let query = supabase
    .from("products")
    .select("*, category:categories(*)");

  if (categorySlug) {
    const { data: cat } = await supabase
      .from("categories")
      .select("id")
      .eq("slug", categorySlug)
      .single();
    if (cat) {
      query = query.eq("category_id", cat.id);
    }
  }

  const { data } = await query.order("name");
  return data ?? [];
}

export const revalidate = 3600;

export default async function ProductsPage({ searchParams }: Props) {
  const params = await searchParams;
  const categorySlug = params.category;
  const [categories, products] = await Promise.all([
    getCategories(),
    getProducts(categorySlug),
  ]);

  return (
    <div className="max-w-7xl mx-auto px-4 py-10">
      <ProductListTracker category={categorySlug} />
      {/* Title */}
      <h1 className="text-3xl font-bold mb-8">
        {categorySlug
          ? categories.find((c) => c.slug === categorySlug)?.name ?? "상품"
          : "전체 상품"}
      </h1>

      {/* Category Filter */}
      <div className="flex gap-2 mb-8 overflow-x-auto pb-2">
        <a
          href="/products"
          className={`px-4 py-2 rounded-full text-sm whitespace-nowrap border transition-colors ${
            !categorySlug
              ? "bg-[#2C3E6B] text-white border-[#2C3E6B]"
              : "bg-white border-border text-muted-foreground hover:border-[#2C3E6B]"
          }`}
        >
          전체
        </a>
        {categories.map((cat) => (
          <a
            key={cat.id}
            href={`/products?category=${cat.slug}`}
            className={`px-4 py-2 rounded-full text-sm whitespace-nowrap border transition-colors ${
              categorySlug === cat.slug
                ? "bg-[#2C3E6B] text-white border-[#2C3E6B]"
                : "bg-white border-border text-muted-foreground hover:border-[#2C3E6B]"
            }`}
          >
            {cat.name}
          </a>
        ))}
      </div>

      {/* Product Grid */}
      {products.length > 0 ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 md:gap-6">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      ) : (
        <div className="text-center py-20 text-muted-foreground">
          <p>해당 카테고리에 상품이 없습니다.</p>
        </div>
      )}
    </div>
  );
}
