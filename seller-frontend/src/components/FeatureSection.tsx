import { motion } from "framer-motion";
import {
  Bot, Zap, BarChart3, Sparkles, Target,
  CheckCircle2, Users, BrainCircuit
} from "lucide-react";
import { getIcon } from "@/lib/icon-map";
import type { PainPoint, Feature, AudienceType } from "@/types/api";

const audienceColors = ["bg-[#FF9900]", "bg-[#007185]", "bg-[#131921]"];

interface FeatureSectionProps {
  painPoints: PainPoint[];
  features: Feature[];
  audienceTypes: AudienceType[];
}

export function FeatureSection({ painPoints, features, audienceTypes }: FeatureSectionProps) {
  return (
    <div className="bg-white">
      {/* Problems Section */}
      <section className="py-24 border-y border-gray-200 bg-[#EAEDED] relative">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#00000005_1px,transparent_1px),linear-gradient(to_bottom,#00000005_1px,transparent_1px)] bg-[size:4rem_4rem]"></div>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center max-w-2xl mx-auto mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold font-display mb-4 text-[#0F1111]">Running Amazon Ads Shouldn't Feel Like a Gamble.</h2>
            <p className="text-gray-600 text-lg">Without intelligent automation, you're constantly fighting algorithms, overspending on ads, and losing ground to competitors who have AI working for them.</p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {painPoints.map((prob, i) => {
              const Icon = getIcon(prob.field_pain_icon);
              return (
                <motion.div
                  key={prob.id}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1 }}
                  className="p-6 rounded-2xl bg-white border border-gray-200 shadow-sm hover:shadow-md hover:border-[#FF9900]/30 transition-all group"
                >
                  <div className="w-12 h-12 rounded-xl bg-red-50 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                    <Icon className="w-6 h-6 text-[#C40000]" />
                  </div>
                  <h3 className="font-semibold text-lg mb-2 text-[#0F1111]">{prob.title}</h3>
                  <p className="text-sm text-gray-600 leading-relaxed">{prob.field_pain_description}</p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Solution Section */}
      <section className="py-32 overflow-hidden bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <motion.div
              initial={{ opacity: 0, x: -40 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
            >
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#FF9900]/10 text-[#0F1111] text-sm font-semibold mb-6 border border-[#FF9900]/20">
                <Bot className="w-4 h-4 text-[#FF9900]" />
                <span>Meet SellerBuddy — Your Amazon Ads Co-Pilot</span>
              </div>
              <h2 className="text-4xl md:text-5xl font-bold font-display mb-6 leading-tight text-[#0F1111]">
                Easy Setup. <br /><span className="text-[#FF9900]">Instant Results.</span>
              </h2>
              <p className="text-xl text-gray-600 mb-8">
                Get started without tech headaches. Connect your Amazon account, set your goals, and let SellerBuddy do the heavy lifting — no complex setup, no learning curve.
              </p>

              <ul className="space-y-5">
                {[
                  { text: "Sync your Amazon Ads account in 60 seconds. Secure. Seamless.", icon: Zap },
                  { text: "Select your budget and ACoS targets — we tailor campaigns around them.", icon: Target },
                  { text: "Autopilot adjusts bids, identifies waste, and scales winning campaigns daily.", icon: BarChart3 },
                ].map((item, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <div className="w-7 h-7 rounded-full bg-[#FF9900]/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <item.icon className="w-4 h-4 text-[#FF9900]" />
                    </div>
                    <span className="text-[#0F1111] font-medium leading-relaxed">{item.text}</span>
                  </li>
                ))}
              </ul>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              className="relative"
            >
              <div className="absolute -inset-4 bg-[#FF9900]/10 blur-2xl opacity-50 rounded-[3rem] animate-pulse"></div>
              <div className="relative rounded-[2rem] p-8 bg-white border border-gray-200 shadow-2xl overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-[#F3F3F3] via-transparent to-transparent"></div>

                <div className="relative z-10 flex flex-col gap-4">
                  <div className="flex items-center gap-4 p-4 rounded-xl bg-white border border-gray-100 shadow-sm">
                    <div className="w-10 h-10 rounded-full bg-[#FF9900] flex items-center justify-center shadow-lg shadow-[#FF9900]/30"><Zap className="w-5 h-5 text-white" /></div>
                    <div className="flex-1">
                      <div className="font-semibold text-[#0F1111]">Autopilot Engine</div>
                      <div className="text-sm text-green-600 font-medium">1,284 bid adjustments today</div>
                    </div>
                    <div className="text-xs bg-green-50 text-green-700 px-2 py-1 rounded font-bold">LIVE</div>
                  </div>
                  <div className="flex items-center gap-4 p-4 rounded-xl bg-white border border-gray-100 shadow-sm ml-6">
                    <div className="w-10 h-10 rounded-full bg-[#007185] flex items-center justify-center shadow-lg shadow-[#007185]/30"><BarChart3 className="w-5 h-5 text-white" /></div>
                    <div>
                      <div className="font-semibold text-[#0F1111]">Budget Reallocator</div>
                      <div className="text-sm text-gray-600">Moved $842 to top ASINs</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 p-4 rounded-xl bg-white border border-gray-100 shadow-sm">
                    <div className="w-10 h-10 rounded-full bg-[#131921] flex items-center justify-center shadow-lg"><BrainCircuit className="w-5 h-5 text-white" /></div>
                    <div>
                      <div className="font-semibold text-[#0F1111]">Agentic AI Chat</div>
                      <div className="text-sm text-green-600 font-medium">47 wasteful keywords paused</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 p-4 rounded-xl bg-white border border-gray-100 shadow-sm ml-6">
                    <div className="w-10 h-10 rounded-full bg-[#FF9900] flex items-center justify-center shadow-lg shadow-[#FF9900]/30"><Users className="w-5 h-5 text-white" /></div>
                    <div>
                      <div className="font-semibold text-[#0F1111]">Agency Dashboard</div>
                      <div className="text-sm text-gray-600">12 client accounts synced</div>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Grid Features */}
      <section id="features" className="py-24 bg-[#F3F3F3] border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold font-display mb-4 text-[#131921]">Everything You Need to Dominate Amazon Ads</h2>
            <p className="text-gray-600 text-lg">A complete AI-powered suite built specifically for Amazon sellers, brands, and agencies who want real results — not just dashboards.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feat, i) => {
              const Icon = getIcon(feat.field_feature_icon);
              const bullets = feat.field_feature_bullets ? feat.field_feature_bullets.split("|").filter(Boolean) : [];
              return (
                <motion.div
                  key={feat.id}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1 }}
                  className="p-8 rounded-3xl bg-white border border-gray-200 shadow-sm hover:shadow-md hover:border-[#FF9900]/50 transition-all group"
                >
                  <div className="w-14 h-14 rounded-2xl bg-[#FF9900]/10 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
                    <Icon className="w-7 h-7 text-[#FF9900]" />
                  </div>
                  <h3 className="text-xl font-bold mb-2 text-[#0F1111] font-display">{feat.title}</h3>
                  <p className="text-gray-600 leading-relaxed mb-4 text-sm">{feat.field_feature_description}</p>
                  <ul className="space-y-2">
                    {bullets.map((b, j) => (
                      <li key={j} className="flex items-start gap-2 text-xs text-gray-500">
                        <CheckCircle2 className="w-3.5 h-3.5 text-[#FF9900] mt-0.5 flex-shrink-0" />
                        <span>{b}</span>
                      </li>
                    ))}
                  </ul>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* For Sellers / Brands / Agencies */}
      <section className="py-24 bg-white border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold font-display mb-4 text-[#131921]">Built for Every Amazon Business</h2>
            <p className="text-gray-600 text-lg">From 1 store to 100 — SellerBuddy fits your workflow.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {audienceTypes.map((item, i) => {
              const Icon = getIcon(item.field_audience_icon);
              const color = audienceColors[i] || audienceColors[0];
              return (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.15 }}
                  className="p-8 rounded-3xl border border-gray-200 bg-white shadow-sm hover:shadow-md transition-all group"
                >
                  <div className={`w-14 h-14 rounded-2xl ${color} flex items-center justify-center mb-5 group-hover:scale-110 transition-transform`}>
                    <Icon className="w-7 h-7 text-white" />
                  </div>
                  <h3 className="text-xl font-bold mb-3 text-[#0F1111]">{item.title}</h3>
                  <p className="text-gray-600 leading-relaxed">{item.field_audience_description}</p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>
    </div>
  );
}
