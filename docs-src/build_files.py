#!/usr/bin/env python3
"""Build all docs-src content files."""
import os, sys
BASE = os.path.dirname(os.path.abspath(__file__))
BT3 = chr(96)*3
BT1 = chr(96)

def w(rel, txt):
    path = os.path.join(BASE, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(txt)
    print("  " + rel)

# will be populated by appended sections
FILES = {}

FILES["src/styles/global.css"] = (
    ":root{--ink:#1a1a1a;--ink-soft:#2d2d2d;--ink-mute:#555;--ink-faint:#888;"
    "--paper:#fcfbf8;--paper-alt:#f5f4f0;"
    "--rule:rgba(26,26,26,.25);--rule-faint:rgba(26,26,26,.10);"
    "--accent:#7C3AED;--accent-bg:rgba(124,58,237,.06);"
    "--warn:#d97706;--danger:#dc2626;--info:#0ea5e9;--tip:#16a34a;"
    "--header-h:60px;--sidebar-w:260px;"
    "--font-serif:'EB Garamond',Georgia,serif;"
    "--font-sans:'Inter',system-ui,sans-serif;"
    "--font-mono:'JetBrains Mono','Fira Code',monospace}\n"
    "*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}\n"
    "html{font-size:16px;scroll-behavior:smooth}\n"
    "body{font-family:var(--font-sans);background:var(--paper);color:var(--ink);line-height:1.6;min-height:100vh}\n"
    "h1,h2,h3,h4{font-family:var(--font-serif);font-weight:400;line-height:1.25;color:var(--ink);letter-spacing:-.01em}\n"
    "h1{font-size:2.25rem;margin-bottom:1rem}\n"
    "h2{font-size:1.65rem;margin-top:2.5rem;margin-bottom:.75rem;padding-top:1rem;border-top:1px solid var(--rule-faint)}\n"
    "h3{font-size:1.25rem;margin-top:1.75rem;margin-bottom:.5rem}\n"
    "p{margin-bottom:1rem;font-size:10.5pt;line-height:1.75;color:var(--ink-soft)}\n"
    "a{color:var(--accent);text-decoration:none}\na:hover{text-decoration:underline}\n"
    "ul,ol{padding-left:1.5rem;margin-bottom:1rem}\n"
    "li{font-size:10.5pt;color:var(--ink-soft);line-height:1.7;margin-bottom:.25rem}\n"
    "strong{font-weight:600;color:var(--ink)}\n"
    "code{font-family:var(--font-mono);font-size:.82em;background:var(--paper-alt);"
    "border:1px solid var(--rule-faint);padding:1px 5px;border-radius:2px;color:var(--accent)}\n"
    "pre{background:#f8f7f4;border:1px solid var(--rule-faint);border-left:3px solid var(--accent);"
    "padding:1.25rem 1.5rem;overflow-x:auto;margin:1.5rem 0;font-family:var(--font-mono);font-size:.82rem;line-height:1.6}\n"
    "pre code{background:none;border:none;padding:0;color:inherit;font-size:inherit}\n"
    "hr{border:none;border-top:1px solid var(--rule-faint);margin:2rem 0}\n"
    "blockquote{border-left:3px solid var(--accent);padding:.75rem 1rem;margin:1.5rem 0;"
    "background:var(--accent-bg);font-style:italic;color:var(--ink-mute)}\n"
    "table{width:100%;border-collapse:collapse;margin:1.5rem 0;font-size:10pt}\n"
    "th{text-align:left;font-family:var(--font-mono);font-size:7.5pt;font-weight:600;"
    "letter-spacing:.1em;text-transform:uppercase;color:var(--ink-faint);"
    "border-bottom:1px solid var(--rule);padding:.5rem .75rem}\n"
    "td{padding:.6rem .75rem;border-bottom:1px solid var(--rule-faint);color:var(--ink-soft);vertical-align:top}\n"
    "tr:last-child td{border-bottom:none}\n"
)

FILES["src/styles/global.css"] += (
    "#site-header{position:fixed;top:0;left:0;right:0;height:var(--header-h);"
    "background:rgba(252,251,248,.92);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);"
    "border-bottom:1px solid var(--rule-faint);display:flex;align-items:center;"
    "padding:0 48px;z-index:1000;transition:border-color .3s}\n"
    "#site-header.scrolled{border-bottom-color:var(--rule)}\n"
    ".header-brand{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--ink);flex-shrink:0}\n"
    ".header-logo-wrap{width:32px;height:32px;position:relative}\n"
    ".header-brand-name{font-family:'JetBrains Mono',monospace;font-size:10pt;font-weight:600;"
    "letter-spacing:.12em;text-transform:uppercase;color:var(--ink)}\n"
    ".header-badge{font-family:'JetBrains Mono',monospace;font-size:7pt;font-weight:500;"
    "letter-spacing:.1em;text-transform:uppercase;color:var(--accent);"
    "border:1px solid var(--accent);padding:1px 6px;margin-left:4px;vertical-align:middle}\n"
    ".header-spacer{flex:1}\nnav.header-nav{display:flex;align-items:center;gap:32px}\n"
    ".nav-link{font-family:'Inter',sans-serif;font-size:9.5pt;font-weight:400;"
    "color:var(--ink-mute);text-decoration:none;letter-spacing:.01em;transition:color .15s}\n"
    ".nav-link:hover{color:var(--ink)}.nav-link.active{color:var(--accent);font-weight:500}\n"
    ".nav-link-cta{font-family:'JetBrains Mono',monospace;font-size:8.5pt;font-weight:500;"
    "letter-spacing:.08em;text-transform:uppercase;color:var(--accent);text-decoration:none;"
    "border:1px solid var(--accent);padding:5px 12px;transition:background .15s,color .15s}\n"
    ".nav-link-cta:hover{background:var(--accent);color:white}\n"
    ".docs-layout{display:grid;grid-template-columns:var(--sidebar-w) 1fr;min-height:100vh;padding-top:var(--header-h)}\n"
    "#docs-sidebar{position:fixed;top:var(--header-h);left:0;width:var(--sidebar-w);"
    "height:calc(100vh - var(--header-h));overflow-y:auto;border-right:1px solid var(--rule-faint);"
    "padding:24px 0 40px;background:var(--paper);z-index:100}\n"
    ".sidebar-section{margin-bottom:24px}\n"
    ".sidebar-section-title{font-family:'JetBrains Mono',monospace;font-size:7pt;font-weight:600;"
    "letter-spacing:.15em;text-transform:uppercase;color:var(--ink-faint);padding:0 20px;display:block;margin-bottom:6px}\n"
    ".sidebar-link{display:block;font-family:'Inter',sans-serif;font-size:9pt;color:var(--ink-mute);"
    "text-decoration:none;padding:5px 20px;transition:color .12s,background .12s;line-height:1.4}\n"
    ".sidebar-link:hover{color:var(--ink);background:var(--paper-alt)}\n"
    ".sidebar-link.active{color:var(--accent);font-weight:500;background:var(--accent-bg);border-right:2px solid var(--accent)}\n"
    ".docs-main{grid-column:2;min-width:0}.docs-content{max-width:740px;margin:0 auto;padding:56px 48px 80px}\n"
    ".callout{border-radius:2px;padding:1rem 1.25rem;margin:1.5rem 0;display:flex;gap:.75rem;font-size:10pt}\n"
    ".callout-icon{font-size:1rem;flex-shrink:0;line-height:1.6}.callout-body{flex:1}\n"
    ".callout-body p{margin:0;font-size:inherit}\n"
    ".callout--info{background:rgba(14,165,233,.08);border-left:3px solid var(--info);color:#0369a1}\n"
    ".callout--tip{background:rgba(22,163,74,.08);border-left:3px solid var(--tip);color:#15803d}\n"
    ".callout--warning{background:rgba(217,119,6,.08);border-left:3px solid var(--warn);color:#92400e}\n"
    ".callout--danger{background:rgba(220,38,38,.08);border-left:3px solid var(--danger);color:#991b1b}\n"
)

FILES["src/styles/global.css"] += (
    "footer#site-footer{border-top:1px solid var(--ink);padding:48px 0 40px;grid-column:1/-1}\n"
    ".footer-inner{max-width:900px;margin:0 auto;padding:0 48px;display:grid;grid-template-columns:1fr 1fr 1fr;gap:40px}\n"
    ".footer-brand{display:flex;flex-direction:column;gap:12px}\n"
    ".footer-brand-row{display:flex;align-items:center;gap:8px}\n"
    ".footer-brand-name{font-family:'JetBrains Mono',monospace;font-size:10pt;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--ink)}\n"
    ".footer-by{font-family:'Inter',sans-serif;font-size:9pt;color:var(--ink-faint)}\n"
    ".footer-tagline{font-family:'EB Garamond',serif;font-size:11pt;font-style:italic;color:var(--ink-mute);line-height:1.5}\n"
    ".footer-col-title{font-family:'JetBrains Mono',monospace;font-size:7.5pt;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-faint);display:block;margin-bottom:14px}\n"
    ".footer-link{font-family:'Inter',sans-serif;font-size:10pt;color:var(--ink-soft);text-decoration:none;display:block;margin-bottom:6px;transition:color .15s}\n"
    ".footer-link:hover{color:var(--accent)}\n"
    ".footer-link-mono{font-family:'JetBrains Mono',monospace;font-size:8.5pt;color:var(--ink-mute);text-decoration:none;display:block;margin-bottom:6px;word-break:break-all;transition:color .15s}\n"
    ".footer-link-mono:hover{color:var(--accent)}\n"
    ".footer-bottom{max-width:900px;margin:36px auto 0;padding:20px 48px 0;border-top:1px solid var(--rule-faint);display:flex;justify-content:space-between;align-items:center}\n"
    ".footer-closing{font-family:'EB Garamond',serif;font-size:11pt;font-style:italic;color:var(--ink-mute)}\n"
    ".footer-license{font-family:'JetBrains Mono',monospace;font-size:7.5pt;color:var(--ink-faint);letter-spacing:.06em}\n"
    ".search-wrap{padding:12px 20px 20px}\n"
    "#search-input{width:100%;font-family:var(--font-mono);font-size:8.5pt;background:var(--paper-alt);border:1px solid var(--rule);padding:6px 10px;color:var(--ink);outline:none;transition:border-color .15s}\n"
    "#search-input:focus{border-color:var(--accent)}#search-input::placeholder{color:var(--ink-faint)}\n"
    "#search-results{margin-top:8px}\n"
    ".breadcrumb{font-family:var(--font-mono);font-size:7.5pt;color:var(--ink-faint);letter-spacing:.05em;margin-bottom:1.5rem}\n"
    ".breadcrumb a{color:var(--ink-faint);text-decoration:none}.breadcrumb a:hover{color:var(--accent)}\n"
    ".breadcrumb span{margin:0 6px}\n"
    ".doc-nav{display:flex;justify-content:space-between;margin-top:3rem;padding-top:1.5rem;border-top:1px solid var(--rule-faint);gap:1rem}\n"
    ".doc-nav-link{font-family:var(--font-mono);font-size:8.5pt;color:var(--accent);text-decoration:none;border:1px solid var(--accent);padding:8px 14px;transition:background .15s,color .15s;max-width:48%}\n"
    ".doc-nav-link:hover{background:var(--accent);color:white}\n"
    '.doc-nav-link.prev::before{content:"<- "}.doc-nav-link.next::after{content:" ->"}\n'
    ".doc-nav-link span{display:block;font-size:7pt;color:var(--ink-faint);margin-bottom:2px;letter-spacing:0}\n"
    ".doc-nav-link:hover span{color:rgba(255,255,255,.7)}\n"
    "@media(max-width:768px){#site-header{padding:0 20px}nav.header-nav{gap:16px}.docs-layout{grid-template-columns:1fr}#docs-sidebar{display:none}.docs-main{grid-column:1}.docs-content{padding:32px 20px 60px}.footer-inner{grid-template-columns:1fr;gap:24px;padding:0 20px}.footer-bottom{flex-direction:column;gap:8px;padding:16px 20px 0;text-align:center}}\n"
    "@media(max-width:480px){nav.header-nav .nav-link:not(.nav-link-cta){display:none}}\n"
)

# ── content/config.ts ──────────────────────────────────────
FILES["src/content/config.ts"] = """import { defineCollection, z } from 'astro:content';
const base = z.object({
  title: z.string(),
  description: z.string().optional(),
  order: z.number().optional(),
  section: z.string().optional(),
});
export const collections = {
  docs: defineCollection({ type: 'content', schema: base }),
  'getting-started': defineCollection({ type: 'content', schema: base }),
  security: defineCollection({ type: 'content', schema: base }),
  glossary: defineCollection({ type: 'content', schema: base }),
};
"""

# ── Header.astro ───────────────────────────────────────────
FILES["src/components/Header.astro"] = """---
const { activePage } = Astro.props;
---
<header id="site-header">
  <a href="https://covenant-lang.org" class="header-brand" aria-label="Covenant home">
    <div class="header-logo-wrap" aria-hidden="true">
      <svg width="32" height="32" viewBox="0 0 96 96" id="header-svg">
        <path d="M 32 20 L 20 20 L 20 76 L 32 76" stroke="#1a1a1a" stroke-width="4" fill="none" stroke-linecap="square"/>
        <path d="M 64 20 L 76 20 L 76 76 L 64 76" stroke="#1a1a1a" stroke-width="4" fill="none" stroke-linecap="square"/>
        <rect x="40" y="40" width="16" height="16" fill="#7C3AED" id="header-square"/>
      </svg>
    </div>
    <span class="header-brand-name">Covenant</span>
    <span class="header-badge">V0.7 GA</span>
  </a>
  <div class="header-spacer"></div>
  <nav class="header-nav" aria-label="Primary navigation">
    <a href="https://covenant-lang.org/manifesto.html" class="nav-link">Manifesto</a>
    <a href="https://covenant-lang.org/#architecture" class="nav-link">Architecture</a>
    <a href="https://covenant-lang.org/#audited" class="nav-link">Audit</a>
    <a href="/getting-started/01-install" class="nav-link">Install</a>
    <a href="https://covenant-lang.org/examples" class="nav-link">Examples</a>
    <a href="/" class="nav-link active">Docs</a>
    <a href="https://github.com/Valisthea/covenant-lang" target="_blank" rel="noopener" class="nav-link">GitHub</a>
    <a href="https://x.com/Covenant_Lang" target="_blank" rel="noopener" class="nav-link-cta">&#x2197; @Covenant_Lang</a>
  </nav>
</header>
<script>
const hdr = document.getElementById('site-header');
if(hdr){const f=()=>hdr.classList.toggle('scrolled',window.scrollY>10);window.addEventListener('scroll',f,{passive:true});f();}
const sq=document.getElementById('header-square');
if(sq){let s=1,d=1;setInterval(()=>{s+=d*.004;if(s>=1.12)d=-1;if(s<=.88)d=1;sq.setAttribute('transform',`translate(48,48) scale(${s}) translate(-48,-48)`);},40);}
</script>
"""

# ── Footer.astro ───────────────────────────────────────────
FILES["src/components/Footer.astro"] = """---
---
<footer id="site-footer">
  <div class="footer-inner">
    <div class="footer-brand">
      <div class="footer-brand-row">
        <svg width="24" height="24" viewBox="0 0 96 96" aria-hidden="true">
          <path d="M 32 20 L 20 20 L 20 76 L 32 76" stroke="#1a1a1a" stroke-width="4" fill="none" stroke-linecap="square"/>
          <path d="M 64 20 L 76 20 L 76 76 L 64 76" stroke="#1a1a1a" stroke-width="4" fill="none" stroke-linecap="square"/>
          <rect x="40" y="40" width="16" height="16" fill="#7C3AED"/>
        </svg>
        <span class="footer-brand-name">Covenant</span>
      </div>
      <p class="footer-by">by Kairos Lab</p>
      <p class="footer-tagline">where cryptographic guarantees become language primitives</p>
    </div>
    <div>
      <span class="footer-col-title">Contact</span>
      <a href="mailto:covenant@kairos-lab.org" class="footer-link">covenant@kairos-lab.org</a>
      <a href="https://x.com/Covenant_Lang" target="_blank" rel="noopener" class="footer-link">@Covenant_Lang on X</a>
      <a href="https://x.com/Valisthea" target="_blank" rel="noopener" class="footer-link">@Valisthea on X</a>
    </div>
    <div>
      <span class="footer-col-title">Repository</span>
      <a href="https://github.com/Valisthea/covenant-lang" target="_blank" rel="noopener" class="footer-link-mono">github.com/Valisthea/covenant-lang</a>
      <a href="https://covenant-lang.org/manifesto.html" class="footer-link" style="margin-top:12px;">Manifesto</a>
      <a href="https://covenant-lang.org/manifesto.html#architecture" class="footer-link">Architecture spec</a>
      <a href="/" class="footer-link">Docs home</a>
    </div>
  </div>
  <div class="footer-bottom">
    <p class="footer-closing">V0.7 GA &mdash; stable for early-adopter production use.</p>
    <span class="footer-license">Specs: CC0-1.0 &middot; Compiler: Apache-2.0</span>
  </div>
</footer>
"""

# ── Callout.astro ──────────────────────────────────────────
FILES["src/components/Callout.astro"] = """---
const { type = 'info', title } = Astro.props;
const icons = { info: 'i', tip: '+', warning: '!', danger: 'x' };
const icon = icons[type] ?? 'i';
---
<div class:list={['callout', `callout--${type}`]} role="note">
  <span class="callout-icon" aria-hidden="true">{icon}</span>
  <div class="callout-body">
    {title && <strong>{title} </strong>}
    <slot />
  </div>
</div>
"""

# ── Sidebar.astro ──────────────────────────────────────────
FILES["src/components/Sidebar.astro"] = """---
const { currentPath } = Astro.props;
const nav = [
  { title: 'Getting Started', links: [
    { href: '/getting-started/01-install', label: '01 - Installation' },
    { href: '/getting-started/02-first-contract', label: '02 - First Contract' },
    { href: '/getting-started/03-cli-reference', label: '03 - CLI Reference' },
  ]},
  { title: 'Fundamentals', links: [
    { href: '/examples/01-hello-contract', label: '01 - Hello Contract' },
    { href: '/examples/02-fields-and-storage', label: '02 - Fields & Storage' },
    { href: '/examples/03-actions-events-errors', label: '03 - Actions, Events & Errors' },
    { href: '/examples/04-guards', label: '04 - Guards' },
    { href: '/examples/05-external-calls', label: '05 - External Calls' },
  ]},
  { title: 'Standards', links: [
    { href: '/examples/06-erc20-token', label: '06 - ERC-20 Token' },
    { href: '/examples/07-fhe-basics', label: '07 - FHE Basics' },
    { href: '/examples/08-encrypted-token', label: '08 - Encrypted Token' },
    { href: '/examples/09-post-quantum-signatures', label: '09 - Post-Quantum Sigs' },
    { href: '/examples/10-zero-knowledge-proofs', label: '10 - Zero-Knowledge Proofs' },
  ]},
  { title: 'Advanced', links: [
    { href: '/examples/11-cryptographic-amnesia', label: '11 - Cryptographic Amnesia' },
    { href: '/examples/12-uups-upgradeable', label: '12 - UUPS Upgradeable' },
    { href: '/examples/13-beacon-proxy', label: '13 - Beacon Proxy' },
    { href: '/examples/14-oracle-integration', label: '14 - Oracle Integration' },
    { href: '/examples/15-deploy-to-sepolia', label: '15 - Deploy to Sepolia' },
  ]},
  { title: 'Security', links: [
    { href: '/security/audit-report', label: 'Audit Report' },
    { href: '/security/critical-findings', label: 'Critical Findings' },
    { href: '/security/secure-patterns', label: 'Secure Patterns' },
    { href: '/security/known-pitfalls', label: 'Known Pitfalls' },
  ]},
  { title: 'Reference', links: [
    { href: '/glossary', label: 'Glossary' },
  ]},
];
---
<aside id="docs-sidebar" aria-label="Documentation navigation">
  <div class="search-wrap">
    <input id="search-input" type="search" placeholder="Search docs..." autocomplete="off" aria-label="Search" />
    <div id="search-results" aria-live="polite"></div>
  </div>
  {nav.map(section => (
    <div class="sidebar-section">
      <span class="sidebar-section-title">{section.title}</span>
      {section.links.map(link => (
        <a href={link.href} class:list={['sidebar-link', { active: currentPath === link.href }]}>{link.label}</a>
      ))}
    </div>
  ))}
</aside>
<script>
async function initSearch() {
  const input = document.getElementById('search-input');
  const resultsEl = document.getElementById('search-results');
  if (!input || !resultsEl) return;
  const pagefind = await import('/pagefind/pagefind.js').catch(() => null);
  if (!pagefind) { input.placeholder = 'Search (build required)'; return; }
  await pagefind.init();
  let t;
  input.addEventListener('input', () => {
    clearTimeout(t);
    t = setTimeout(async () => {
      const q = input.value.trim();
      if (!q) { resultsEl.innerHTML = ''; return; }
      const r = await pagefind.search(q);
      const top = await Promise.all(r.results.slice(0,6).map(x => x.data()));
      resultsEl.innerHTML = top.length === 0
        ? '<p style="color:var(--ink-faint);font-size:8.5pt;padding:4px 0">No results</p>'
        : top.map(r => '<a class="search-result-item" href="' + r.url + '"><div class="search-result-title">' + (r.meta?.title || r.url) + '</div><div class="search-result-excerpt">' + (r.excerpt || '') + '</div></a>').join('');
    }, 220);
  });
}
initSearch();
</script>
"""

# ── DocsLayout.astro ───────────────────────────────────────
FILES["src/layouts/DocsLayout.astro"] = """---
import Header from '../components/Header.astro';
import Sidebar from '../components/Sidebar.astro';
import Footer from '../components/Footer.astro';
import '../styles/global.css';
const { title, description = 'Covenant language documentation.', prev, next, breadcrumb } = Astro.props;
const currentPath = Astro.url.pathname;
const pageTitle = title ? title + ' - Covenant Docs' : 'Covenant Docs';
---
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>{pageTitle}</title>
  <meta name="description" content={description}/>
  <meta property="og:title" content={pageTitle}/>
  <meta property="og:description" content={description}/>
  <meta property="og:image" content="https://covenant-lang.org/og-image.png"/>
  <link rel="icon" href="https://covenant-lang.org/favicon.svg" type="image/svg+xml"/>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
  <link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;1,400;1,500&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet"/>
  <link rel="canonical" href={"https://docs.covenant-lang.org" + currentPath}/>
</head>
<body>
  <Header/>
  <div class="docs-layout">
    <Sidebar currentPath={currentPath}/>
    <main class="docs-main" id="main-content">
      <article class="docs-content" data-pagefind-body>
        {breadcrumb && (
          <nav class="breadcrumb" aria-label="Breadcrumb">
            <a href="/">Docs</a>
            {breadcrumb.map((c, i) => (
              <>
                <span aria-hidden="true">/</span>
                {c.href ? <a href={c.href}>{c.label}</a> : <span>{c.label}</span>}
              </>
            ))}
          </nav>
        )}
        <slot/>
        {(prev || next) && (
          <nav class="doc-nav" aria-label="Page navigation">
            {prev ? <a href={prev.href} class="doc-nav-link prev"><span>Previous</span>{prev.label}</a> : <span/>}
            {next ? <a href={next.href} class="doc-nav-link next"><span>Next</span>{next.label}</a> : <span/>}
          </nav>
        )}
      </article>
    </main>
  </div>
  <Footer/>
</body>
</html>
"""

# ── Pages ──────────────────────────────────────────────────
FILES["src/pages/index.astro"] = """---
import DocsLayout from '../layouts/DocsLayout.astro';
---
<DocsLayout title="Covenant Language Documentation" description="Official documentation for Covenant - post-quantum, FHE, ZK smart contract language.">
  <h1>Covenant Language Docs</h1>
  <p style="font-family:'EB Garamond',serif;font-size:1.2rem;font-style:italic;color:var(--ink-mute);margin-bottom:2rem;">where cryptographic guarantees become language primitives</p>
  <p>Covenant is a declarative smart contract language that compiles to EVM bytecode. Post-quantum signatures, FHE, zero-knowledge proofs, and cryptographic amnesia are first-class language primitives.</p>
  <h2>Quick start</h2>
  <pre><code>cargo install covenant-cli
covenant new my-contract
cd my-contract
covenant build</code></pre>
  <h2>Browse</h2>
  <ul>
    <li><a href="/getting-started/01-install">Getting Started</a> - Install the CLI and write your first contract</li>
    <li><a href="/examples/01-hello-contract">By Example</a> - 15 annotated chapters from Hello Contract to Sepolia deployment</li>
    <li><a href="/security/audit-report">Security</a> - OMEGA V4 audit: 41 findings, all resolved</li>
    <li><a href="/glossary">Glossary</a> - 100+ terms: keywords, types, FHE primitives, ZK, PQ</li>
  </ul>
  <h2>V0.7 GA highlights</h2>
  <ul>
    <li><strong>Post-quantum signatures</strong> - Dilithium3 (NIST FIPS 204), <code>@pq_signed</code></li>
    <li><strong>FHE</strong> - <code>encrypted&lt;T&gt;</code>, <code>fhe_add</code>, <code>fhe_mul</code>, scheme-agnostic precompiles</li>
    <li><strong>ZK proofs</strong> - <code>zk_prove</code> / <code>zk_verify</code>, Groth16 / PLONK / Halo2</li>
    <li><strong>Cryptographic amnesia</strong> - <code>amnesia {{ }}</code> blocks, two-pass provable erasure</li>
    <li><strong>Multi-target</strong> - EVM, Aster Chain (ID 1996), WASM</li>
    <li><strong>LSP</strong> - 38+ lint detectors in VS Code</li>
    <li><strong>OMEGA V4 audited</strong> - 41 findings, 5 Critical, all resolved</li>
  </ul>
</DocsLayout>
"""

FILES["src/pages/glossary.astro"] = """---
import { getCollection } from 'astro:content';
import DocsLayout from '../layouts/DocsLayout.astro';
const entries = await getCollection('glossary');
const entry = entries[0];
const { Content } = entry ? await entry.render() : { Content: null };
---
<DocsLayout title="Glossary" description="Complete glossary of Covenant language terms." breadcrumb={[{label:'Glossary'}]}>
  {Content ? <Content/> : <p>Glossary coming soon.</p>}
</DocsLayout>
"""

FILES["src/pages/getting-started/[slug].astro"] = """---
import { getCollection } from 'astro:content';
import DocsLayout from '../../layouts/DocsLayout.astro';
export async function getStaticPaths() {
  const pages = await getCollection('getting-started');
  return pages.map(entry => ({ params: { slug: entry.slug }, props: { entry } }));
}
const { entry } = Astro.props;
const { Content } = await entry.render();
const all = (await getCollection('getting-started')).sort((a,b) => (a.data.order??99)-(b.data.order??99));
const idx = all.findIndex(e => e.slug === entry.slug);
const prev = idx > 0 ? all[idx-1] : null;
const next = idx < all.length-1 ? all[idx+1] : null;
---
<DocsLayout title={entry.data.title} description={entry.data.description}
  breadcrumb={[{label:'Getting Started',href:'/getting-started/01-install'},{label:entry.data.title}]}
  prev={prev ? {href:'/getting-started/'+prev.slug,label:prev.data.title} : undefined}
  next={next ? {href:'/getting-started/'+next.slug,label:next.data.title} : undefined}>
  <Content/>
</DocsLayout>
"""

FILES["src/pages/examples/[slug].astro"] = """---
import { getCollection } from 'astro:content';
import DocsLayout from '../../layouts/DocsLayout.astro';
export async function getStaticPaths() {
  const pages = await getCollection('docs');
  return pages.map(entry => ({ params: { slug: entry.slug }, props: { entry } }));
}
const { entry } = Astro.props;
const { Content } = await entry.render();
const all = (await getCollection('docs')).sort((a,b) => (a.data.order??99)-(b.data.order??99));
const idx = all.findIndex(e => e.slug === entry.slug);
const prev = idx > 0 ? all[idx-1] : null;
const next = idx < all.length-1 ? all[idx+1] : null;
---
<DocsLayout title={entry.data.title} description={entry.data.description}
  breadcrumb={[{label:'Examples',href:'/examples/01-hello-contract'},{label:entry.data.title}]}
  prev={prev ? {href:'/examples/'+prev.slug,label:prev.data.title} : undefined}
  next={next ? {href:'/examples/'+next.slug,label:next.data.title} : undefined}>
  <Content/>
</DocsLayout>
"""

FILES["src/pages/security/[slug].astro"] = """---
import { getCollection } from 'astro:content';
import DocsLayout from '../../layouts/DocsLayout.astro';
export async function getStaticPaths() {
  const pages = await getCollection('security');
  return pages.map(entry => ({ params: { slug: entry.slug }, props: { entry } }));
}
const { entry } = Astro.props;
const { Content } = await entry.render();
const all = (await getCollection('security')).sort((a,b) => (a.data.order??99)-(b.data.order??99));
const idx = all.findIndex(e => e.slug === entry.slug);
const prev = idx > 0 ? all[idx-1] : null;
const next = idx < all.length-1 ? all[idx+1] : null;
---
<DocsLayout title={entry.data.title} description={entry.data.description}
  breadcrumb={[{label:'Security'},{label:entry.data.title}]}
  prev={prev ? {href:'/security/'+prev.slug,label:prev.data.title} : undefined}
  next={next ? {href:'/security/'+next.slug,label:next.data.title} : undefined}>
  <Content/>
</DocsLayout>
"""

# ── Getting Started markdown files (already written via heredoc) ──
# Verify they exist, write if missing
import os
BASE = "/tmp/covenant-lang/docs-src"
GS = os.path.join(BASE, "src/content/getting-started")

if not os.path.exists(os.path.join(GS, "01-install.md")):
    FILES["src/content/getting-started/01-install.md"] = "---\ntitle: Installation\norder: 1\n---\n# Installation\n\ncargo install covenant-cli\n"
if not os.path.exists(os.path.join(GS, "02-first-contract.md")):
    FILES["src/content/getting-started/02-first-contract.md"] = "---\ntitle: First Contract\norder: 2\n---\n# First Contract\n"
if not os.path.exists(os.path.join(GS, "03-cli-reference.md")):
    FILES["src/content/getting-started/03-cli-reference.md"] = "---\ntitle: CLI Reference\norder: 3\n---\n# CLI Reference\n"

# ── Execute all file writes ──────────────────────────────────
for rel, content in FILES.items():
    path = os.path.join(BASE, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  wrote: " + rel)

print("\nDone!")
