import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';

export default defineConfig({
  site: 'https://docs.covenant-lang.org',
  integrations: [mdx()],
  output: 'static',
  trailingSlash: 'never',
  markdown: {
    shikiConfig: {
      theme: 'github-light',
      // Treat unknown langs as plaintext silently
      defaultColor: false,
    },
  },
  vite: {
    build: {
      rollupOptions: {
        // pagefind is a post-build static asset, not a bundled module
        external: ['/pagefind/pagefind.js'],
      },
    },
  },
});
