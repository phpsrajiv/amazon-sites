export interface HeroSlide {
  id: string;
  title: string;
  field_slide_tag: string;
  field_slide_description: string;
  field_slide_image: string;
  field_slide_weight: string;
}

export interface StatCard {
  id: string;
  title: string;
  field_stat_value: string;
  field_stat_prefix: string;
  field_stat_suffix: string;
  field_stat_icon: string;
  field_stat_weight: string;
}

export interface PainPoint {
  id: string;
  title: string;
  field_pain_description: string;
  field_pain_icon: string;
  field_pain_weight: string;
}

export interface Feature {
  id: string;
  title: string;
  field_feature_description: string;
  field_feature_icon: string;
  field_feature_bullets: string;
  field_feature_category: string;
  field_feature_weight: string;
}

export interface AudienceType {
  id: string;
  title: string;
  field_audience_description: string;
  field_audience_icon: string;
  field_audience_weight: string;
}

export interface OnboardingStep {
  id: string;
  title: string;
  field_step_description: string;
  field_step_icon: string;
  field_step_number: string;
}

export interface Testimonial {
  id: string;
  title: string;
  field_testimonial_author: string;
  field_testimonial_role: string;
  field_testimonial_company: string;
  field_testimonial_body: string;
  field_testimonial_rating: string;
  field_testimonial_avatar: string;
  field_testimonial_weight: string;
}

export interface PricingPlan {
  id: string;
  title: string;
  field_plan_subtitle: string;
  field_plan_price: string;
  field_plan_currency: string;
  field_plan_billing_period: string;
  field_plan_features: string;
  field_plan_highlighted: string;
  field_plan_badge: string;
  field_plan_cta_text: string;
  field_plan_cta_url: string;
  field_plan_weight: string;
}

export interface ResultMetric {
  id: string;
  title: string;
  field_metric_value: string;
  field_metric_icon: string;
  field_metric_weight: string;
}

export interface CtaSection {
  id: string;
  title: string;
  field_cta_subheading: string;
  field_cta_badge: string;
  field_cta_primary_text: string;
  field_cta_primary_url: string;
  field_cta_secondary_text: string;
  field_cta_secondary_url: string;
}

export interface SiteSettings {
  site_name: string;
  site_slogan: string;
}

export interface LandingPageData {
  hero_slides: HeroSlide[];
  stats: StatCard[];
  pain_points: PainPoint[];
  features: Feature[];
  audience_types: AudienceType[];
  onboarding_steps: OnboardingStep[];
  testimonials: Testimonial[];
  pricing_plans: PricingPlan[];
  result_metrics: ResultMetric[];
  cta_sections: CtaSection[];
  site_settings: SiteSettings;
}

export interface BlogPost {
  id: string;
  title: string;
  field_blog_body: string;
  field_blog_summary: string;
  field_blog_image: string;
  field_blog_author: string;
  field_blog_category: string;
  field_blog_date: string;
  field_blog_weight: string;
}

export interface DrupalLoginResponse {
  current_user: {
    uid: string;
    roles: string[];
    name: string;
  };
  csrf_token: string;
  logout_token: string;
}

export interface AuthUser {
  uid: string;
  name: string;
}

export interface TrialSignupRequest {
  name: string;
  email: string;
  storeUrl?: string;
}

export interface TrialSignupResponse {
  success: boolean;
  message: string;
  user_id?: string;
}
