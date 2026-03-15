import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "path";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },
  server: {
    port: 3000,
    proxy: {
      "/api": {
        target: "http://drupal:80",
        changeOrigin: true,
      },
      "/user": {
        target: "http://drupal:80",
        changeOrigin: true,
      },
      "/session": {
        target: "http://drupal:80",
        changeOrigin: true,
      },
      "/sitemap.xml": {
        target: "http://drupal:80",
        changeOrigin: true,
      },
    },
  },
  preview: {
    port: 3000,
  },
});
