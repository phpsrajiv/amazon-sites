import type {
  LandingPageData,
  BlogPost,
  DrupalLoginResponse,
  TrialSignupRequest,
  TrialSignupResponse,
} from "@/types/api";

let csrfToken: string | null = null;

async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Accept: "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (csrfToken && options.method && options.method !== "GET") {
    headers["X-CSRF-Token"] = csrfToken;
  }

  const response = await fetch(path, {
    ...options,
    headers,
    credentials: "include",
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);
    throw new Error(
      errorBody?.message || `API error: ${response.status} ${response.statusText}`
    );
  }

  const text = await response.text();
  return text ? JSON.parse(text) : ({} as T);
}

export async function fetchLandingPageData(): Promise<LandingPageData> {
  return apiFetch<LandingPageData>("/api/v1/landing-page");
}

export async function fetchBlogs(): Promise<BlogPost[]> {
  return apiFetch<BlogPost[]>("/api/v1/blogs");
}

export async function fetchBlog(id: string): Promise<BlogPost> {
  return apiFetch<BlogPost>(`/api/v1/blog/${id}`);
}

export async function fetchCsrfToken(): Promise<string> {
  const response = await fetch("/session/token", { credentials: "include" });
  const token = await response.text();
  csrfToken = token;
  return token;
}

export async function login(
  username: string,
  password: string
): Promise<DrupalLoginResponse> {
  const data = await apiFetch<DrupalLoginResponse>(
    "/user/login?_format=json",
    {
      method: "POST",
      body: JSON.stringify({ name: username, pass: password }),
    }
  );
  csrfToken = data.csrf_token;
  return data;
}

export async function logout(logoutToken: string): Promise<void> {
  await apiFetch<void>(
    `/user/logout?_format=json&token=${logoutToken}`,
    { method: "POST" }
  );
  csrfToken = null;
}

export async function submitTrialSignup(
  data: TrialSignupRequest
): Promise<TrialSignupResponse> {
  return apiFetch<TrialSignupResponse>("/api/v1/trial-signup", {
    method: "POST",
    body: JSON.stringify(data),
  });
}
