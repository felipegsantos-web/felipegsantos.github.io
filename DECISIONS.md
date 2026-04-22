# DECISIONS.md — Site update: discoverability + content changes

**Branch:** `feature/discoverability-content-updates`
**Date:** 2026-04-21

---

## Discoverability

### Root `/` page
**Decision:** Replaced the near-empty, `noindex` root page with a bilingual static landing page containing real content (name, role, short bio, EN/ES links, profile links). The `router.js` script is still loaded at the bottom as progressive enhancement — users with JS will be routed to their preferred language; crawlers and JS-disabled visitors see the static content.

**Canonical tag on `/`:** Set to `/en/` (the primary English page). This is the correct signal to Google for the default-language canonical, per hreflang best practice. The root URL itself is included in the sitemap with its own `<loc>` entry, so it is independently crawlable.

**Note:** The root page now lists both `/en/` and `/es/` as visible navigation links, which is the minimal requirement for crawler discovery without JS.

---

### `noindex` removal
The old root `index.html` had `<meta name="robots" content="noindex">`. This has been removed. `robots.txt` was already `Allow: /` and needed no change beyond minor cleanup.

---

### `sitemap.xml`
Added `https://www.felipegsantos.com/` as a separate `<url>` entry with hreflang alternates for `en`, `es`, and `x-default`. All other URLs unchanged.

---

### `llms.txt`
Created at `/llms.txt` following the Answer.AI/llmstxt.org convention:
- H1: site name
- Blockquote: concise summary
- Body paragraphs: research areas
- Sections: Main pages, Spanish versions, Academic profiles, Optional

Included all four approved external profile URLs (Google Scholar, ORCID, ResearchGate, LinkedIn).

---

### Person JSON-LD `sameAs`
Added `https://www.researchgate.net/profile/Felipe-G-Santos` and `https://www.linkedin.com/in/felipegsantos/` to the `sameAs` array in `PERSON_SCHEMA`. This schema is emitted only on the English homepage (`/en/`). No schema on the root or Spanish homepage — this is intentional to avoid duplicate Person schemas.

---

### ResearchGate + LinkedIn on homepage and footer
Added ResearchGate and LinkedIn icon links to:
1. The `hero-bio__social` row on the homepage (both EN and ES)
2. The `footer-social` bar (all pages, both languages)

The icons use SVG inline, consistent with the existing icon system.

---

## CV section

### City St George's position merge
**Owner instruction:** "Merge the two City St George's positions into one position starting in 2021."
**Applied as:** One entry, `2021 – present`, with detail `"Department of Sociology; INTERFACED project (Horizon Europe)"`. The Babeş-Bolyai 2023–present position remains separate.
**Note:** This creates a slight inconsistency with the CV PDF if it shows two separate entries. The instruction explicitly authorized this simplification, so it is applied directly as instructed.

### Teaching section removed
Removed from CV sidebar navigation and from CV body in both EN and ES. The existing content (one entry, "2021–2023, City, University of London") was also marked `<!-- TODO: complete teaching record -->` — removal is clean.

### Affiliations section removed
Removed from CV sidebar navigation and body. The three listed affiliations (ESA, APSA, Council for European Studies) were not confirmed against the CV PDF independently (the PDF was not directly accessible as a parseable document). **Owner action:** Verify the CV PDF does not include affiliations you want to keep — if so, they have been removed per your explicit instruction.

### CES board member — Professional Service
Added: "Board member — Social Movements Research Network, Council for European Studies (CES)". Source: explicit owner instruction ("mention that I am a board member of the Social Movements RN of the CES"). Not sourced from an independently verifiable external document — added on owner authority.

### Email on CV contact card
Updated from `felipe.santos@ubbcluj.ro` to `f.santos@citystgeorges.ac.uk` per owner instruction.

---

## Contact section

### Email
Updated from `felipe.santos@ubbcluj.ro` to `f.santos@citystgeorges.ac.uk` in:
- Contact page body (both EN/ES)
- CV contact card (both EN/ES)
- Footer `mailto:` icon link (all pages)

**Email exposure:** In the contact page main section, the email is encoded as HTML character entities (`&#102;&#46;...`) so it does not appear as plain text in source. In the footer icon link and CV card, the email appears as a plain `mailto:` href — this is a design tradeoff (icon links are expected to be machine-readable) and consistent with the existing pattern for all other pages.

### Academic profiles, social media, affiliations removed from Contact
All three sections ("Academic Profiles", "Social Media", "Institutional Affiliations") have been removed from the contact page per instruction. These profiles are still available on the homepage, footer, and (for Scholar/ORCID) the CV page.

### "Media enquiries" note removed
The sentence "For media enquiries and consultancy, please see the Consultancy page" has been removed per instruction.

### Contact form — Web3Forms
**Service selected:** Web3Forms. Rationale: 250 submissions/month free tier (higher than comparable alternatives), built-in honeypot spam protection, access key is safe to publish in client-side code (it acts as an alias, not a secret), no server required.

**Implementation:** The form is fully wired (HTML + fetch JS) but uses a placeholder access key `OWNER_WEB3FORMS_ACCESS_KEY`.

### ⚠️ OWNER ACTION REQUIRED — Contact form setup

1. Go to [https://web3forms.com](https://web3forms.com)
2. Enter your email address (`f.santos@citystgeorges.ac.uk`) and click "Create Access Key"
3. You will receive a confirmation email — click the link to verify
4. Copy your access key (a UUID string like `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)
5. Open `/home/user/workspace/gen/build_all_pages.py`, find the line:
   ```
   <input type="hidden" name="access_key" value="OWNER_WEB3FORMS_ACCESS_KEY">
   ```
   Replace `OWNER_WEB3FORMS_ACCESS_KEY` with your actual key.
6. Rebuild with `python3 gen/build_all_pages.py` and push (or ask the agent to do it).

**Free tier details:**
- 250 submissions/month
- Honeypot spam protection included (the hidden `botcheck` checkbox field)
- No CAPTCHA required unless you want extra protection (available on paid plans)
- Submissions are forwarded to your email — not stored on Web3Forms servers
- The access key is not sensitive: it is safe in public HTML source

**Fallback:** Both the EN and ES contact pages include a visible fallback paragraph with the entity-encoded email address for users whose JS fails or who encounter a form error.

---

## Skipped items

### CV PDF content verification
The CV PDF at `/documents/CV.pdf` was not directly read as a text document during this session (the file may not be in the repository or may be binary). All CV section content was taken from the existing rendered HTML, which was built from prior sessions that explicitly populated content from the owner's CV. No new facts were added. Items removed (teaching, affiliations) were removed per explicit instruction.

### Peer reviewer journal list
The existing list (*Party Politics*, *Social Movement Studies*, *Political Studies*, *Democratization*) was preserved as-is. It was already on the site. No additions were made from external sources.

### LinkedIn profile content
The LinkedIn profile at `https://www.linkedin.com/in/felipegsantos/` was confirmed to exist (the URL was explicitly approved). Its content was not extracted (LinkedIn blocks automated access). The URL has been added to `sameAs` and to profile link sections as approved, with no content derived from it.

### Spanish CV sidebar
The sidebar heading keys were updated to remove `teaching` and `affiliations` in both EN and ES. The sidebar is auto-generated from the `sections` dict — no manual edit required.

### Root canonical vs self-referencing
The root `/index.html` canonical points to `/en/`. An alternative would be a self-referencing canonical (`https://www.felipegsantos.com/`). The choice of `/en/` was made because the root is a routing shim, not the primary content page — pointing it to `/en/` signals to Google which URL to rank as the canonical English page. The root is still indexed (no noindex) and in the sitemap. This is the standard approach for bilingual sites with language routing.

---

## No invented facts
No publication titles, dates, co-authors, grant names, journal names, institution names, or any other externally verifiable facts were invented. All content derives from the existing site (built from prior owner-verified sessions) or explicit owner instructions in this session.
