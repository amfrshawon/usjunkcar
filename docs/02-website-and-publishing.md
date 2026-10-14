# Website parity, content and publication

## A-to-Z inventory before implementation

Reference: `https://www.usjunkcars.com/`. The stored fixture is the homepage only. The following families are known from observed navigation; individual interior-page designs have not yet been audited. The implementation agent must inspect them rather than extrapolate all interiors from the homepage.

Create `reference/routes.csv` with source URL, destination path, family, screenshot IDs at desktop/mobile sizes, components/interactions, data dependencies, design status, implementation status, publication status and acceptance evidence. Discover the sitemap and internal links, normalize duplicates/canonicals and record the discovered total. Do not bulk publish discovered routes. Use representative fixtures to design templates, then inventory the content variants separately.

| Family | Observed examples / scope | Required designs and behavior |
| --- | --- | --- |
| Homepage | `/` | Full header-to-footer parity, menus, map, carousels, video, banner, forms |
| Quote intake | `/online-quote` | Vehicle/contact/location steps, validation, consent, photos, submission and recovery |
| Service-area directory | `/areas` | State/county/city navigation, search and empty states |
| State pages | `/california`, `/texas`, and other states | Location copy, local CTA, directory links and proof content |
| County/borough pages | `/texas/tx_dallas_car_salvage.html`, other source patterns | Breadcrumbs, areas served and links |
| City pages | `/california/los_angeles_auto_removal.html` and others | City template and unique local content |
| Condition/service pages | `/car-condition-damaged`, scrap, totaled, non-running, missing parts, etc. | Condition copy, appropriate qualification fields and CTA |
| Vehicle type | `/car-body-rv` and source body-type links | Type-specific templates and content |
| Title/registration | `/car-title-without-title` and observed registration links | Actual business eligibility rules; no invented legal guarantees |
| Pricing | `/car-prices`, cash-for-500 source service | Explain genuine valuation factors, approved claims only |
| Brand/model | `/sell-my-acura`, other brands and discovered model routes | Brand template, model variants and internal navigation |
| Company | `/about_us`, `/contact-us` | Identity, contact details, real contact submission |
| FAQ | `/faqs` and `?name=` deep links | Accessible accordions, selected-question linking, no dead `#` links |
| Blog | `/blog`, article URLs | List/detail, categories if present, author/date, pagination |
| VIN decoder | `/vin-decoder`, make-specific variants | Input/loading/result/error/unsupported states, real provider adapter |
| Value calculator | `/totaled-car-value-calculator` | Approved rules, assumptions and result states |
| Paid reports | `/autocheck-report`, `/vin-photo-report` | Private designs first; provider/payment prerequisites must be explicit |
| Legal | `/policy`, `/terms-and-condition` | Owner-approved policies for the new business |
| System pages | 404, validation, unavailable and success states | Consistent style, helpful recovery, no false submission success |
| Private application | dashboard, auth, preview gallery | Designed separately for operations, not inferred from source marketing |

## Initial ten-page proposal

This is a proposed selection because the owner specified a maximum, not the exact URLs. `launch-pages.json` is a planning artifact, not runtime publication permission. Every entry starts unapproved; the owner can exchange entries while keeping the cap.

| # | New public path | Purpose |
| --- | --- | --- |
| 1 | `/` | Homepage |
| 2 | `/online-quote` | Primary lead intake |
| 3 | `/areas` | Approved service-area directory |
| 4 | `/about-us` | Business identity |
| 5 | `/contact-us` | Contact and secondary lead intake |
| 6 | `/faqs` | Seller questions |
| 7 | `/car-prices` | Pricing explanation |
| 8 | `/car-condition-damaged` | Initial service landing page |
| 9 | `/privacy-policy` | Privacy and data handling |
| 10 | `/terms-and-conditions` | Service/site terms |

No public state/city, brand, blog, VIN or report pages initially. Directory links for unlaunched locations should select the location in the quote flow, not expose drafts or point to the reference business. An approved location page can replace another candidate later.

The cap counts distinct anonymous marketing/content HTML routes, including legal pages, paginated/filter variants that render distinct content, and localized variants. API endpoints, static assets, sitemap/robots, redirects, error responses and the minimal authentication entry are infrastructure, not marketing pages. Dashboard and preview screens are authenticated. Keep quote success inline on `/online-quote` to avoid an eleventh content page. Do not use query strings to evade the cap.

## Publication mechanism

Maintain a versioned runtime registry containing route ID, normalized path, family/template, content revision, `draft|review|approved|published|archived`, allowed environments, approved revision and owner approval reference. Publishing requires both the approved production allowlist and an approved immutable content revision. A database `published=true` alone cannot create a new public route.

At build time validate uniqueness, maximum ten public routes, valid content, metadata, destination links and approval evidence. At request time verify the registry again before rendering/fetching content. New route defaults to draft and fails closed if config is absent. Unapproved public paths return a real 404 with no content, including RSC requests, generated static paths and alternate encoded/trailing-slash/query variants.

Private previews use `/preview/<page-id>` after server-verified staff/editor authentication and authorization. Serve `Cache-Control: private, no-store`, `X-Robots-Tag: noindex, nofollow`; never put private pages in shared caches, public data APIs, sitemap, search indexes or static prerender exports. Guessing IDs, changing cookies or adding `?preview=true` must not reveal content. Protect development deployment URLs and `dev.usjunkcars.si` with deployment access control plus app auth as appropriate; noindex is an additional signal only.

Private uploaded content/assets also require authorization/signed URLs. The current GitHub repository is public: unpublished designs in Git are visible to anyone who reads the repository even if the website is protected. If source-design confidentiality is required, the owner must explicitly choose private repository visibility before those designs are committed. Do not change visibility silently.

## Design parity and accessibility

Capture desktop at 1440 and 1280, tablet at 768, mobile at 390 and 360 CSS pixels. Compare original and clone at identical viewport, font load, banner state and active carousel item. Verify every section, not only the first screen. Preserve typography, colors, spacing, image crops, icons, borders, sticky behavior, footer and all interaction states. Record intentional changes for new identity or accessibility.

Homepage checks include all 51 state/DC labels, map targets, title conditions, vehicle conditions and body types, registration variants, offers table, reviews, brands, FAQs, two article cards, featured logos and full footer. Do not retain source testimonials or numeric claims as this business's facts without approval.

Keyboard navigation must reach all controls; menus/modals have correct focus handling; forms expose labels and errors; touch controls work without hover; reduced-motion mode is honored; images have appropriate alternative text; readable contrast is checked. Use real skeleton, error, empty, offline and pending-submit states.

## SEO and performance

Canonical/social/schema origins always use `https://usjunkcars.si`. Use truthful business data and unique page copy. Sitemap contains only approved public URLs. Development and dashboard stay non-indexable. Redirect old path shapes on this domain only when their destination is published; do not create public placeholder pages. Optimize local images, explicit dimensions and fonts, remove tracking inherited from the reference, and measure the final bundle. Proposed targets: LCP ≤2.5s, CLS ≤0.1 and INP ≤200ms at the 75th percentile once field data exists; prelaunch lab tests are proxies, not field evidence.
