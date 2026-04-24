import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';

export default defineConfig({
  site: 'https://covenant-lang.org',
  base: '/docs',
  integrations: [mdx()],
  output: 'static',
  trailingSlash: 'never',
  markdown: {
    shikiConfig: {
      theme: 'github-light',
      defaultColor: false,
    },
  },
  vite: {
    build: {
      rollupOptions: {
        external: ['/docs/pagefind/pagefind.js'],
      },
    },
  },
});
