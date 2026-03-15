import { motion } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { useTrial } from "./TrialContext";
import { Button } from "@/components/ui/button";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ChevronLeft, ChevronRight, Play, ShieldCheck, Sparkles, TrendingUp, Zap } from "lucide-react";
import type { HeroSlide, StatCard } from "@/types/api";

const mockData = [
  { name: "Mon", score: 45 },
  { name: "Tue", score: 52 },
  { name: "Wed", score: 67 },
  { name: "Thu", score: 70 },
  { name: "Fri", score: 82 },
  { name: "Sat", score: 91 },
  { name: "Sun", score: 98 },
];

function HeroSlider({ slides }: { slides: HeroSlide[] }) {
  const [current, setCurrent] = useState(0);
  const [animating, setAnimating] = useState(false);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const goTo = (index: number) => {
    if (animating) return;
    setAnimating(true);
    setCurrent(index);
    setTimeout(() => setAnimating(false), 500);
  };

  const prev = () => goTo((current - 1 + slides.length) % slides.length);
  const next = () => goTo((current + 1) % slides.length);

  const resetTimer = () => {
    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = setInterval(() => {
      setCurrent((c) => (c + 1) % slides.length);
    }, 4500);
  };

  useEffect(() => {
    if (slides.length === 0) return;
    resetTimer();
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, [slides.length]);

  if (slides.length === 0) return null;

  return (
    <div className="relative w-full overflow-hidden rounded-2xl shadow-2xl group h-[340px] md:h-[440px]">
      {slides.map((slide, i) => (
        <div
          key={slide.id}
          className="absolute inset-0 transition-opacity duration-700 ease-in-out"
          style={{ opacity: i === current ? 1 : 0, zIndex: i === current ? 1 : 0 }}
        >
          {slide.field_slide_image ? (
            <img src={slide.field_slide_image} alt={slide.title} className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-[#131921] to-[#007185]" />
          )}
          <div className="absolute inset-0 bg-gradient-to-t from-black/75 via-black/30 to-black/10" />
          <div className="absolute bottom-0 left-0 right-0 p-6 md:p-10 text-white z-10">
            <span className="inline-block text-xs font-bold uppercase tracking-widest text-[#FF9900] bg-[#FF9900]/15 border border-[#FF9900]/30 rounded-full px-3 py-1 mb-3">
              {slide.field_slide_tag}
            </span>
            <h3 className="text-2xl md:text-3xl font-bold mb-2 drop-shadow-lg">{slide.title}</h3>
            <p className="text-sm md:text-base text-white/80 max-w-lg">{slide.field_slide_description}</p>
          </div>
        </div>
      ))}

      <button
        onClick={() => { prev(); resetTimer(); }}
        className="absolute left-4 top-1/2 -translate-y-1/2 z-20 w-10 h-10 rounded-full bg-black/40 hover:bg-black/70 border border-white/20 text-white flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity backdrop-blur-sm"
        aria-label="Previous slide"
      >
        <ChevronLeft className="w-5 h-5" />
      </button>

      <button
        onClick={() => { next(); resetTimer(); }}
        className="absolute right-4 top-1/2 -translate-y-1/2 z-20 w-10 h-10 rounded-full bg-black/40 hover:bg-black/70 border border-white/20 text-white flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity backdrop-blur-sm"
        aria-label="Next slide"
      >
        <ChevronRight className="w-5 h-5" />
      </button>

      <div className="absolute bottom-5 right-6 z-20 flex gap-2">
        {slides.map((_, i) => (
          <button
            key={i}
            onClick={() => { goTo(i); resetTimer(); }}
            className={`h-2 rounded-full transition-all duration-300 ${i === current ? "w-6 bg-[#FF9900]" : "w-2 bg-white/50 hover:bg-white/80"}`}
            aria-label={`Go to slide ${i + 1}`}
          />
        ))}
      </div>
    </div>
  );
}

interface HeroSectionProps {
  slides: HeroSlide[];
  stats: StatCard[];
}

export function HeroSection({ slides, stats }: HeroSectionProps) {
  const { openTrialModal } = useTrial();

  return (
    <section className="relative overflow-hidden pt-12 pb-20 lg:pt-16 lg:pb-32 bg-[#F3F3F3]">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-[#FF9900]/10 rounded-full blur-[120px] opacity-70 pointer-events-none" />
      <div className="absolute top-0 left-1/4 w-[400px] h-[400px] bg-[#007185]/10 rounded-full blur-[100px] opacity-50 pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">

        {/* Image Slider */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-14"
        >
          <HeroSlider slides={slides} />
        </motion.div>

        {/* Hero Text */}
        <div className="text-center max-w-4xl mx-auto mb-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.15 }}
          >
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#FF9900] text-[#0F1111] text-sm font-bold mb-8 shadow-sm">
              <Sparkles className="w-4 h-4" />
              <span>Now with Agentic AI — Ask, Analyze & Act in one chat</span>
            </div>

            <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold font-display tracking-tight mb-6 text-[#0F1111]">
              Supercharge Your<br className="hidden md:block" />
              <span className="text-[#FF9900]">Amazon Business</span>
            </h1>

            <p className="text-lg md:text-xl text-gray-600 mb-10 max-w-2xl mx-auto leading-relaxed">
              Run, optimize, and scale your Amazon campaigns with AI-powered precision, agentic AI, real-time optimizations, and crystal-clear reporting — so you never waste a dollar or a second.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button
                onClick={openTrialModal}
                size="lg"
                className="w-full sm:w-auto text-lg h-14 px-8 bg-[#FF9900] hover:bg-[#FA8900] text-[#0F1111] font-bold shadow-md hover:shadow-lg transition-all hover:-translate-y-1 rounded-md"
              >
                Get a Free Audit Report
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="w-full sm:w-auto text-lg h-14 px-8 border border-[#D5D9D9] text-[#0F1111] hover:bg-[#F7FAFA] bg-white transition-all rounded-md"
                onClick={openTrialModal}
              >
                <Play className="w-5 h-5 mr-2" />
                Request a Demo
              </Button>
            </div>

            <div className="mt-8 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-sm text-gray-500">
              <span className="flex items-center gap-1.5"><ShieldCheck className="w-4 h-4 text-[#007185]" /> Verified by Amazon</span>
              <span className="flex items-center gap-1.5"><Zap className="w-4 h-4 text-[#FF9900]" /> Setup in 60 seconds</span>
              <span className="flex items-center gap-1.5"><TrendingUp className="w-4 h-4 text-green-600" /> Trusted by 12,000+ sellers</span>
            </div>
          </motion.div>
        </div>

        {/* Stats Row */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.25 }}
          className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-14 max-w-4xl mx-auto"
        >
          {stats.map((stat) => (
            <div key={stat.id} className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 text-center">
              <div className="text-2xl md:text-3xl font-bold text-[#FF9900]">
                {stat.field_stat_prefix}{stat.field_stat_value}{stat.field_stat_suffix}
              </div>
              <div className="text-sm text-gray-500 mt-1">{stat.title}</div>
            </div>
          ))}
        </motion.div>

        {/* Mock Dashboard */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.3 }}
          className="relative max-w-5xl mx-auto"
        >
          <div className="absolute inset-0 bg-gradient-to-t from-[#F3F3F3] via-transparent to-transparent z-20 h-full pointer-events-none" style={{ top: "60%" }} />

          <div className="rounded-2xl border border-gray-200 bg-white shadow-2xl overflow-hidden ring-1 ring-black/5">
            <div className="flex flex-col sm:flex-row sm:items-center px-4 py-3 border-b border-gray-100 bg-gray-50">
              <div className="flex space-x-2 mb-3 sm:mb-0">
                <div className="w-3 h-3 rounded-full bg-red-400" />
                <div className="w-3 h-3 rounded-full bg-yellow-400" />
                <div className="w-3 h-3 rounded-full bg-green-400" />
              </div>
              <div className="sm:ml-8 flex overflow-x-auto space-x-2 text-xs font-medium text-gray-500 pb-1 sm:pb-0">
                <span className="text-[#0F1111] bg-white px-4 py-1.5 rounded-md whitespace-nowrap shadow-sm border border-gray-200">Autopilot Overview</span>
                <span className="px-4 py-1.5 whitespace-nowrap">Campaign Optimizer</span>
                <span className="px-4 py-1.5 whitespace-nowrap">AI Chat</span>
                <span className="px-4 py-1.5 whitespace-nowrap">Keyword Research</span>
              </div>
            </div>

            <div className="p-6 grid grid-cols-1 md:grid-cols-3 gap-6 bg-white">
              <div className="md:col-span-1 space-y-4">
                <div className="p-5 rounded-xl bg-white border border-gray-100 shadow-sm">
                  <div className="flex justify-between items-start mb-2">
                    <div className="text-sm text-gray-500">ACoS Improvement</div>
                    <Sparkles className="w-4 h-4 text-[#FF9900]" />
                  </div>
                  <div className="text-4xl font-display font-bold text-[#0F1111] mb-2">
                    -38<span className="text-xl text-gray-400 font-medium">%</span>
                  </div>
                  <div className="text-xs text-green-600 flex items-center font-medium bg-green-50 w-fit px-2 py-1 rounded">
                    <TrendingUp className="w-3 h-3 mr-1" /> vs. last 30 days
                  </div>
                </div>
                <div className="p-4 rounded-xl bg-white border border-gray-100 shadow-sm">
                  <div className="text-xs text-gray-500 mb-3 font-medium">Autopilot Actions Today</div>
                  <div className="space-y-2">
                    {[["Bid adjustments", "1,284", "text-[#0F1111]"], ["Keywords paused", "47", "text-[#C40000]"], ["Budget reallocated", "$842", "text-green-600"], ["Ad spend saved", "$312", "text-[#FF9900]"]].map(([label, val, cls]) => (
                      <div key={label} className="flex justify-between text-xs">
                        <span className="text-gray-700">{label}</span>
                        <span className={`font-bold ${cls}`}>{val}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="p-4 rounded-xl bg-[#131921] border border-gray-700 shadow-sm">
                  <div className="text-xs text-gray-400 mb-2">AI Chat</div>
                  <div className="text-xs text-white italic">"Why is my ACoS high on ASIN B08XYZ?"</div>
                  <div className="mt-2 text-xs text-[#FF9900]">→ High bids on 3 broad keywords. Pausing now...</div>
                </div>
              </div>

              <div className="md:col-span-2 p-5 rounded-xl bg-white border border-gray-100 shadow-sm flex flex-col">
                <div className="flex justify-between items-center mb-6">
                  <div className="text-sm font-medium text-[#0F1111]">Ad Revenue vs. Ad Spend</div>
                  <div className="text-xs text-gray-500 bg-gray-50 px-2 py-1 rounded border border-gray-200">Last 7 Days</div>
                </div>
                <div className="flex-1 min-h-[200px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={mockData} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
                      <defs>
                        <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#FF9900" stopOpacity={0.2} />
                          <stop offset="95%" stopColor="#FF9900" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" vertical={false} />
                      <XAxis dataKey="name" stroke="#6B7280" fontSize={12} tickLine={false} axisLine={false} />
                      <YAxis stroke="#6B7280" fontSize={12} tickLine={false} axisLine={false} domain={["dataMin - 10", "auto"]} />
                      <Tooltip
                        contentStyle={{ backgroundColor: "#ffffff", border: "1px solid #E5E7EB", borderRadius: "8px", boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)" }}
                        itemStyle={{ color: "#0F1111", fontWeight: "bold" }}
                      />
                      <Area type="monotone" dataKey="score" stroke="#FF9900" strokeWidth={3} fillOpacity={1} fill="url(#colorScore)" activeDot={{ r: 6, strokeWidth: 0, fill: "#FF9900" }} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
