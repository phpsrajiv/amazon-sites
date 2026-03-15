import { Layout } from "@/components/Layout";
import { useBlogData } from "@/hooks/use-blogs";
import { Loader2, ArrowLeft, Calendar, User, Tag } from "lucide-react";
import { Link, useParams } from "wouter";

export default function BlogPost() {
  const { id } = useParams<{ id: string }>();
  const { data: post, isLoading, isError } = useBlogData(id || "");

  return (
    <Layout>
      {isLoading && (
        <div className="flex justify-center py-32">
          <Loader2 className="w-8 h-8 animate-spin text-[#FF9900]" />
        </div>
      )}

      {isError && (
        <div className="text-center py-32">
          <p className="text-red-600 text-lg mb-4">Blog post not found.</p>
          <Link
            href="/blog"
            className="text-[#FF9900] font-semibold hover:underline"
          >
            Back to Blog
          </Link>
        </div>
      )}

      {post && (
        <>
          {/* Hero */}
          <section className="bg-[#131921] py-16 md:py-24">
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
              <Link
                href="/blog"
                className="inline-flex items-center gap-1 text-sm text-white/60 hover:text-[#FF9900] transition-colors mb-6"
              >
                <ArrowLeft className="w-4 h-4" />
                Back to Blog
              </Link>

              <span className="inline-block px-2 py-1 text-xs font-semibold bg-[#FF9900] text-[#0F1111] rounded mb-4">
                {post.field_blog_category}
              </span>

              <h1 className="text-3xl md:text-4xl lg:text-5xl font-display font-bold text-white mb-6 leading-tight">
                {post.title}
              </h1>

              <div className="flex flex-wrap items-center gap-6 text-sm text-white/60">
                <span className="flex items-center gap-1.5">
                  <User className="w-4 h-4" />
                  {post.field_blog_author}
                </span>
                <span className="flex items-center gap-1.5">
                  <Calendar className="w-4 h-4" />
                  {post.field_blog_date}
                </span>
                <span className="flex items-center gap-1.5">
                  <Tag className="w-4 h-4" />
                  {post.field_blog_category}
                </span>
              </div>
            </div>
          </section>

          {/* Content */}
          <section className="py-12 md:py-16 bg-white">
            <article className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
              <div
                className="prose prose-lg max-w-none
                  prose-headings:font-display prose-headings:text-[#0F1111] prose-headings:font-bold
                  prose-h2:text-2xl prose-h2:mt-10 prose-h2:mb-4
                  prose-h3:text-xl prose-h3:mt-8 prose-h3:mb-3
                  prose-p:text-gray-700 prose-p:leading-relaxed prose-p:mb-4
                  prose-a:text-[#FF9900] prose-a:no-underline hover:prose-a:underline
                  prose-strong:text-[#0F1111]"
                dangerouslySetInnerHTML={{ __html: post.field_blog_body }}
              />

              {/* Bottom nav */}
              <div className="mt-16 pt-8 border-t border-gray-200">
                <Link
                  href="/blog"
                  className="inline-flex items-center gap-2 px-6 py-3 bg-[#FF9900] text-[#0F1111] font-bold rounded-md hover:bg-[#FA8900] transition-colors"
                >
                  <ArrowLeft className="w-4 h-4" />
                  Back to all articles
                </Link>
              </div>
            </article>
          </section>
        </>
      )}
    </Layout>
  );
}
