import * as amplitude from '@amplitude/analytics-browser';

let initialized = false;

export function initAmplitude() {
  const apiKey = process.env.NEXT_PUBLIC_AMPLITUDE_API_KEY;
  if (!apiKey || initialized) return;

  amplitude.init(apiKey, {
    defaultTracking: false,
  });
  initialized = true;
}

export function trackAmplitude(event: string, properties: Record<string, unknown> = {}) {
  if (!initialized) return;
  amplitude.track(event, properties);
}
