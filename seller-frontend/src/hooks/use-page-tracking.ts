import { useEffect } from "react";
import { useLocation } from "wouter";

declare global {
  interface Window {
    dataLayer: Record<string, unknown>[];
  }
}

/**
 * Tracks SPA route changes by pushing virtual pageview events to GTM dataLayer.
 * Call this hook once inside the Router component.
 */
export function usePageTracking() {
  const [location] = useLocation();

  useEffect(() => {
    if (window.dataLayer) {
      window.dataLayer.push({
        event: "virtualPageview",
        page: location,
        pageTitle: document.title,
      });
    }
  }, [location]);
}
