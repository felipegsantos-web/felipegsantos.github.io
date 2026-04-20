# felipegsantos.com — Academic Personal Website

Bilingual English/Spanish academic website for Felipe G. Santos, Research Fellow in Political Sociology.

**Live domain:** [www.felipegsantos.com](https://www.felipegsantos.com)

---

## Branch strategy

| Branch | Purpose |
|--------|---------|
| `main` | **Production** — live at www.felipegsantos.com via GitHub Pages. Do not modify until redesign is approved. |
| `legacy-site-archive` | Full backup of the original site. Used for rollback. |
| `redesign-bilingual-2026` | Working branch for the redesign. Preview and test here. |

**Before launching:** merge `redesign-bilingual-2026` → `main` only after explicit approval.

---

## Site structure

```
/                        → Language router (cookie + browser detection)
/en/                     → English homepage
/en/publications/        → Publications archive (EN)
/en/media/               → Media archive (EN)
/en/cv/                  → CV page (EN)
/en/current-work/        → Current work (EN)
/en/contact/             → Contact (EN)
/es/                     → Spanish homepage
/es/publicaciones/       → Publicaciones (ES)
/es/medios/              → Medios (ES)
/es/cv/                  → CV (ES)
/es/trabajo-actual/      → Trabajo actual (ES)
/es/contacto/            → Contacto (ES)
/assets/css/             → Stylesheets
/assets/js/              → JavaScript
/images/                 → Images (Perfil.png etc.)
/documents/              → CV.pdf and other downloads
CNAME                    → www.felipegsantos.com (do not change)
```

---

## Language architecture

- Root `/` runs a JavaScript router (`assets/js/router.js`).
- On first visit, if no `site_lang` cookie exists:
  - Browser language is `es` → redirect to `/es/`
  - Otherwise → redirect to `/en/`
- If a `site_lang` cookie exists (set when user manually switches language), it takes priority.
- Never overrides an explicitly visited language URL.
- Each page pair has `hreflang` alternate links.
- Root has `x-default` pointing to `/en/`.

**Cookie name:** `site_lang` · **Values:** `en` or `es` · **Expiry:** 365 days

---

## Content system

Content is embedded in HTML pages. To update:

1. Edit the relevant `index.html` in the `en/` or `es/` subdirectory.
2. For new publications, add a `<div class="pub-entry" data-pub data-type="..." data-year="..." data-topics="...">` block to both `/en/publications/` and `/es/publicaciones/`.
3. For new media, add a `<a class="media-item" data-media data-year="..." data-outlet="...">` block to both `/en/media/` and `/es/medios/`.
4. For news/updates on the homepage, edit the `.updates-list` section in `/en/index.html` and `/es/index.html`.

### Adding a publication

```html
<div class="pub-entry" data-pub data-type="article" data-year="2026" data-topics="protest participation">
  <div class="pub-entry__top">
    <span class="pub-entry__year-col">2026</span>
    <div class="pub-entry__body">
      <div style="display:flex;gap:var(--space-2);flex-wrap:wrap;margin-bottom:var(--space-2);">
        <span class="badge badge--published">Published</span>
      </div>
      <h3 style="font-family:var(--font-display);...">
        <a href="https://doi.org/..." target="_blank" rel="noopener">Title of article</a>
      </h3>
      <p style="font-size:var(--text-sm);color:var(--color-text-muted);"><strong>Felipe G. Santos</strong> and Coauthor Name</p>
      <p style="font-size:var(--text-sm);color:var(--color-text-muted);font-style:italic;">Journal Name</p>
    </div>
  </div>
</div>
```

### Status badge classes

| Class | Meaning |
|-------|---------|
| `badge--published` | Published |
| `badge--forthcoming` | Forthcoming |
| `badge--review` | Under review |
| `badge--rr` | Revise & resubmit |
| `badge--ongoing` | Ongoing project |
| `badge--type` | Neutral type label |

---

## CV downloads

Place PDF files in `/documents/`:
- `CV.pdf` — English CV (already present)
- Add `CV_ES.pdf` for Spanish CV when available
- Add `bio_en.pdf` and `bio_es.pdf` for short bios when available

Link buttons are in `/en/cv/index.html` and `/es/cv/index.html`. Add `style="display:none"` to hide buttons for files that don't exist yet.

---

## Analytics (Plausible)

Plausible is loaded via script tag in the `<head>` of all pages:
```html
<script defer data-domain="felipegsantos.com" src="https://plausible.io/js/script.outbound-links.js"></script>
```

To activate, sign up at [plausible.io](https://plausible.io) and add `felipegsantos.com` as a site.

Tracked events (via `data-track` attributes):
- `Publication Click` — outbound publication links
- `Media Click` — outbound media links
- `CV Download` — CV PDF downloads
- `Contact Click` — email and profile links
- `CTA Click` — primary call-to-action buttons

---

## Dark/light mode

The site supports both light and dark mode via:
- System preference detection (`prefers-color-scheme`)
- Manual toggle button in the header
- Theme stored in `sessionStorage`

---

## Launch checklist

Before merging `redesign-bilingual-2026` → `main`:

- [ ] Review all content for accuracy
- [ ] Add any missing publications, media, or CV updates
- [ ] Upload updated `CV.pdf` to `/documents/`
- [ ] Add profile photo update if needed
- [ ] Sign up for Plausible analytics
- [ ] Test on mobile and desktop browsers
- [ ] Verify all links open correctly
- [ ] Check CNAME file still contains `www.felipegsantos.com`
- [ ] Get explicit approval before merging

**DNS and GitHub Pages production settings must NOT be changed until explicitly approved.**

---

## Rollback

To restore the previous site:
```bash
git checkout main
git reset --hard origin/legacy-site-archive
git push --force
```

Or simply delete the new files and restore `index.html` from `legacy-site-archive`.

---

## Local preview

```bash
# Serve locally (Python)
cd /path/to/repo
python3 -m http.server 8080
# Then open: http://localhost:8080/en/
```

Note: The root `/` router requires JavaScript. For local testing, go directly to `/en/` or `/es/`.

---

## Color palette

| Role | Light | Dark |
|------|-------|------|
| Background | `#F6F2EB` | `#181614` |
| Surface | `#FBF8F3` | `#1E1C19` |
| Primary text | `#1F2423` | `#D8D3CB` |
| Muted text | `#5C6664` | `#7D847F` |
| Primary accent | `#0F6B6F` | `#5BA8AC` |
| Secondary accent | `#A35C45` | `#C4806A` |
| Border | `#D9D1C7` | `#373430` |

---

## Fonts

- **Display (headings):** [Playfair Display](https://fonts.google.com/specimen/Playfair+Display) — loaded from Google Fonts
- **Body / UI:** [Inter](https://fonts.google.com/specimen/Inter) — loaded from Google Fonts

---

*Last updated: April 2026*
