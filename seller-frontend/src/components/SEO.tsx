import { Helmet } from "react-helmet-async";

const SITE_NAME = "SellerBuddy";
const SITE_URL = import.meta.env.VITE_SITE_URL || "https://sellerbuddy.app";
const DEFAULT_OG_IMAGE = `${SITE_URL}/opengraph.jpg`;
const DEFAULT_DESCRIPTION =
  "Automate your Amazon advertising with intelligent AI agents. Increase rankings, lower ACOS, and scale effortlessly.";

interface SEOProps {
  title?: string;
  description?: string;
  canonicalUrl?: string;
  ogTitle?: string;
  ogDescription?: string;
  ogImage?: string;
  ogType?: "website" | "article";
  twitterCard?: "summary" | "summary_large_image";
  articleAuthor?: string;
  articlePublishedTime?: string;
  articleSection?: string;
  noindex?: boolean;
  jsonLd?: Record<string, unknown>;
}

export function SEO({
  title,
  description = DEFAULT_DESCRIPTION,
  canonicalUrl,
  ogTitle,
  ogDescription,
  ogImage = DEFAULT_OG_IMAGE,
  ogType = "website",
  twitterCard = "summary_large_image",
  articleAuthor,
  articlePublishedTime,
  articleSection,
  noindex = false,
  jsonLd,
}: SEOProps) {
  const fullTitle = title || `${SITE_NAME} | AI-Powered Amazon Advertising Automation`;
  const resolvedCanonical = canonicalUrl || SITE_URL;

  return (
    <Helmet>
      <title>{fullTitle}</title>
      <meta name="description" content={description} />
      <link rel="canonical" href={resolvedCanonical} />

      {noindex && <meta name="robots" content="noindex, nofollow" />}

      {/* Open Graph */}
      <meta property="og:title" content={ogTitle || fullTitle} />
      <meta property="og:description" content={ogDescription || description} />
      <meta property="og:type" content={ogType} />
      <meta property="og:url" content={resolvedCanonical} />
      <meta property="og:site_name" content={SITE_NAME} />
      {ogImage && <meta property="og:image" content={ogImage} />}

      {/* Twitter Cards */}
      <meta name="twitter:card" content={twitterCard} />
      <meta name="twitter:title" content={ogTitle || fullTitle} />
      <meta
        name="twitter:description"
        content={ogDescription || description}
      />
      {(ogImage) && (
        <meta name="twitter:image" content={ogImage} />
      )}

      {/* Article-specific */}
      {articleAuthor && (
        <meta property="article:author" content={articleAuthor} />
      )}
      {articlePublishedTime && (
        <meta
          property="article:published_time"
          content={articlePublishedTime}
        />
      )}
      {articleSection && (
        <meta property="article:section" content={articleSection} />
      )}

      {/* JSON-LD Structured Data */}
      {jsonLd && (
        <script type="application/ld+json">{JSON.stringify(jsonLd)}</script>
      )}
    </Helmet>
  );
}
