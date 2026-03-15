import { useQuery } from "@tanstack/react-query";
import { fetchLandingPageData } from "@/lib/api";
import type { LandingPageData } from "@/types/api";

export function useLandingPageData() {
  return useQuery<LandingPageData>({
    queryKey: ["landing-page"],
    queryFn: fetchLandingPageData,
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
  });
}
