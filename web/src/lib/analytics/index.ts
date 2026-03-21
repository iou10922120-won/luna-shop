import { pushToDataLayer } from './gtm';
import { initAmplitude, trackAmplitude } from './amplitude';
import { initMixpanel, trackMixpanel } from './mixpanel';
import type { AnalyticsEvent, EventPropertiesMap } from './types';

const isDev = process.env.NODE_ENV === 'development';

export function initAnalytics() {
  initAmplitude();
  initMixpanel();
}

export function track<E extends AnalyticsEvent>(
  event: E,
  properties: EventPropertiesMap[E]
) {
  const props = properties as Record<string, unknown>;

  pushToDataLayer(event, props);
  trackAmplitude(event, props);
  trackMixpanel(event, props);

  if (isDev) {
    console.log(`[Analytics] ${event}`, props);
  }
}

export { AnalyticsEvent } from './types';
export type { EventPropertiesMap } from './types';
