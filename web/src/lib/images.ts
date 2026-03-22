// Unsplash 무료 이미지 (상업적 이용 가능, 출처 표기 불필요)

// 히어로: 스킨케어 제품 이미지 (SK-II 스타일 배너)
export const HERO_IMAGE =
  'https://images.unsplash.com/photo-1612817288484-6f916006741a?auto=format&fit=crop&w=900&q=80';

// 카테고리별 상품 이미지 (각 카테고리 10개 상품에 순환 배정)
const PRODUCT_IMAGES: Record<string, string[]> = {
  cleanser: [
    'https://images.unsplash.com/photo-1556228578-0d85b1a4d571?auto=format&fit=crop&w=400&q=80',
    'https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=400&q=80',
    'https://images.unsplash.com/photo-1631729371254-42c2892f0e6e?auto=format&fit=crop&w=400&q=80',
  ],
  toner: [
    'https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?auto=format&fit=crop&w=400&q=80',
    'https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?auto=format&fit=crop&w=400&q=80',
    'https://images.unsplash.com/photo-1611930022073-b7a4ba5fcccd?auto=format&fit=crop&w=400&q=80',
  ],
  serum: [
    'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=400&q=80',
    'https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?auto=format&fit=crop&w=400&q=80',
    'https://images.unsplash.com/photo-1556228578-0d85b1a4d571?auto=format&fit=crop&w=400&q=80',
  ],
  cream: [
    'https://images.unsplash.com/photo-1611930022073-b7a4ba5fcccd?auto=format&fit=crop&w=400&q=80',
    'https://images.unsplash.com/photo-1512290923902-8a9f81dc236c?auto=format&fit=crop&w=400&q=80',
    'https://images.unsplash.com/photo-1601049541289-9b1b7bbbfe19?auto=format&fit=crop&w=400&q=80',
  ],
  sunscreen: [
    'https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=400&q=80',
    'https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?auto=format&fit=crop&w=400&q=80',
    'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=400&q=80',
  ],
};

const DEFAULT_IMAGE =
  'https://images.unsplash.com/photo-1556228578-0d85b1a4d571?auto=format&fit=crop&w=400&q=80';

/**
 * 상품의 카테고리 slug + 인덱스로 이미지 URL 반환
 * slug가 "cleanser-01"이면 카테고리 "cleanser", 인덱스 0
 */
export function getProductImage(slug: string): string {
  const parts = slug.split('-');
  const categorySlug = parts.slice(0, -1).join('-');
  const index = parseInt(parts[parts.length - 1] || '1', 10) - 1;

  const images = PRODUCT_IMAGES[categorySlug];
  if (!images) return DEFAULT_IMAGE;
  return images[index % images.length];
}

/**
 * 카테고리 slug로 대표 이미지 URL 반환
 */
export function getCategoryImage(categorySlug: string): string {
  const images = PRODUCT_IMAGES[categorySlug];
  return images?.[0] ?? DEFAULT_IMAGE;
}
