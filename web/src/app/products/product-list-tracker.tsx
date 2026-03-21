'use client';

import { useEffect, useRef } from 'react';
import { track, AnalyticsEvent } from '@/lib/analytics';

interface Props {
  category?: string;
}

export function ProductListTracker({ category }: Props) {
  const prevCategory = useRef(category);

  useEffect(() => {
    track(AnalyticsEvent.PRODUCT_LIST_VIEW, {
      category: category ?? undefined,
    });
  }, [category]);

  useEffect(() => {
    if (prevCategory.current !== category && category) {
      track(AnalyticsEvent.PRODUCT_LIST_FILTER, {
        filter_type: 'category',
        filter_value: category,
      });
    }
    prevCategory.current = category;
  }, [category]);

  return null;
}
