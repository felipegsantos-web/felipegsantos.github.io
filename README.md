# felipegsantos.com

Bilingual (English/Spanish) academic website of Felipe G. Santos, built with [Jekyll](https://jekyllrb.com/) and deployed to GitHub Pages with GitHub Actions.

**Live site:** <https://www.felipegsantos.com>

## How the site is built

Content lives in `_data/` and the pages are templates, so a new publication, media item or news item is a change to one YAML file. Both languages and the five theme pages are generated from the same entries.

```
_data/          content: publications, themes, media, news, projects, cv, profile, i18n
_layouts/       the page layout
_includes/      head, header, footer, cards, lists, icons
en/  es/        one page per URL (front matter + a few includes)
assets/         css, js, favicons
images/ documents/   photo and CV PDF
index.html      language router at / (static, not processed by Jekyll)
sitemap.xml  llms.txt  robots.txt   static files
scripts/        checks that run in CI
docs/           historical notes
```

Every page has `lang` and `ref` in its front matter. `ref` pairs a page with its translation, and the `hreflang` tags are generated from that pair.

Strings in `_data/` may contain inline HTML (`<em>`, `&amp;`) exactly as it should appear on the page.

## Adding content

### A publication

Add an entry to `_data/publications.yml`, newest first (the list keeps file order). It appears in the English and Spanish lists, on the theme pages named in `themes`, in the theme counts and in the JSON-LD.

```yaml
- id: 2027-short-slug          # unique, stable
  type: article                # article | chapter | book | edited_volume | encyclopedia_entry | profile
  status: published
  year: 2027
  authors:                     # in the order they are shown
    - Felipe G. Santos
    - Coauthor Name
  title: Title of the article
  venue: Journal Name          # as displayed (chapters and books: the full line shown)
  doi: 10.1000/xyz123          # optional
  url: https://doi.org/10.1000/xyz123   # where the title links to ("" for no link)
  themes: [protest]            # care | farright | protest | movementparties | democracy
  keywords: [protest, participation]    # used by the page filters
  summary_en: ...
  summary_es: ...
  why_en: ...
  why_es: ...
  oa_url: ""
```

Optional fields: `venue_es` (if the Spanish line differs), `editors`, `book_title`, `publisher`, `volume`, `issue`, `pages`. `edited_volume` adds "(eds.)" after the authors.

### A media item

Add an entry at the top of `_data/media.yml`: `outlet`, `date` (year), `format` (press, radio, podcast, opinion), `theme` (far_right, protest, democracy), `language` of the piece, `url`, `title_en`, `title_es`.

### A news item

Add an entry at the top of `_data/news.yml` (the homepage shows them in file order). `link` is the linked text; `rest_en` / `rest_es` is the text after it.

Interface strings (navigation, buttons, filter labels) are in `_data/i18n.yml`. A new research theme needs an entry in `_data/themes.yml`, a `.theme--<slug>` colour in `assets/css/components.css`, and two page files like `en/publications/theme/care/index.html` (they only contain front matter).

## Preview locally

```bash
bundle install
bundle exec jekyll serve
```

Open <http://localhost:4000/en/>. The root `/` redirects with JavaScript; go straight to `/en/` or `/es/`.

## Deployment

Pushing to `main` runs `.github/workflows/site.yml`: it builds the site, runs the checks below and, only if they pass, publishes `_site` with `actions/upload-pages-artifact` and `actions/deploy-pages`. Pull requests run the build and the checks but do not deploy.

The repository's Pages source must be set to **GitHub Actions** (Settings → Pages). The custom domain is configured there; the `CNAME` file is kept for reference.

## Checks in CI

1. `jekyll build` must finish with no warnings or errors.
2. `htmlproofer ./_site --disable-external`: internal links and images. External links are not checked.
3. `python3 scripts/check_hreflang.py`: every English page has a Spanish pair and the `hreflang` tags are reciprocal.

`scripts/paridad.py OLD_DIR _site` compares two builds page by page (text, metadata, JSON-LD, links and images). It was used to check the migration to Jekyll against the previous static HTML.

## Branches

| Branch | Purpose |
|--------|---------|
| `main` | Production. Every push is built and deployed. |
| `migracion-jekyll` | The Jekyll migration (PR 1 of 4). |
| `legacy-site-archive`, `redesign-bilingual-2026`, `feature/discoverability-content-updates`, `code-reference` | Older branches kept as history. They are not sources for the current site. |

## Design

- Light/dark theme: system preference or the header toggle; the choice is stored in `localStorage` (`site-theme`).
- Language: the `site_lang` cookie (365 days) set by the language toggle; the root router uses it.
- Fonts: Playfair Display (headings) and Inter (body), from Google Fonts.
- Colours are defined in `assets/css/tokens.css`.
