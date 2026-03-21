'use client';

import { useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { initAnalytics, track, AnalyticsEvent } from '@/lib/analytics';

export function AnalyticsProvider({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  useEffect(() => {
    initAnalytics();
  }, []);

  useEffect(() => {
    track(AnalyticsEvent.PAGE_VIEW, {
      page_path: pathname,
      page_title: document.title,
    });
  }, [pathname]);

  return <>{children}</>;
}
