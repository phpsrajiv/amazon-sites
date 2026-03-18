import { Layout } from "@/components/Layout";
import { SEO } from "@/components/SEO";
import { useBlogsData } from "@/hooks/use-blogs";
import { Loader2, ArrowRight, Calendar, User } from "lucide-react";
import { Link } from "wouter";

const SITE_URL = import.meta.env.VITE_SITE_URL || "https://sellerbuddy.app";

export default function Blog() {
  const { data: blogs, isLoading, isError } = useBlogsData();

  return (
    <>
      <SEO
        title="Blog | Insights & Strategies | SellerBuddy"
        description="Expert tips, industry insights, and proven strategies to help you dominate Amazon advertising."
        canonicalUrl={`${SITE_URL}/blog`}
        ogType="website"
      />
      <Layout>
      {/* Hero Banner */}
      <section className="bg-[#131921] py-16 md:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <span className="inline-block px-3 py-1 text-xs font-bold tracking-wider uppercase bg-[#FF9900]/20 text-[#FF9900] rounded-full mb-4">
            Blog
          </span>
          <h1 className="text-3xl md:text-5xl font-display font-bold text-white mb-4">
            Insights & Strategies
          </h1>
          <p className="text-lg text-white/60 max-w-2xl mx-auto">
            Expert tips, industry insights, and proven strategies to help you
            dominate Amazon advertising.
          </p>
        </div>
      </section>

      {/* Blog Grid */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {isLoading && (
            <div className="flex justify-center py-20">
              <Loader2 className="w-8 h-8 animate-spin text-[#FF9900]" />
            </div>
          )}

          {isError && (
            <div className="text-center py-20">
              <p className="text-red-600 text-lg">
                Failed to load blog posts. Please try again later.
              </p>
            </div>
          )}

          {blogs && blogs.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {blogs.map((post) => (
                <Link
                  key={post.id}
                  href={`/blog/${post.id}`}
                  className="group"
                >
                  <article className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-1 h-full flex flex-col">
                    {/* Image placeholder */}
                    <div className="h-48 bg-gradient-to-br from-[#131921] to-[#232F3E] flex items-center justify-center relative overflow-hidden">
                      <div className="absolute inset-0 bg-[#FF9900]/10" />
                      <span className="text-white/30 text-6xl font-display font-bold">
                        {post.title.charAt(0)}
                      </span>
                      <span className="absolute top-4 left-4 px-2 py-1 text-xs font-semibold bg-[#FF9900] text-[#0F1111] rounded">
                        {post.field_blog_category}
                      </span>
                    </div>

                    <div className="p-6 flex flex-col flex-1">
                      <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3.5 h-3.5" />
                          {post.field_blog_date}
                        </span>
                        <span className="flex items-center gap-1">
                          <User className="w-3.5 h-3.5" />
                          {post.field_blog_author}
                        </span>
                      </div>

                      <h2 className="text-xl font-display font-bold text-[#0F1111] mb-3 group-hover:text-[#FF9900] transition-colors line-clamp-2">
                        {post.title}
                      </h2>

                      <p className="text-gray-600 text-sm leading-relaxed mb-4 flex-1 line-clamp-3">
                        {post.field_blog_summary}
                      </p>

                      <span className="inline-flex items-center gap-1 text-sm font-semibold text-[#FF9900] group-hover:gap-2 transition-all">
                        Read more
                        <ArrowRight className="w-4 h-4" />
                      </span>
                    </div>
                  </article>
                </Link>
              ))}
            </div>
          )}
        </div>
      </section>
      </Layout>
    </>
  );
}
