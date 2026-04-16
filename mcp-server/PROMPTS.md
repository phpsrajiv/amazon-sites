# SellerBuddy AI Agents — Example Prompts

Example prompts for triggering SellerBuddy AI agents via Claude Code or the Claude desktop app.

---

## Health Checks

```
Are all SellerBuddy agents running?
```
```
Check the status of the SEO agent / content writer / video script / video generator / social media agent
```

---

## SEO Agent

### Fetch Keywords from Google Search Console

```
Fetch the latest keywords from Google Search Console for https://sellerbuddy.app
```
```
Pull GSC keyword data for https://sellerbuddy.app and show me the top opportunities
```
```
Run the weekly SEO pipeline for https://sellerbuddy.app and list all keyword opportunities with their category, impressions, clicks, and opportunity type (quick-win / grow / new)
```
```
Run the weekly SEO pipeline for https://sellerbuddy.app and only show me the quick-win keywords — ones already ranking between position 5 and 20
```
```
Fetch keywords from GSC for https://sellerbuddy.app and suggest two blog topics based on the highest opportunity keywords
```

---

### Generate Outlines

```
Generate an SEO outline for a blog post titled "How to Lower Your Amazon ACoS in 30 Days" targeting the keyword "amazon acos optimization"
```
```
Generate a comparison-style SEO outline targeting the keyword "helium 10 vs jungle scout" with secondary keywords: ["amazon product research", "fba tools"]
```
```
Run the weekly SEO pipeline for https://sellerbuddy.com
```
```
Push this outline to Drupal as a draft: [paste outline JSON]
```

---

## Content Writer

```
Write a full blog post from this outline: [paste outline JSON]
```
```
Write a blog post from this outline and push it to Drupal as a draft: [paste outline JSON]
```
```
Generate LinkedIn carousel slides from this outline: [paste outline JSON]
```
```
Generate a tweet thread from this blog HTML: [paste blog HTML]
```
```
Run the full content pipeline (blog + LinkedIn + tweets) from this outline: [paste outline JSON]
```
```
Run the full content pipeline and push the blog to Drupal: [paste outline JSON]
```

---

## Video Script Agent

```
Generate a YouTube video script from this blog post: [paste blog HTML]
```
```
Generate an 8-minute YouTube script from this outline: [paste outline JSON]
```
```
Generate 5 YouTube Shorts hooks from this blog: [paste blog HTML]
```
```
Generate both a YouTube script and Shorts hooks from this outline: [paste outline JSON]
```

---

## Video Generator

```
Start video generation for this YouTube script: [paste script JSON]
```
```
Check the status of video job abc123
```
```
Get the result for video job abc123
```
```
Give me the download URL for video job abc123
```

---

## Social Media Agent

```
Generate Facebook posts about "Amazon Prime Day tips for sellers"
```
```
Generate a professional LinkedIn post about "how SellerBuddy cuts wasted ad spend"
```
```
Generate Instagram content about "behind the scenes of running an Amazon FBA business"
```
```
Generate posts for all platforms about "Black Friday preparation for Amazon sellers"
```
```
What are the best times to post on LinkedIn this week?
```
```
Get the weekly posting schedule for Facebook, LinkedIn and Instagram starting 2026-04-14
```
```
What events are coming up in the next 30 days that I should plan content around?
```
```
What's the current news sentiment — should I be posting right now?
```
```
Show me the best posting times for Instagram based on past engagement
```
```
Generate the weekly engagement report for this week
```
```
Show me the last 20 decision logs for the social media agent
```
```
Show me all posts logged for LinkedIn in the past week
```

---

## Chained Pipelines

Claude orchestrates these automatically — no manual wiring needed.

```
Run the weekly SEO pipeline for sellerbuddy.com, then write a full blog post and LinkedIn carousel from the first outline it returns
```
```
Generate an SEO outline for "amazon ppc automation" then run the full content pipeline and also generate a YouTube script — push the blog to Drupal when done
```
```
Check if all agents are healthy, then generate posts for all social platforms about Prime Day and tell me the best time to post them this week
```
