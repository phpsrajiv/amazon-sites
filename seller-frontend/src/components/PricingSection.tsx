import { motion } from "framer-motion";
import { Star, CheckCircle2 } from "lucide-react";
import { useTrial } from "./TrialContext";
import { Button } from "@/components/ui/button";
import { getIcon } from "@/lib/icon-map";
import type {
  OnboardingStep, Testimonial, PricingPlan,
  ResultMetric, CtaSection
} from "@/types/api";

interface PricingSectionProps {
  steps: OnboardingStep[];
  testimonials: Testimonial[];
  pricingPlans: PricingPlan[];
  resultMetrics: ResultMetric[];
  ctaSections: CtaSection[];
}

export function PricingSection({
  steps, testimonials, pricingPlans, resultMetrics, ctaSections
}: PricingSectionProps) {
  const { openTrialModal } = useTrial();

  const finalCta = ctaSections.find(c => c.title.toLowerCase().includes("final")) || ctaSections[ctaSections.length - 1];

  return (
    <>
      {/* Results Strip */}
      <section className="py-16 bg-[#131921] border-y border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-10">
            <h2 className="text-2xl font-bold text-white">Proven Results from Businesses Like Yours</h2>
          </div>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
            {resultMetrics.map((r, i) => (
              <motion.div
                key={r.id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="text-center"
              >
                <div className="text-4xl md:text-5xl font-bold text-[#FF9900] mb-2">{r.field_metric_value}</div>
                <div className="text-sm text-gray-400">{r.title}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="py-24 border-b border-gray-200 bg-[#EAEDED]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold font-display mb-4 text-[#0F1111]">Get Started in 3 Simple Steps</h2>
            <p className="text-gray-600 text-lg">No tech headaches. No learning curve. Just results.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
            <div className="hidden md:block absolute top-1/2 left-[10%] right-[10%] h-0.5 bg-gray-300 -translate-y-1/2 z-0"></div>
            {steps.map((step, i) => {
              const Icon = getIcon(step.field_step_icon);
              return (
                <motion.div
                  key={step.id}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.2 }}
                  className="relative z-10 flex flex-col items-center text-center p-6"
                >
                  <div className="w-16 h-16 rounded-full bg-white border-4 border-[#EAEDED] flex items-center justify-center mb-6 shadow-lg">
                    <Icon className="w-7 h-7 text-[#FF9900]" />
                  </div>
                  <div className="text-sm font-bold text-[#FF9900] mb-2 tracking-widest uppercase">Step {step.field_step_number}</div>
                  <h3 className="text-xl font-bold mb-3 text-[#0F1111]">{step.title}</h3>
                  <p className="text-gray-600">{step.field_step_description}</p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section id="testimonials" className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold font-display mb-4 text-[#0F1111]">Trusted by 12,000+ Happy Sellers, Brands & Agencies</h2>
            <p className="text-gray-600">Verified by Amazon · Real results, real sellers</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((t, i) => {
              const rating = parseInt(t.field_testimonial_rating) || 5;
              const displayRole = t.field_testimonial_company
                ? `${t.field_testimonial_role} — ${t.field_testimonial_company}`
                : t.field_testimonial_role;
              return (
                <motion.div
                  key={t.id}
                  initial={{ opacity: 0, scale: 0.95 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1 }}
                  className="p-8 rounded-3xl bg-white shadow-sm border border-gray-200 relative"
                >
                  <div className="flex gap-1 mb-6">
                    {Array.from({ length: rating }, (_, star) => (
                      <Star key={star} className="w-5 h-5 fill-[#FF9900] text-[#FF9900]" />
                    ))}
                  </div>
                  <p className="text-base mb-8 leading-relaxed font-medium text-[#0F1111]">"{t.field_testimonial_body}"</p>
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-[#131921] flex items-center justify-center text-white font-bold text-lg flex-shrink-0">
                      {t.field_testimonial_author.charAt(0)}
                    </div>
                    <div>
                      <div className="font-bold text-[#0F1111]">{t.field_testimonial_author}</div>
                      <div className="text-sm text-gray-500">{displayRole}</div>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-24 relative overflow-hidden bg-[#F3F3F3]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold font-display mb-4 text-[#0F1111]">Simple, Transparent Pricing</h2>
            <p className="text-gray-600 text-lg">Start free. Scale as you grow. No hidden fees.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto items-center">
            {pricingPlans.map((plan, i) => {
              const isHighlighted = plan.field_plan_highlighted === "1";
              const planFeatures = plan.field_plan_features ? plan.field_plan_features.split("|").filter(Boolean) : [];
              const price = Math.round(parseFloat(plan.field_plan_price));

              return (
                <motion.div
                  key={plan.id}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1 }}
                  className={`p-8 rounded-3xl ${
                    isHighlighted
                      ? "bg-white border-2 border-[#FF9900] relative transform md:-translate-y-4 shadow-xl"
                      : "bg-white border border-gray-200 shadow-sm"
                  }`}
                >
                  {plan.field_plan_badge && (
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 px-4 py-1 bg-[#FF9900] text-[#0F1111] text-xs font-bold rounded-full uppercase tracking-wider">
                      {plan.field_plan_badge}
                    </div>
                  )}
                  <h3 className="text-xl font-bold mb-1 text-[#0F1111]">{plan.title}</h3>
                  <p className="text-sm text-gray-500 mb-4">{plan.field_plan_subtitle}</p>
                  <div className="mb-6">
                    <span className={`${isHighlighted ? "text-5xl" : "text-4xl"} font-bold text-[#0F1111]`}>
                      {plan.field_plan_currency}{price}
                    </span>
                    <span className="text-gray-500">{plan.field_plan_billing_period}</span>
                  </div>
                  <ul className="space-y-3 mb-8 text-sm text-[#0F1111]">
                    {planFeatures.map((f, j) => (
                      <li key={j} className="flex items-center gap-3">
                        <CheckCircle2 className="w-4 h-4 text-[#FF9900] flex-shrink-0" />
                        {f}
                      </li>
                    ))}
                  </ul>
                  <Button
                    onClick={openTrialModal}
                    variant={isHighlighted ? "default" : "outline"}
                    className={
                      isHighlighted
                        ? "w-full bg-[#FF9900] hover:bg-[#FA8900] text-[#0F1111] font-bold shadow-md rounded-md"
                        : "w-full bg-white border-gray-300 text-[#0F1111] hover:bg-gray-50 font-bold rounded-md"
                    }
                  >
                    {plan.field_plan_cta_text || "Start Free Trial"}
                  </Button>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      {finalCta && (
        <section className="py-24 relative overflow-hidden bg-[#131921]">
          <div className="max-w-4xl mx-auto px-4 text-center relative z-10">
            <motion.div initial={{ opacity: 0, scale: 0.9 }} whileInView={{ opacity: 1, scale: 1 }} viewport={{ once: true }}>
              {finalCta.field_cta_badge && (
                <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#FF9900]/10 border border-[#FF9900]/30 text-[#FF9900] text-sm font-semibold mb-6">
                  {finalCta.field_cta_badge}
                </div>
              )}
              <h2 className="text-5xl md:text-6xl font-bold font-display text-white mb-6">
                AI-powered decisions.<br />Results you can trust.
              </h2>
              <p className="text-xl text-white/70 mb-10 max-w-2xl mx-auto">
                {finalCta.field_cta_subheading}
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <Button onClick={openTrialModal} size="lg" className="h-16 px-10 text-lg bg-[#FF9900] text-[#0F1111] hover:bg-[#FA8900] font-bold shadow-xl hover:scale-105 transition-all rounded-md">
                  {finalCta.field_cta_primary_text || "Get a Free Audit Report"}
                </Button>
                <Button onClick={openTrialModal} variant="outline" size="lg" className="h-16 px-10 text-lg border-white/20 text-white hover:bg-white/10 transition-all rounded-md">
                  {finalCta.field_cta_secondary_text || "Request a Demo"}
                </Button>
              </div>
            </motion.div>
          </div>
        </section>
      )}
    </>
  );
}
