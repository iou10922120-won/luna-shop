'use client';

import { useEffect } from 'react';
import { track, AnalyticsEvent } from '@/lib/analytics';

interface Props {
  productId: string;
  productName: string;
  category: string;
  price: number;
  salePrice: number | null;
  hasIngredients?: boolean;
}

export function ProductTracker({ productId, productName, category, price, salePrice, hasIngredients }: Props) {
  useEffect(() => {
    track(AnalyticsEvent.PRODUCT_VIEW, {
      product_id: productId,
      product_name: productName,
      category,
      price,
      sale_price: salePrice,
    });

    if (hasIngredients) {
      track(AnalyticsEvent.INGREDIENT_VIEW, {
        product_id: productId,
        product_name: productName,
      });
    }
  }, [productId, productName, category, price, salePrice, hasIngredients]);

  return null;
}
