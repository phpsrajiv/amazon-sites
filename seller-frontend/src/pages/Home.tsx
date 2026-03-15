import { Layout } from "@/components/Layout";
import { SEO } from "@/components/SEO";
import { HeroSection } from "@/components/HeroSection";
import { FeatureSection } from "@/components/FeatureSection";
import { PricingSection } from "@/components/PricingSection";
import { useLandingPageData } from "@/hooks/use-landing-data";
import { Loader2, AlertTriangle } from "lucide-react";

const SITE_URL = import.meta.env.VITE_SITE_URL || "https://selleragent.ai";

const organizationJsonLd = {
  "@context": "https://schema.org",
  "@type": "Organization",
  name: "SellerAgent AI",
  url: SITE_URL,
  logo: `${SITE_URL}/favicon.svg`,
  description:
    "AI-powered Amazon advertising automation platform. Increase rankings, lower ACOS, and scale effortlessly.",
};

export default function Home() {
  const { data, isLoading, isError, error } = useLandingPageData();

  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <Loader2 className="size-8 text-[#FF9900] animate-spin" />
        </div>
      </Layout>
    );
  }

  if (isError || !data) {
    return (
      <Layout>
        <div className="max-w-xl mx-auto mt-32 px-4">
          <div className="rounded-xl border border-red-200 bg-red-50 p-6 flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-red-800">Failed to load page content</h3>
              <p className="text-sm text-red-600 mt-1">
                {error?.message || "Please try refreshing the page."}
              </p>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <>
      <SEO
        title={data.seo?.title}
        description={data.seo?.description}
        canonicalUrl={SITE_URL}
        ogType="website"
        jsonLd={organizationJsonLd}
      />
      <Layout>
        <HeroSection slides={data.hero_slides} stats={data.stats} />
      <FeatureSection
        painPoints={data.pain_points}
        features={data.features}
        audienceTypes={data.audience_types}
      />
      <PricingSection
        steps={data.onboarding_steps}
        testimonials={data.testimonials}
        pricingPlans={data.pricing_plans}
        resultMetrics={data.result_metrics}
        ctaSections={data.cta_sections}
      />
      </Layout>
    </>
  );
}
