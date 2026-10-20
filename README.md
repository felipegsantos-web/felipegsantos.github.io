# felipegsantos.com

Bilingual (English/Spanish) academic website of Felipe G. Santos, built with [Jekyll](https://jekyllrb.com/) and deployed to GitHub Pages with GitHub Actions.

**Live site:** <https://www.felipegsantos.com>

## How the site is built

Content lives in `_data/` and the pages are templates, so a new publication, media item or news item is a change to one YAML file. Both languages and the five theme pages are generated from the same entries.

```
_data/          content: publications, themes, media, news, projects, cv, book, profile, i18n
_layouts/       the page layout
_includes/      head, header, footer, cards, lists, icons
en/  es/        one page per URL (front matter + a few includes)
assets/         css, js, favicons
images/ documents/   photo and CV PDF
index.html      language router at / (plain links to /en/ and /es/ for readers without JavaScript)
sitemap.xml  llms.txt   generated from the pages and _data/ (lastmod from git, see _plugins/last_modified.rb)
robots.txt      static
_plugins/       last_modified.rb: git dates for the sitemap
scripts/        checks that run in CI
docs/           historical notes and publications-content.md (verified publication content, the source for publication data)
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
  oa_url: https://...          # optional: link to a free PDF (never ResearchGate)
  oa_version: published        # published | accepted (only needed with oa_url)
```

Open-access order of preference: the publisher's open version, then City Research Online, then the CEU repository. Run `python3 scripts/check_oa_links.py` after changing any `oa_url` (needs network and `pdftotext`; not part of CI). `isbn_print` / `isbn_ebook` (book only) feed the JSON-LD and the book page.

Optional fields: `venue_es` (if the Spanish line differs), `book_title`, `publisher`, `volume`, `issue`, `pages`, `online` (online-first date when it differs from `year`), `summary_list_en` / `summary_list_es` (bullet list after the summary), `page` (slug of a dedicated page under the publications section), `version_of` (id of the article a chapter reproduces; shows a linked line). `year` is the year of the issue or volume. Leave `why_en` / `why_es` out when there is no "Why it matters" line. `edited_volume` adds "(eds.)" ("(coords.)" in Spanish) after the authors; `type: profile` shows a Profile badge. Author names that differ from `name` in `profile.yml` (e.g. as printed in a book) go in `name_variants` so they are still highlighted.

`python3 scripts/print_publications.py` prints authors, year, venue, volume, issue and pages for every work, to compare with `docs/publications-content.md`.

### Identity, structured data and theme texts

`_data/profile.yml` is the single source for the JSON-LD `Person` (`_includes/jsonld-person.html`), `llms.txt`, the footer and the meta tags: name and variants, position, canonical descriptions (`description_en` / `description_es`), profiles (`profiles` are the icons, `other_profiles` only feed `sameAs` and `llms.txt`) and the images. Each publication gets its own block from `_includes/jsonld-work.html`. The lead paragraph and the question sections of each theme page are in `_data/theme-answers.yml`.

### A media item

Add an entry at the top of `_data/media.yml`: `outlet`, `date` (year), `format` (press, radio, podcast, opinion), `theme` (far_right, protest, democracy), `language` of the piece, `url`, `title_en`, `title_es`.

### A project

Add an entry to `_data/projects.yml` with `status: current` or `past` (newest first within each). Only fill in what a source gives: `title`, `funder`, `host`, `years`, `role`, `grant`, `description_en` / `description_es`. The research page and the CV section "Grants and projects" are generated from it. The posts shown on the CV and the homepage sentence come from `posts` in `_data/profile.yml`; the email address is `email` in the same file and is the only place it is written.

### A news item

Add an entry at the top of `_data/news.yml` (the homepage shows them in file order). `ref` is the id of the media or publication entry it points to (used for the analytics event name). `link` is the linked text; `rest_en` / `rest_es` is the text after it.

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
3. `python3 scripts/check_hreflang.py`: every English page has a Spanish pair and the `hreflang` tags are reciprocal; `x-default` is the English version of the same page.
4. `python3 scripts/check_jsonld.py _site`: every JSON-LD block parses, publication blocks have the authors of `_data/publications.yml` in order, and the Person is defined once on the homepages and CV pages only.
5. `python3 scripts/check_theme_answers.py`: word counts, sentence counts and links of `_data/theme-answers.yml`.

`scripts/paridad.py OLD_DIR _site` compares two builds page by page (text, metadata, JSON-LD, links and images). It was used to check the migration to Jekyll against the previous static HTML.

## Branches

| Branch | Purpose |
|--------|---------|
| `main` | Production. Every push is built and deployed. |
| `migracion-jekyll` | The Jekyll migration (PR 1 of 4). |
| `legacy-site-archive`, `redesign-bilingual-2026`, `feature/discoverability-content-updates`, `code-reference` | Older branches kept as history. They are not sources for the current site. |

## Analytics

[GoatCounter](https://www.goatcounter.com/) counts page views (`https://felipegsantos.goatcounter.com`); the script is loaded once, in `_layouts/default.html`. There are no cookies and no other analytics. Clicks are counted with `data-goatcounter-click` on the link, with stable names: `cv-download`, `email`, `publication-<id>`, `media-<id>` (ids from `publications.yml` and `media.yml`) and `profile-<site>` (the profile icons). The root redirect page (`index.html`) is not instrumented. Search Console is verified by DNS, so no verification tag is needed.

There is no contact form: the contact page shows the email address only.

## Design

- Light/dark theme: system preference or the header toggle; the choice is stored in `localStorage` (`site-theme`).
- Language: the `site_lang` cookie (365 days) set by the language toggle; the root router uses it.
- Fonts: Playfair Display (headings) and Inter (body), from Google Fonts.
- Colours are defined in `assets/css/tokens.css`.
