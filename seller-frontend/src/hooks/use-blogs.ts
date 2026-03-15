import { useQuery } from "@tanstack/react-query";
import { fetchBlogs, fetchBlog } from "@/lib/api";
import type { BlogPost } from "@/types/api";

export function useBlogsData() {
  return useQuery<BlogPost[]>({
    queryKey: ["blogs"],
    queryFn: fetchBlogs,
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
  });
}

export function useBlogData(id: string) {
  return useQuery<BlogPost>({
    queryKey: ["blog", id],
    queryFn: () => fetchBlog(id),
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
    enabled: !!id,
  });
}
