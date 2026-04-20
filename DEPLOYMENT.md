# Covenant — Deployment Guide

Step-by-step instructions to deploy the Covenant manifesto site to GitHub + Vercel.

## Prerequisites

- GitHub account
- Vercel account (free tier is sufficient)
- `git` installed locally
- Optional: a purchased domain (you can start on a `*.vercel.app` subdomain first)

## Step 1 — Create GitHub repository

1. Go to https://github.com/new
2. Repository name: `covenant-lang`
3. Description: *Covenant smart contract language — cryptographic guarantees as language primitives*
4. Public
5. **Do NOT initialize** with README, `.gitignore`, or a license — the repo already has them
6. Click *Create repository*

## Step 2 — Push code to GitHub

From the unzipped deployment folder:

```bash
git init
git add .
git commit -m "Initial commit — Covenant manifesto v2.0"
git branch -M main
git remote add origin https://github.com/Valisthea/covenant-lang.git
git push -u origin main
```

## Step 3 — Deploy to Vercel

### Option A — Vercel CLI (recommended)

```bash
npm install -g vercel

vercel

# Prompts:
#   Link to existing project?   No
#   Project name                covenant-lang
#   Directory                   ./
#   Deploy?                     Yes

vercel --prod
```

### Option B — Vercel dashboard

1. Go to https://vercel.com/new
2. *Import Git Repository* → select `covenant-lang`
3. Framework Preset: **Other**
4. Build Command: *(leave empty)*
5. Output Directory: `./`
6. Click *Deploy*

## Step 4 — Connect a custom domain (optional)

If you own a domain (e.g. `covenant-lang.org`):

1. Vercel dashboard → project → *Settings* → *Domains*
2. Add `covenant-lang.org` and `www.covenant-lang.org`
3. Vercel shows the DNS records to configure
4. At your registrar (Namecheap, Porkbun, Cloudflare, …) add the A/CNAME records
5. Wait 10 – 60 minutes for DNS propagation

Vercel issues and renews SSL certificates automatically via Let's Encrypt.

## Step 5 — Update URLs in code

If your final domain differs from `covenant-lang.org`, update three files:

- `index.html` — all `https://covenant-lang.org/` occurrences (canonical, og:url, og:image, twitter:image)
- `sitemap.xml` — `<loc>` value
- `robots.txt` — `Sitemap:` directive

Then:

```bash
git add index.html sitemap.xml robots.txt
git commit -m "Update URLs to production domain"
git push
```

Vercel auto-deploys every push to `main`.

## Verification checklist

After deployment, verify:

- [ ] Site loads at your domain over HTTPS
- [ ] Favicon appears in the browser tab
- [ ] Open Graph image shows correctly when sharing on X / Discord / LinkedIn
- [ ] Print works (Ctrl / Cmd + P) with proper A4 pagination
- [ ] Mobile responsive (check on a phone or Chrome DevTools device mode)
- [ ] All internal anchor links work
- [ ] SSL active (green padlock)
- [ ] Security headers active (test with https://securityheaders.com)

## Troubleshooting

**Favicon not showing**
- Hard refresh (Ctrl+Shift+R / Cmd+Shift+R)
- Check the browser console for 404s on `/favicon.svg`, `/favicon-32.png`, etc.
- Confirm all favicon files are present in the repo root

**OG image not showing in Twitter / X preview**
- Validate with https://cards-dev.twitter.com/validator
- The `og:image` URL must be absolute (`https://...`)
- Image must be publicly accessible and under 5 MB

**Vercel build fails**
- Check `vercel.json` is valid JSON (no trailing commas)
- Check `package.json` has no syntax errors
- Read the Vercel build log for the exact error

**Custom domain stuck on "Invalid Configuration"**
- DNS can take up to an hour to propagate
- Use `dig covenant-lang.org` or https://dnschecker.org to verify records
- Remove any stale A / AAAA records at the registrar

## Post-launch

1. Share on X with the OG card preview
2. Post on the Ethereum Magicians forum once the spec V1 is ready
3. Submit to Hacker News when the first contributor commitments land
4. Link from the Kairos Lab main site

## Security notes (Web3-specific)

- `vercel.json` sets HSTS, X-Frame-Options (DENY), X-Content-Type-Options (nosniff), a restrictive Permissions-Policy, and cache-immutable headers for all static assets
- No JavaScript is loaded from third-party domains beyond Google Fonts (CSS only, subresource integrity not required for CSS)
- The site ships no cookies, no trackers, and makes no outbound requests from the document itself

---

Questions? Ping [@Valisthea](https://x.com/Valisthea).
