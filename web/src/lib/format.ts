/** 원화 포맷: 29000 → "29,000원" */
export function formatPrice(price: number): string {
  return price.toLocaleString("ko-KR") + "원";
}

/** 할인율 계산: (price, salePrice) → "17%" */
export function discountRate(price: number, salePrice: number): string {
  const rate = Math.round(((price - salePrice) / price) * 100);
  return `${rate}%`;
}
