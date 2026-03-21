import mixpanel from 'mixpanel-browser';

let initialized = false;

export function initMixpanel() {
  const token = process.env.NEXT_PUBLIC_MIXPANEL_TOKEN;
  if (!token || initialized) return;

  mixpanel.init(token, {
    track_pageview: false,
    persistence: 'localStorage',
  });
  initialized = true;
}

export function trackMixpanel(event: string, properties: Record<string, unknown> = {}) {
  if (!initialized) return;
  mixpanel.track(event, properties);
}
