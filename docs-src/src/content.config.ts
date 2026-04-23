import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const base = z.object({
  title: z.string(),
  description: z.string().optional(),
  order: z.number().optional(),
  section: z.string().optional(),
});

export const collections = {
  docs: defineCollection({
    loader: glob({ pattern: '**/*.md', base: './src/content/docs' }),
    schema: base,
  }),
  'getting-started': defineCollection({
    loader: glob({ pattern: '**/*.md', base: './src/content/getting-started' }),
    schema: base,
  }),
  security: defineCollection({
    loader: glob({ pattern: '**/*.md', base: './src/content/security' }),
    schema: base,
  }),
  glossary: defineCollection({
    loader: glob({ pattern: '**/*.md', base: './src/content/glossary' }),
    schema: base,
  }),
};
