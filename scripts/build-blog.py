"""Build the USJunkCars Blog index page (content/pages/blog.html) from content/blog/posts.json
and register /blog/ in content/publication.json.

How it works:
- Topics are 100% dynamic: whenever you declare ANY `category` on a post in content/blog/posts.json
  (whether an existing topic or a brand-new topic), this script automatically:
  1. Adds or updates that topic's filter pill in the "Explore Blog Topics" toolbar.
  2. Creates or updates that topic's dedicated Topic Section on /blog/, sorted with the latest post first.
  3. Places the overall latest post across all topics in the Hero & Featured banner.
  4. Generates the dedicated `/blog/<slug>/` full article route.

Run: python3 scripts/build-blog.py
"""
import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE, PHONE, TEL = 'https://usjunkcars.si', '1-844-512-0697', 'tel:+18445120697'
ISO = '2026-10-18'
PATH, ID = '/blog/', 'blog'
POSTS_FILE = ROOT / 'content/blog/posts.json'

KNOWN_TOPICS = {
    'pricing': {
        'name': 'Scrap & Pricing',
        'icon': '/images/icons/blog-pricing.svg',
        'description': 'How instant cash offers are calculated, reusable parts vs. scrap metal weight, and current payout factors across the USA.',
    },
    'titles': {
        'name': 'Titles & Paperwork',
        'icon': '/images/icons/blog-title-doc.svg',
        'description': 'State-by-state rules for selling a junk car without a title, getting duplicate titles, handling salvage certificates, and clearing liens.',
    },
    'damaged': {
        'name': 'Damaged & Non-Running',
        'icon': '/images/icons/blog-engine-repair.svg',
        'description': 'When to sell vs. repair vehicles with blown engines, bad transmissions, frame damage, flood loss, or failed state inspections.',
    },
    'pickup': {
        'name': 'Pickup & Scams',
        'icon': '/images/icons/blog-pickup-checklist.svg',
        'description': 'How free flatbed towing works, what to remove before the driver arrives, and how to avoid driveway bait-and-switch scams.',
    },
    'recycling': {
        'name': 'Auto Recycling',
        'icon': '/images/icons/blog-eco-recycling.svg',
        'description': 'Inside responsible auto dismantling: hazardous fluid depollution, OEM parts reuse, catalytic metal recovery, and steel recycling.',
    },
    'guides': {
        'name': 'State & Seller Guides',
        'icon': '/images/icons/blog-license-plate.svg',
        'description': 'Step-by-step seller walkthroughs, license plate & insurance cancellation rules, and regional towing guides across all 50 states.',
    },
}


def slugify(text: str) -> str:
    return re.sub(r'^-|-$', '', re.sub(r'[^a-z0-9]+', '-', text.lower()))


def discover_topics(posts: list[dict]) -> list[dict]:
    """Return all topics present in `posts` dynamically, preserving known metadata and auto-creating any newly declared topic."""
    seen: dict[str, dict] = {}
    for p in posts:
        cat_name = p.get('category', 'Seller Guides').strip()
        cat_slug = p.get('categorySlug') or slugify(cat_name)
        p['categorySlug'] = cat_slug
        if cat_slug not in seen:
            meta = KNOWN_TOPICS.get(cat_slug, {})
            seen[cat_slug] = {
                'slug': cat_slug,
                'name': meta.get('name', cat_name),
                'icon': p.get('topicIcon') or meta.get('icon') or p.get('icon') or '/images/icons/blog-pricing.svg',
                'description': p.get('topicDescription') or meta.get('description') or f'Latest guides, tips and expert answers on {cat_name}.',
            }
    return list(seen.values())


DEFAULT_POSTS = [
    {
        'slug': 'how-much-is-my-junk-car-worth',
        'title': 'How Much Is My Junk Car Worth in 2026? Parts vs. Scrap Weight Explained',
        'category': 'Scrap & Pricing',
        'categorySlug': 'pricing',
        'date': 'October 18, 2026',
        'dateIso': '2026-10-18T12:00:00',
        'readTime': '6 min read',
        'icon': '/images/icons/blog-pricing.svg',
        'iconAlt': 'Junk car valuation and instant cash offer',
        'heroImage': '/images/photos/flatbed-tow-truck-junk-car-pickup-895.png',
        'summary': 'Find out why two junk cars of the same curb weight can receive very different cash offers—and how reusable drivetrain parts, catalytic converters and local demand boost your payout.',
        'keyTakeaways': [
            'Weight-only scrapyard quotes price your car purely as crushed steel, often missing hundreds of dollars in salvageable parts value.',
            'Year, make, model, powertrain condition, completeness and your ZIP code are the biggest drivers of an instant offer.',
            'Free towing matters: a higher phone quote that deducts $125–$250 for flatbed hook-up nets you less cash at pickup.'
        ],
        'sections': [
            {
                'heading': 'Why Scrap Weight Alone Undersells Most Vehicles',
                'body': '''<p>When you call a traditional metal yard and ask what they pay for a junk car, the answer is almost always calculated by curb weight multiplied by the week's local shredded-steel rate. While a weight-only formula makes sense for a rusted shell that has already been stripped of its drivetrain and interior, most end-of-life vehicles sitting in driveways still carry valuable assemblies that repair shops, rebuilders and parts recyclers actively buy.</p>
<p>At <a href="/">US Junk Cars</a>, our Super Intelligent valuation looks beyond raw tonnage. Before generating your quote, our pricing engine checks regional demand across <a href="/locations/">all 50 states</a> for your exact year, make, model and trim—factoring in salvageable engines, transmissions, body panels, electronics and emissions components alongside current metal markets.</p>'''
            },
            {
                'heading': 'The 5 Biggest Factors That Determine Your Offer',
                'body': '''<ul>
<li><strong>Year, Make &amp; Model Demand:</strong> High-volume commuter sedans, pickup trucks, SUVs and work vans share parts with millions of vehicles still on the road, raising their component value even when the car itself no longer runs.</li>
<li><strong>Mechanical &amp; Structural Condition:</strong> A vehicle with a blown head gasket or failed transmission may still have intact doors, fenders, glass, airbags and electronics. Conversely, a collision-damaged vehicle with a strong engine and transmission is prized by mechanical rebuilders.</li>
<li><strong>Vehicle Completeness:</strong> Having the original engine, transmission, wheels, battery and catalytic converter intact keeps your offer in the highest tier.</li>
<li><strong>Title &amp; Ownership Status:</strong> A clean or salvage title in your name streamlines processing, though we also help sellers with alternative proof of ownership in eligible states (see our <a href="/faq/">Junk Car FAQ</a>).</li>
<li><strong>Local Market &amp; Distance:</strong> Proximity to licensed auto recyclers, export hubs and steel mills influences regional payouts—and because our pickup is always 100% free, distance never subtracts from the number you see.</li>
</ul>'''
            },
            {
                'heading': 'Comparing Net Payouts: Weight Quote vs. Instant Offer',
                'body': '''<p>Always compare buyers by the <strong>net cash left in your hand</strong> after the truck pulls away. A local yard that quotes $450 over the phone but charges $150 for flatbed towing and $40 for gate paperwork leaves you with $260. When you request an instant offer from <a href="/about/">US Junk Cars</a>, towing is built in at zero cost to you—so the price you accept online or at <a href="tel:+18445120697">1-844-512-0697</a> is the exact amount paid at pickup.</p>'''
            }
        ]
    },
    {
        'slug': 'scrap-metal-prices-vs-whole-car-offers',
        'title': 'Why Pickup Trucks, SUVs & Work Vans Command Higher Junk Car Offers',
        'category': 'Scrap & Pricing',
        'categorySlug': 'pricing',
        'date': 'October 17, 2026',
        'dateIso': '2026-10-17T15:00:00',
        'readTime': '5 min read',
        'icon': '/images/icons/blog-truck-value.svg',
        'iconAlt': 'Pickup truck and SUV junk car cash offer',
        'heroImage': '/images/photos/tow-truck-cash-for-junk-cars-870.png',
        'summary': 'Heavy-duty frames, high-demand transfer cases, beds, tailgates and commercial drivetrain parts make trucks, SUVs and cargo vans some of the highest-paying junk vehicles.',
        'keyTakeaways': [
            'Full-size pickup trucks and SUVs weigh 1,500–2,500 lbs more than compact sedans, giving them a higher baseline metal value.',
            'Truck beds, tailgates, differentials, 4x4 transfer cases and diesel powertrains are in constant demand from repair shops.',
            'Even high-mileage fleet vans and rusted work trucks qualify for instant offers with free heavy-duty towing.'
        ],
        'sections': [
            {
                'heading': 'More Curb Weight Plus Higher Component Demand',
                'body': '''<p>Full-size pickups, body-on-frame SUVs and cargo vans stay on the road longer than almost any other vehicle segment. Because contractors, fleets and everyday drivers keep repairing these vehicles past 200,000 miles, licensed dismantlers pay a premium for intact truck transmissions, rear axles, doors, hoods and electronics.</p>'''
            },
            {
                'heading': 'How to Get the Best Quote for a Truck or Van',
                'body': '''<p>When entering your vehicle details on <a href="/">US Junk Cars</a>, specify whether your truck is 4x4 or 2WD, note the cab and bed length, and mention if the engine starts. Our dispatch network includes flatbed tow trucks equipped for heavy pickups, commercial vans and motorhomes at no extra charge.</p>'''
            }
        ]
    },
    {
        'slug': 'sell-junk-car-without-a-title',
        'title': 'How to Sell a Junk Car Without a Title: State Rules & Ownership Options',
        'category': 'Titles & Paperwork',
        'categorySlug': 'titles',
        'date': 'October 18, 2026',
        'dateIso': '2026-10-18T11:00:00',
        'readTime': '7 min read',
        'icon': '/images/icons/blog-title-doc.svg',
        'iconAlt': 'Selling a junk car without a title guide',
        'heroImage': '/images/photos/flatbed-tow-truck-junk-car-pickup-895.png',
        'summary': 'Lost or misplaced your vehicle title? Learn when state DMV rules allow selling an older or non-running car with registration and photo ID, and when a fast duplicate title increases your payout.',
        'keyTakeaways': [
            'A certificate of title is always the fastest way to sell, and often unlocks a higher offer because rebuilders can transfer ownership immediately.',
            'Many states allow licensed recyclers to purchase older vehicles using a valid registration and matching government photo ID when the title is lost.',
            'Cars with active bank liens cannot be sold for scrap until the loan is satisfied and the lender issues a lien release.'
        ],
        'sections': [
            {
                'heading': 'Why Buyers Ask About Your Title First',
                'body': '''<p>Every legitimate junk car buyer is required by state law and federal anti-theft reporting (NMVTIS) to verify that the person selling a vehicle is its rightful owner. Having a clear, signed title in your name makes that verification instant—and allows the vehicle to be resold or rebuilt rather than restricted strictly to dismantling.</p>'''
            },
            {
                'heading': 'Three Paths When Your Title Is Missing',
                'body': '''<ul>
<li><strong>Option 1: Sell Using Registration &amp; Photo ID (Where Permitted):</strong> In many states, if the vehicle meets certain age thresholds and has no active lien, licensed auto dismantlers can accept a registration certificate paired with your driver's license and a state bill of sale.</li>
<li><strong>Option 2: Order an Expedited Duplicate Title:</strong> Most state DMVs offer online duplicate title applications for $15–$50. If your car is a newer model with high parts value, getting a duplicate title can increase your cash offer by far more than the DMV fee.</li>
<li><strong>Option 3: Resolve an Old Paid-Off Lien:</strong> If your loan was paid off years ago but the lender still appears on your paperwork, request a lien release letter from the lender before scheduling pickup.</li>
</ul>'''
            },
            {
                'heading': 'How We Verify Your Paperwork Before Dispatch',
                'body': '''<p>When you start your quote online or <a href="/contact/">contact our 24/7 support team</a>, select your current title status honestly. We check the exact rules for your state and confirm what documents the tow driver will need before a truck is dispatched, all backed by our transparent <a href="/terms-and-conditions/">Terms and Conditions</a>.</p>'''
            }
        ]
    },
    {
        'slug': 'clean-vs-salvage-vs-rebuilt-title-value',
        'title': 'Clean Title vs. Salvage Title vs. Non-Repairable Certificate: What It Means When Selling',
        'category': 'Titles & Paperwork',
        'categorySlug': 'titles',
        'date': 'October 16, 2026',
        'dateIso': '2026-10-16T14:00:00',
        'readTime': '5 min read',
        'icon': '/images/icons/blog-title-compare.svg',
        'iconAlt': 'Salvage title vs clean title guide',
        'heroImage': '/images/photos/junk-car-removal-free-towing-841.jpg',
        'summary': 'Retaining your car after an insurance total-loss settlement? Understand how salvage brands, rebuilt titles and parts-only certificates work when you are ready to sell for cash.',
        'keyTakeaways': [
            'We buy vehicles with clean titles, salvage titles, rebuilt titles and flood or hail brands in all 50 states.',
            'Signing the exact Seller line that matches the name printed on the front of the title prevents DMV rejection.',
            'If two owners are listed with "AND" between their names, both owners must sign the title.'
        ],
        'sections': [
            {
                'heading': 'How Title Brands Affect Vehicle Buyers',
                'body': '''<p>Private buyers and traditional dealerships rarely touch vehicles with a salvage or total-loss brand because lenders and standard insurers restrict them. Licensed auto buyers and dismantlers, however, purchase salvage-titled cars every day for parts harvesting, export and metal recovery.</p>'''
            },
            {
                'heading': 'How to Sign Your Title Without Voiding It',
                'body': '''<p>Never cross out mistakes or use correction fluid on a vehicle title—DMVs treat altered titles as void and require a duplicate. Sign your name on the <strong>Seller</strong> line exactly as it is printed on the face of the certificate, and check our <a href="/faq/">FAQ</a> if your title lists multiple owners or an estate.</p>'''
            }
        ]
    },
    {
        'slug': 'blown-engine-or-bad-transmission-repair-vs-sell',
        'title': 'Blown Engine or Bad Transmission? How to Decide Between Fixing and Selling',
        'category': 'Damaged & Non-Running',
        'categorySlug': 'damaged',
        'date': 'October 18, 2026',
        'dateIso': '2026-10-18T10:30:00',
        'readTime': '5 min read',
        'icon': '/images/icons/blog-engine-repair.svg',
        'iconAlt': 'Blown engine or bad transmission vehicle guide',
        'heroImage': '/images/photos/tow-truck-cash-for-junk-cars-870.png',
        'summary': 'Facing a $4,500 engine or transmission replacement quote on an older vehicle? Use the 50% repair-to-value rule to decide whether to fix it or take an instant cash offer.',
        'keyTakeaways': [
            'If a major mechanical repair exceeds 50% of the vehicle\'s running private-party value, sinking money into the repair rarely pays back.',
            'Non-running cars with seized engines or failed transmissions still command strong cash offers for their intact body panels, electronics and catalytic metals.',
            'Our flatbed and wheel-lift tow trucks pick up non-starting vehicles from driveways, apartment lots and repair shops at no charge.'
        ],
        'sections': [
            {
                'heading': 'The Hidden Cost of Major Powertrain Repairs on Older Cars',
                'body': '''<p>When an older sedan, SUV or pickup suffers a timing chain failure, blown head gasket, thrown rod or slipping automatic transmission, the initial shop estimate is rarely the final bill. Once a mechanic opens a high-mileage engine bay, worn motor mounts, brittle cooling hoses, rusted exhaust flanges and aging sensors frequently add hundreds of dollars to the invoice.</p>'''
            },
            {
                'heading': 'Applying the 50% Repair-to-Value Rule',
                'body': '''<p>Automotive financial advisors widely use a simple benchmark: if a single repair costs more than <strong>50% of what the car would be worth after the repair</strong>, it makes financial sense to sell the vehicle as-is and put the proceeds toward your next car. With your permission, <a href="/">US Junk Cars</a> can pick up your non-running vehicle directly from the mechanic's lot anywhere in <a href="/locations/">our nationwide service network</a>.</p>'''
            }
        ]
    },
    {
        'slug': 'selling-wrecked-flooded-or-hail-damaged-car',
        'title': 'How to Sell a Wrecked, Totaled or Storm-Damaged Car for Cash',
        'category': 'Damaged & Non-Running',
        'categorySlug': 'damaged',
        'date': 'October 16, 2026',
        'dateIso': '2026-10-16T11:00:00',
        'readTime': '5 min read',
        'icon': '/images/icons/blog-wrecked-car.svg',
        'iconAlt': 'Selling a wrecked or storm-damaged car for cash',
        'heroImage': '/images/photos/flatbed-tow-truck-junk-car-pickup-895.png',
        'summary': 'Uninsured collision, deployed airbags, bent frame or flood damage? Learn how to turn a wrecked or weather-damaged car into immediate cash without paying towing or storage fees.',
        'keyTakeaways': [
            'If your car is sitting at a tow yard or body shop accruing daily storage fees, getting an immediate offer stops the clock.',
            'Even after a front-end or rear-end collision, surviving drivetrain assemblies and opposite-end body panels retain strong value.',
            'Flatbed winches safely load cars with locked wheels, broken axles, flat tires or deployed airbags.'
        ],
        'sections': [
            {
                'heading': 'Why Acting Quickly Matters After an Accident',
                'body': '''<p>When a vehicle is damaged in a collision without collision coverage—or when you choose an owner-retained settlement from your insurer—leaving the vehicle in a storage lot can cost $40 to $95 per day. Requesting an instant offer lets you clear the vehicle quickly and convert its remaining components into cash.</p>'''
            },
            {
                'heading': 'Honest Damage Descriptions Lock In Your Price',
                'body': '''<p>When describing a collision- or storm-damaged vehicle, note which panels are impacted, whether the airbags deployed, and whether the engine still turns over. Accurate descriptions ensure the offer you see online is the exact payout handed to you at pickup.</p>'''
            }
        ]
    },
    {
        'slug': 'junk-car-pickup-checklist-before-tow-truck-arrives',
        'title': 'What to Do Before the Tow Truck Arrives: 7-Step Junk Car Pickup Checklist',
        'category': 'Pickup & Scams',
        'categorySlug': 'pickup',
        'date': 'October 18, 2026',
        'dateIso': '2026-10-18T09:30:00',
        'readTime': '5 min read',
        'icon': '/images/icons/blog-pickup-checklist.svg',
        'iconAlt': 'Junk car pickup day checklist',
        'heroImage': '/images/photos/junk-car-removal-free-towing-841.jpg',
        'summary': 'Make pickup day take less than 15 minutes. Follow this 7-step checklist to clear personal items, pull license plates, sign your title in the right spot and wrap up your DMV release.',
        'keyTakeaways': [
            'Check glove boxes, center consoles, door pockets, visors, trunk wells and the CD player before the driver arrives.',
            'Do not sign your title until you verify the exact Seller signature line—signing in the Buyer slot can void the document at the DMV.',
            'Remove both license plates and cancel your auto insurance and toll transponder as soon as pickup is complete.'
        ],
        'sections': [
            {
                'heading': '15 Minutes of Preparation Saves Hours Later',
                'body': '''<p>Once you accept your instant offer and select a pickup window, the actual handoff with our licensed tow operator usually takes just 10 to 15 minutes. Preparing your vehicle and paperwork ahead of time ensures a smooth inspection and immediate on-the-spot payment.</p>'''
            },
            {
                'heading': 'The 7-Step Seller Checklist',
                'body': '''<ul>
<li><strong>1. Sweep Every Compartment for Personal Items:</strong> Check under the seats, inside the glove box, center console, sun visors, trunk spare-tire well and door pockets for sunglasses, garage openers, toll tags, registration cards and house keys.</li>
<li><strong>2. Have Your Title &amp; Photo ID Ready:</strong> Keep your government-issued ID and title together.</li>
<li><strong>3. Gather All Keys &amp; Fobs:</strong> Handing over the ignition key and spare fob helps the driver load the vehicle smoothly.</li>
<li><strong>4. Remove Your License Plates:</strong> Pull the front and rear plates before the car is winched onto the truck.</li>
<li><strong>5. Ensure Clear Tow Truck Access:</strong> Move any other vehicles blocking the driveway.</li>
<li><strong>6. Collect Your On-the-Spot Payment &amp; Receipt:</strong> Receive your agreed payment right when the driver collects the car.</li>
<li><strong>7. File Your State DMV Notice of Sale &amp; Cancel Insurance:</strong> Notify your DMV that the vehicle has been sold and cancel coverage. See our <a href="/contact/">Contact &amp; Seller Guide</a> for more details.</li>
</ul>'''
            }
        ]
    },
    {
        'slug': 'how-to-avoid-junk-car-bait-and-switch-scams',
        'title': 'How Junk Car Scams Work (and 5 Red Flags Every Seller Should Watch For)',
        'category': 'Pickup & Scams',
        'categorySlug': 'pickup',
        'date': 'October 17, 2026',
        'dateIso': '2026-10-17T10:00:00',
        'readTime': '5 min read',
        'icon': '/images/icons/blog-scam-shield.svg',
        'iconAlt': 'Avoid junk car scams and hidden towing fees',
        'heroImage': '/images/photos/tow-truck-cash-for-junk-cars-870.png',
        'summary': 'Watch out for inflated phone quotes, surprise hook-up deductions and delayed payment promises. Here is how to spot predatory buyers and protect your payout.',
        'keyTakeaways': [
            'The #1 junk car scam is quoting an inflated price on the phone, then inventing "winch fees" or reducing the offer by 40% once the tow truck blocks your driveway.',
            'Never hand over a signed title or allow a vehicle to be towed away on a promise that a check will be mailed later.',
            'With US Junk Cars, your offer is shown in writing before you schedule and towing is always $0.'
        ],
        'sections': [
            {
                'heading': 'The Driveway Bait-and-Switch Explained',
                'body': '''<p>Unlicensed curbstoners and rogue towing operators frequently use a high-pressure tactic known as the driveway bait-and-switch. Over the phone, they promise $100 to $200 more than market value without asking detailed questions about your car. When the driver arrives, they claim the car weighs less than expected or charge surprise hook-up and dolly fees.</p>'''
            },
            {
                'heading': '5 Red Flags to Avoid When Selling Your Car',
                'body': '''<ul>
<li><strong>Vague Phone Estimates Without Written Confirmation:</strong> Always insist on a specific dollar figure tied to your vehicle's details before you commit.</li>
<li><strong>Hidden Towing, Fuel or Hook-Up Fees:</strong> Confirm upfront that pickup is 100% free and nothing is deducted from your payout.</li>
<li><strong>"We Will Mail Your Check Next Week":</strong> Legitimate buyers pay you on the spot when you sign over the vehicle.</li>
<li><strong>Asking You to Leave the Buyer Name Blank on the Title:</strong> Leaving an "open title" can leave you liable for future tickets or abandonment fines.</li>
<li><strong>No Privacy or Data Transparency:</strong> Deal only with companies that publish clear <a href="/privacy-policy/">Privacy Policies</a> and <a href="/terms-and-conditions/">Terms and Conditions</a>.</li>
</ul>'''
            }
        ]
    },
    {
        'slug': 'what-happens-to-your-junk-car-after-pickup-recycling',
        'title': 'What Happens to Your Junk Car After Pickup? Inside Modern Auto Recycling',
        'category': 'Auto Recycling',
        'categorySlug': 'recycling',
        'date': 'October 18, 2026',
        'dateIso': '2026-10-18T08:00:00',
        'readTime': '5 min read',
        'icon': '/images/icons/blog-eco-recycling.svg',
        'iconAlt': 'Responsible auto recycling and parts recovery',
        'heroImage': '/images/photos/flatbed-tow-truck-junk-car-pickup-895.png',
        'summary': 'Automobiles are the most recycled consumer product in America. Follow your vehicle from safe fluid depollution and parts harvesting to circular steel and aluminum recovery.',
        'keyTakeaways': [
            'More than 80% of an end-of-life vehicle by weight is recycled or reused through licensed auto dismantling and metal processing.',
            'Environmental depollution safely drains motor oil, coolant, brake fluid, fuel and A/C refrigerants so nothing leaks into local soil or groundwater.',
            'Harvesting working OEM parts helps other drivers keep their vehicles on the road at a fraction of new-part manufacturing cost.'
        ],
        'sections': [
            {
                'heading': 'Stage 1: Environmental Depollution & Hazard Removal',
                'body': '''<p>When an old vehicle sits unused on a street or lawn, rubber gaskets dry out and hazardous fluids slowly seep into storm drains and soil. Once a vehicle is picked up through <a href="/about/">US Junk Cars</a> and delivered to a licensed recycling partner, technicians safely drain engine oil, transmission fluid, antifreeze and fuel, capture refrigerants, and remove the battery for proper processing.</p>'''
            },
            {
                'heading': 'Stage 2: Reusable OEM Parts & Circular Metal Recovery',
                'body': '''<p>Before a vehicle shell reaches a shredder, dismantlers catalog working engines, transmissions, alternators, starters, mirrors and electronics. Precious metals inside the catalytic converter are refined, and high-strength steel and aluminum are melted into new raw stock.</p>'''
            }
        ]
    },
    {
        'slug': 'environmental-benefits-of-junking-an-old-car',
        'title': 'Why Letting an Unused Car Sit in Your Driveway Costs More Than You Think',
        'category': 'Auto Recycling',
        'categorySlug': 'recycling',
        'date': 'October 15, 2026',
        'dateIso': '2026-10-15T16:00:00',
        'readTime': '4 min read',
        'icon': '/images/icons/blog-driveway-cost.svg',
        'iconAlt': 'Environmental and financial cost of keeping an unused car',
        'heroImage': '/images/photos/junk-car-removal-free-towing-841.jpg',
        'summary': 'Between ongoing insurance premiums, municipal code fines, deteriorating tires, rodent damage and fluid leaks, a parked car loses value every month it sits.',
        'keyTakeaways': [
            'Many cities and HOAs issue citations for unregistered or inoperable vehicles parked in driveways or on public streets.',
            'Rubber seals, tires, batteries and fuel systems degrade rapidly when a vehicle sits unstarted for 90+ days.',
            'Recycling an idle vehicle clears your driveway immediately and puts cash in your pocket before parts corrode.'
        ],
        'sections': [
            {
                'heading': 'Depreciation and Municipal Code Fines Add Up Fast',
                'body': '''<p>A non-running car rarely gets cheaper to fix by waiting. Moisture corrodes brake rotors and electrical connectors, stale gasoline gums up fuel injectors, and municipal code enforcement officers or homeowners associations frequently fine property owners for storing inoperable vehicles with expired tags.</p>'''
            },
            {
                'heading': 'Turn Driveway Clutter Into Cash in 24–48 Hours',
                'body': '''<p>Instead of paying for tarps, storage or liability insurance on a car you no longer drive, get an instant offer on our <a href="/">homepage</a> and let our local crew haul it away for free.</p>'''
            }
        ]
    },
    {
        'slug': 'what-to-do-with-license-plates-and-insurance-after-selling',
        'title': 'After the Tow Truck Leaves: License Plates, DMV Notice of Sale & Insurance Guide',
        'category': 'State & Seller Guides',
        'categorySlug': 'guides',
        'date': 'October 18, 2026',
        'dateIso': '2026-10-18T07:30:00',
        'readTime': '5 min read',
        'icon': '/images/icons/blog-license-plate.svg',
        'iconAlt': 'Post-sale license plate and DMV release of liability guide',
        'heroImage': '/images/photos/flatbed-tow-truck-junk-car-pickup-895.png',
        'summary': 'Protect yourself from future parking tickets, toll charges and registration renewals by completing these three quick steps right after your junk car is picked up.',
        'keyTakeaways': [
            'In almost every state, license plates belong to the seller—remove them before the tow truck leaves your driveway.',
            'File a Notice of Transfer and Release of Liability (online in most states) within 5 to 30 days of the sale.',
            'Cancel your auto insurance policy and remove the vehicle from your highway toll transponder account the same day.'
        ],
        'sections': [
            {
                'heading': 'Step 1: Remove and Surrender or Transfer Your Plates',
                'body': '''<p>Before our driver loads your vehicle onto the flatbed, remove both the front and rear license plates. Depending on your state's motor vehicle rules, you will either transfer those plates to another vehicle, surrender them to the DMV to cancel your registration (and claim any prorated registration refund), or destroy them.</p>'''
            },
            {
                'heading': 'Step 2: File Your State DMV Release of Liability',
                'body': '''<p>Filing a Notice of Sale or Release of Liability lets your state DMV know that you no longer own the vehicle as of the pickup date and time. In states like California, Texas, Florida, New York, Illinois and Washington, you can submit this form online in under five minutes.</p>'''
            }
        ]
    },
    {
        'slug': 'selling-a-junk-car-from-an-apartment-garage-or-mechanic-shop',
        'title': 'How Free Junk Car Pickup Works at Apartments, Street Parking & Repair Shops',
        'category': 'State & Seller Guides',
        'categorySlug': 'guides',
        'date': 'October 15, 2026',
        'dateIso': '2026-10-15T12:00:00',
        'readTime': '4 min read',
        'icon': '/images/icons/blog-location-pickup.svg',
        'iconAlt': 'Junk car pickup from apartment, street or mechanic shop',
        'heroImage': '/images/photos/tow-truck-cash-for-junk-cars-870.png',
        'summary': 'Your car does not have to be parked in a single-family driveway to qualify for free pickup. Here is how we coordinate towing from gated complexes, city streets and repair shops.',
        'keyTakeaways': [
            'We pick up vehicles from home driveways, apartment parking lots, workplace garages, city streets and mechanic shops across all 50 states.',
            'If your car is at a repair shop, simply let the service desk know our driver is coming and meet the driver there with your ID and title.',
            'Wheel-lift tow trucks can extract vehicles from tight parking spaces or low-clearance areas where a full flatbed cannot fit.'
        ],
        'sections': [
            {
                'heading': 'Coordinating Pickup Outside a Standard Driveway',
                'body': '''<p>When you schedule your free pickup across <a href="/locations/">our 50-state network</a>, you can add gate codes, parking stall numbers or repair shop contact details right in your booking notes. Our local dispatch team selects the right truck—flatbed or nimble wheel-lift—for your parking layout and calls ahead before arrival.</p>'''
            }
        ]
    },
]


def load_posts() -> list[dict]:
    POSTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not POSTS_FILE.exists():
        POSTS_FILE.write_text(json.dumps(DEFAULT_POSTS, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        return DEFAULT_POSTS
    posts = json.loads(POSTS_FILE.read_text(encoding='utf-8'))
    existing_slugs = {p['slug'] for p in posts}
    changed = False
    for dp in DEFAULT_POSTS:
        if dp['slug'] not in existing_slugs:
            posts.append(dp)
            changed = True
        else:
            for p in posts:
                if p['slug'] == dp['slug']:
                    if p.get('icon') != dp['icon'] or 'heroImage' not in p:
                        p['icon'] = dp['icon']
                        p['heroImage'] = dp['heroImage']
                        p['dateIso'] = dp['dateIso']
                        changed = True
    if changed:
        POSTS_FILE.write_text(json.dumps(posts, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return posts


def sort_latest_first(posts: list[dict]) -> list[dict]:
    return sorted(posts, key=lambda p: p.get('dateIso', ''), reverse=True)


def render_card(p: dict, is_latest_in_topic: bool = False) -> str:
    slug = p['slug']
    url = f'/blog/{slug}/'
    cat = p['category']
    cat_slug = p['categorySlug']
    title = p['title']
    date = p['date']
    date_iso = p['dateIso'][:10]
    read_time = p['readTime']
    summary = p['summary']
    icon = p['icon']
    icon_alt = p['iconAlt']
    latest_pill = '<span class="blog-latest-chip">Latest</span>' if is_latest_in_topic else ''
    refs_count = len(p.get('references', []))
    takeaways_count = len(p.get('keyTakeaways', []))
    keywords_str = ' '.join(p.get('targetKeywords', []))
    first_takeaway = p.get('keyTakeaways', [''])[0]
    quick_takeaway_html = (
        f'<div class="blog-card__quick"><span class="blog-card__quick-label">Key Takeaway:</span> {first_takeaway}</div>'
        if first_takeaway
        else ''
    )
    refs_note = (
        f'<span class="blog-card__refs-pill">{takeaways_count} Key Takeaways &bull; {refs_count} Official Refs</span>'
        if refs_count
        else ''
    )

    return f'''<article class="blog-card" data-blog-card="" data-category="{cat_slug}" data-keywords="{keywords_str}">
<div class="blog-card__top">
<div class="blog-card__icon"><img alt="{icon_alt}" decoding="async" height="44" loading="lazy" src="{icon}" width="44"/></div>
<div class="blog-card__badges">
<span class="blog-badge blog-badge--{cat_slug}">{cat}</span>
<span class="blog-meta-pill">{read_time}</span>
</div>
</div>
<h3 class="blog-card__title"><a href="{url}">{title}</a></h3>
<p class="blog-card__excerpt">{summary}</p>
{quick_takeaway_html}
{refs_note}
<div class="blog-card__footer">
<div class="blog-card__date-wrap">{latest_pill}<time class="blog-card__date" datetime="{date_iso}">{date}</time></div>
<a class="blog-card__read" href="{url}">Read Full Guide <span aria-hidden="true">&rarr;</span></a>
</div>
</article>'''


def build_html(posts: list[dict]) -> str:
    sorted_all = sort_latest_first(posts)
    latest_post = sorted_all[0]
    latest_url = f'/blog/{latest_post["slug"]}/'
    latest_takeaways = ''.join(f'<li>{t}</li>' for t in latest_post.get('keyTakeaways', [])[:4])
    latest_ai_overview = latest_post.get('aiOverview', '')
    ai_overview_html = (
        f'<div class="blog-featured__ai-box"><span class="blog-featured__ai-badge">Quick Answer &bull; AI Overview</span><p>{latest_ai_overview}</p></div>'
        if latest_ai_overview
        else ''
    )
    topics = discover_topics(sorted_all)

    filter_buttons = [
        f'<button type="button" class="blog-filter-btn is-active" data-blog-filter="all" aria-pressed="true">All Topics ({len(posts)})</button>'
    ]
    for topic in topics:
        t_count = sum(1 for p in posts if p['categorySlug'] == topic['slug'])
        filter_buttons.append(
            f'<button type="button" class="blog-filter-btn" data-blog-filter="{topic["slug"]}" aria-pressed="false">'
            f'{topic["name"]} ({t_count})</button>'
        )

    topic_sections_html = []
    for idx, topic in enumerate(topics, 1):
        t_slug = topic['slug']
        t_posts = sort_latest_first([p for p in posts if p['categorySlug'] == t_slug])
        cards = ''.join(render_card(p, is_latest_in_topic=(i == 0)) for i, p in enumerate(t_posts))
        tint_class = ' page-section--tint' if idx % 2 == 1 else ''
        topic_sections_html.append(f'''<section class="page-section{tint_class} blog-topic-section" id="topic-{t_slug}" data-blog-topic-section="{t_slug}"><div class="container">
<div class="blog-topic-header">
<div class="blog-topic-header__left">
<div class="blog-topic-header__icon"><img alt="{topic["name"]}" decoding="async" height="42" loading="lazy" src="{topic["icon"]}" width="42"/></div>
<div>
<div class="blog-topic-header__eyebrow">
<span class="blog-badge blog-badge--{t_slug}">{topic["name"]}</span>
<span class="blog-topic-sort-note">Sorted by Latest Post First &bull; {len(t_posts)} {"Guide" if len(t_posts) == 1 else "Guides"}</span>
</div>
<h2 class="section-title blog-topic-header__title">{topic["name"]}</h2>
<p class="blog-topic-header__desc">{topic["description"]}</p>
</div>
</div>
</div>
<div class="blog-grid">
{cards}
</div>
</div></section>''')

    return f'''<div class="breadcrumbs"><div class="container"><ul class="breadcrumbs-list"><li class="breadcrumbs-list__item"><a class="breadcrumbs-list__item-link" href="/">Home</a></li><li class="breadcrumbs-list__item" aria-current="page">Blog</li></ul></div></div>
<section class="page-title blog-hero-section"><div class="container">
<div class="blog-hero-top">
<span class="page-card__badge">US Junk Cars Editorial &amp; Seller Resource Hub</span>
<h1 class="section-title">Junk Car Selling Blog: Latest Guides by Topic</h1>
<p class="page-title__lead">Explore deeply researched seller guides across every topic—complete with <a href="/faq/">2026 scrap vs. parts valuation tables, official state DMV forms</a>, <a href="/locations/">50-state pickup logistics</a> and <a href="/about/">EPA auto recycling rules</a>. Every new article is automatically featured below and filed at the top of its topic section.</p>
</div>

<div class="blog-featured">
<div class="blog-featured__content">
<div class="blog-featured__top">
<div class="blog-featured__meta">
<span class="blog-badge blog-badge--featured">Latest &amp; Featured Post</span>
<span class="blog-badge blog-badge--{latest_post["categorySlug"]}">{latest_post["category"]}</span>
<time datetime="{latest_post["dateIso"][:10]}">{latest_post["date"]}</time>
<span>&bull; {latest_post["readTime"]}</span>
</div>
<h2 class="blog-featured__title"><a href="{latest_url}">{latest_post["title"]}</a></h2>
{ai_overview_html}
<div class="blog-featured__takeaways-box">
<p class="blog-featured__takeaways-label">Key Takeaways &amp; Seller Highlights</p>
<ul class="checklist blog-featured__list">{latest_takeaways}</ul>
</div>
</div>
<div class="blog-featured__actions">
<a class="button button--default blog-featured__btn" href="{latest_url}"><span class="button__inner">Read Latest Guide <svg class="icon icon--arrow-left" height="18" width="10"><use xlink:href="#icon-arrow-left"></use></svg></span></a>
<a class="button button--red blog-featured__btn" data-peddle-offer="" href="{TEL}"><span class="button__inner">Get My Instant Offer</span></a>
</div>
</div>
<div class="blog-featured__media">
<div class="blog-featured__media-header">
<span class="blog-featured__media-Tag">Super Intelligent Valuation</span>
<p class="blog-featured__media-heading">Real-Time Offers for Parts + Metal</p>
<p class="blog-featured__media-sub">We price your vehicle across licensed rebuilders, parts buyers and metal recyclers nationwide.</p>
</div>
<div class="blog-featured__media-stage">
<picture>
<source media="(max-width: 575.98px)" srcset="/images/photos/flatbed-tow-truck-junk-car-pickup-600.webp, /images/photos/flatbed-tow-truck-junk-car-pickup-600@2x.webp 2x" type="image/webp"/>
<source media="(min-width: 576px)" srcset="/images/photos/flatbed-tow-truck-junk-car-pickup-895.webp, /images/photos/flatbed-tow-truck-junk-car-pickup-895@2x.webp 2x" type="image/webp"/>
<img alt="{latest_post["iconAlt"]}" class="blog-featured__img" decoding="async" height="438" loading="eager" src="{latest_post.get("heroImage", "/images/photos/flatbed-tow-truck-junk-car-pickup-895.png")}" width="895"/>
</picture>
</div>
<div class="blog-featured__stats">
<div class="blog-featured__stat"><strong>All 50 States</strong><span>Free Pickup</span></div>
<div class="blog-featured__stat"><strong>In Minutes</strong><span>Instant Quote</span></div>
<div class="blog-featured__stat"><strong>$0 Towing</strong><span>Paid on the Spot</span></div>
</div>
<div class="blog-featured__caption">
<span>Need immediate help? <a href="/contact/">Contact our 24/7 team</a> or call <a href="{TEL}">{PHONE}</a>.</span>
</div>
</div>
</div>
</div></section>

<section class="page-section blog-filter-section" id="blog-directory"><div class="container">
<div class="blog-directory-header">
<div>
<h2 class="section-title">Explore Blog Topics</h2>
<p class="section-lead">Select any topic below or search by keyword. Whenever a new topic or article is added, it automatically appears here sorted by the latest post first.</p>
</div>
<div class="blog-search-box">
<label class="sr-only" for="blog-search-input">Search blog articles</label>
<input type="search" id="blog-search-input" class="blog-search-input" placeholder="Search guides (e.g. no title, blown engine, towing)..." autocomplete="off"/>
</div>
</div>

<div class="blog-toolbar" role="toolbar" aria-label="Filter articles by topic">
<div class="blog-filters">{''.join(filter_buttons)}</div>
<p class="blog-count" id="blog-results-count" aria-live="polite">Showing all {len(posts)} guides across {len(topics)} topics</p>
</div>
<p class="blog-empty" id="blog-empty-state" hidden="">No guides matched your search. Try another keyword or click <strong>All Topics</strong> above.</p>
</div></section>

{''.join(topic_sections_html)}

<div class="hiw">
<div class="container">
<div class="hiw__cta" style="background: url(/images/backgrounds/cta-banner-blue.webp) no-repeat center / cover;">
<div class="hiw__image"><picture> <source media="(max-width: 360px)" srcset="/images/photos/flatbed-tow-truck-junk-car-pickup-600.webp, /images/photos/flatbed-tow-truck-junk-car-pickup-600@2x.webp 2x" type="image/webp"/> <source media="(max-width: 991.98px)" srcset="/images/photos/flatbed-tow-truck-junk-car-pickup-895.webp, /images/photos/flatbed-tow-truck-junk-car-pickup-895@2x.webp 2x" type="image/webp"/> <source media="(min-width: 992px)" srcset="/images/photos/flatbed-tow-truck-junk-car-pickup-1206.webp, /images/photos/flatbed-tow-truck-junk-car-pickup-1206@2x.webp 2x" type="image/webp"/> <source media="(max-width: 360px)" srcset="/images/photos/flatbed-tow-truck-junk-car-pickup-600.png, /images/photos/flatbed-tow-truck-junk-car-pickup-600@2x.png 2x" type="image/png"/> <source media="(max-width: 991.98px)" srcset="/images/photos/flatbed-tow-truck-junk-car-pickup-895.png, /images/photos/flatbed-tow-truck-junk-car-pickup-895@2x.png 2x" type="image/png"/> <source media="(min-width: 992px)" srcset="/images/photos/flatbed-tow-truck-junk-car-pickup-1206.png, /images/photos/flatbed-tow-truck-junk-car-pickup-1206@2x.png 2x" type="image/png"/><img alt="Flatbed tow truck for junk car pickup near you" decoding="async" height="438" loading="lazy" src="/images/photos/flatbed-tow-truck-junk-car-pickup-1206.png" srcset="/images/photos/flatbed-tow-truck-junk-car-pickup-1206.png, /images/photos/flatbed-tow-truck-junk-car-pickup-1206@2x.png 2x" width="1206"/> </picture></div>
<div class="cta hiw__content">
<p class="cta__title">Ready to turn your car into cash?</p>
<a class="cta__phone section-title" href="{TEL}"><svg class="icon icon--phone" height="26" width="26"> <use xlink:href="#icon-phone"></use> </svg>{PHONE}</a>
<p class="cta__text">Call us 24/7, or get your guaranteed instant offer online in minutes.</p>
<a class="cta__button button button--default button--default-white" data-peddle-offer="" href="{TEL}"><span class="button__inner">Get My Free Offer <svg class="icon icon--arrow-left" height="20" width="11"> <use xlink:href="#icon-arrow-left"></use> </svg></span></a></div>
</div>
</div>
</div>
'''


def main() -> None:
    posts = load_posts()
    topics = discover_topics(sort_latest_first(posts))
    page_html = build_html(posts)
    (ROOT / 'content/pages' / f'{ID}.html').write_text(page_html, encoding='utf-8')

    reg_path = ROOT / 'content/publication.json'
    reg = json.loads(reg_path.read_text(encoding='utf-8'))

    sorted_posts = sort_latest_first(posts)
    blog_postings_ld = [
        {
            '@type': 'BlogPosting',
            'headline': p['title'],
            'description': p['summary'],
            'datePublished': p['dateIso'][:10],
            'dateModified': p['dateIso'][:10],
            'url': f'{SITE}{PATH}{p["slug"]}/',
            'author': {'@type': 'Organization', 'name': 'US Junk Cars Editorial Team', 'url': f'{SITE}/'},
            'publisher': {'@type': 'Organization', 'name': 'US Junk Cars', 'legalName': 'USJunkCars', 'url': f'{SITE}/'},
        }
        for p in sorted_posts
    ]

    route = {
        'id': ID,
        'path': PATH,
        'family': 'blog',
        'title': 'Junk Car Selling Blog: Prices, Titles & Tips | USJunkCars',
        'description': 'Expert guides on selling a junk car for cash: scrap vs. parts pricing, selling without a title, pickup checklists, avoiding scams and auto recycling.',
        'lastModified': ISO,
        'jsonLd': [
            {
                '@context': 'https://schema.org',
                '@type': 'Blog',
                'name': 'US Junk Cars Blog & Seller Resource Center',
                'url': f'{SITE}{PATH}',
                'description': 'Practical guides on selling junk, damaged and non-running vehicles for cash with free towing across all 50 states.',
                'publisher': {
                    '@type': 'Organization',
                    'name': 'US Junk Cars',
                    'legalName': 'USJunkCars',
                    'url': f'{SITE}/',
                    'logo': f'{SITE}/images/brand/logo-stacked.svg',
                },
                'blogPost': blog_postings_ld,
            },
            {
                '@context': 'https://schema.org',
                '@type': 'BreadcrumbList',
                'itemListElement': [
                    {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': f'{SITE}/'},
                    {'@type': 'ListItem', 'position': 2, 'name': 'Blog', 'item': f'{SITE}{PATH}'},
                ],
            },
        ],
        'status': 'review',
        'environments': ['local', 'development'],
        'approval': None,
    }

    existing = next((r for r in reg['routes'] if r['id'] == ID), None)
    if existing:
        route.update(status=existing['status'], environments=existing['environments'], approval=existing['approval'])
        reg['routes'][reg['routes'].index(existing)] = route
    else:
        reg['routes'].append(route)

    reg_path.write_text(json.dumps(reg, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'wrote {PATH} ({len(posts)} posts across {len(topics)} dynamic topic sections) | registry routes: {len(reg["routes"])}')


if __name__ == '__main__':
    main()

