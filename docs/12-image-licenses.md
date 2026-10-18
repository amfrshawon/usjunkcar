# Image sources and licenses

| Site file (apps/web/public/images/photos/) | Where it's used | Source | License |
| --- | --- | --- | --- |
| `tow-truck-cash-for-junk-cars-*` | Homepage hero | Adobe Stock #1993300031 "Blue Towing Truck Lifting Yellow Sedan Car with Hook" | Adobe Stock free license, owner's Adobe account, 2026-10-15 |
| `junk-car-removal-free-towing-*` | Homepage benefits | Adobe Stock #723267975 "A Transportation Service" | Adobe Stock free license, owner's Adobe account, 2026-10-15 |
| `flatbed-tow-truck-junk-car-pickup-*` | Call-to-action banner (Home, Locations, About, FAQ) | Adobe Stock #1846950729 "Orange tow truck PNG isolated on transparent background" | Adobe Stock free license, owner's Adobe account, 2026-10-15 |

Processing: Adobe Photoshop API background removal (hero and banner), then trimming, fitting to the original layout slots, and WebP plus PNG/JPG encoding at 1x and 2x sizes.

Keep the Adobe Stock license records in the owner's Adobe account. Adobe Stock's standard license does not allow use of these images in a logo or trademark.

## Original artwork (owned by US Junk Cars)

- `images/icons/*.svg`: 49 icons for conditions, titles, paperwork, vehicle types and page sections, drawn for this site by `scripts/build-icons.py`.
- `images/backgrounds/*`: the hero board, the call-to-action banner and the US flag graphic, drawn by `scripts/build-backgrounds.py`. The US flag design itself is public domain.

Still in `apps/web/public` from the reference site, but not loaded by any current page: CSS-only images for page types this site does not have (`frontend/images/base/hero_image-brand_bg.png`, `image-car.png`, `image.png`), small generic UI glyphs referenced by the stylesheet (`frontend/images/icons/`), and car-brand logos in the brand slider (`frontend/images/brands/`, manufacturer trademarks).
