"""Build the static inner pages (locations, about, faq, contact) from the homepage shell.

Header, footer and assets come from index.html so every page stays in sync with the
homepage. Run after editing index.html or the page content below:  python3 scripts/build-pages.py
"""
import html, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = 'https://usjunkcars.si'
PHONE, TEL = '1-844-512-0697', 'tel:+18445120697'
NAV = {'Locations': '/locations/', 'About': '/about/', 'About Us': '/about/', 'FAQ': '/faq/',
       'Contact us': '/contact/', 'Contact': '/contact/', 'Homepage': '/', 'Who buys Junk Cars': '/locations/'}
OLD_NAV = {'Locations': 'areas', 'About': 'about_us', 'About Us': 'about_us', 'FAQ': 'faqs',
           'Contact us': 'contact-us', 'Contact': 'contact-us', 'Homepage': '', 'Who buys Junk Cars': 'areas'}


def link_nav(page):
    """Point the header/footer nav at the local pages instead of the reference site."""
    for text, slug in OLD_NAV.items():
        page = re.sub(r'<a href="https://www\.usjunkcars\.com/%s/?" rel="noopener" target="_blank" '
                      r'title="Opens the original USJunkCars website">\s*%s\s*</a>' % (re.escape(slug), re.escape(text)),
                      f'<a href="{NAV[text]}">{text}</a>', page)
    return page


def state_name(slug):
    return ' '.join(w.capitalize() for w in slug.split('-')).replace('Of ', 'of ')


def local_states(page):
    """Map and state-list links open the instant offer (phone fallback) instead of the reference site."""
    page = re.sub(r'<a class="region-link" href="https://www\.usjunkcars\.com/([a-z-]+)" rel="noopener" target="_blank" '
                  r'title="Opens the original USJunkCars website">',
                  lambda m: f'<a class="region-link" data-peddle-offer="" data-state="{state_name(m.group(1))}" '
                            f'href="{TEL}" aria-label="Cash for junk cars in {state_name(m.group(1))}">', page)
    page = re.sub(r'<a class="location-cities__list-link" href="https://www\.usjunkcars\.com/([a-z-]+)" rel="noopener" '
                  r'target="_blank" title="Opens the original USJunkCars website">',
                  lambda m: f'<a class="location-cities__list-link" data-peddle-offer="" href="{TEL}">', page)
    return page


home = local_states(link_nav((ROOT / 'index.html').read_text()))
(ROOT / 'index.html').write_text(home)

head_end = home.index('<main class="main">')
shell_top, shell_bottom = home[:head_end], home[home.index('</main>'):]
steps = re.search(r'<div class="hiw">\s*<div class="container container--small">.*?</ul>\s*</div>\s*</div>', home, re.S).group(0)
cta = re.search(r'<div class="hiw">\s*<div class="container">\s*<div class="hiw__cta".*?</div>\s*</div>\s*</div>\s*</div>', home, re.S).group(0)
map_block = re.search(r'<section class="map section">.*?</section>', home, re.S).group(0)
state_block = re.search(r'<div class="section">\s*<div class="container">\s*<div class="location-counties">.*?</ul>\s*</div>\s*</div>\s*</div>', home, re.S).group(0)
offer_btn = ('<a class="button button--default" data-peddle-offer="" href="%s"><span class="button__inner">'
             'Get My Instant Offer <svg class="icon icon--arrow-left" height="20" width="11"> '
             '<use xlink:href="#icon-arrow-left"></use> </svg></span></a>' % TEL)
call_btn = ('<a class="button button--white" href="%s"><span class="button__inner" style="color:#DE193E">'
            'Call %s</span></a>' % (TEL, PHONE))


def esc(t):
    return html.escape(t, quote=True)


def shell(slug, title, desc, crumb, ld):
    top = shell_top
    old_title = re.search(r'<title>(.*?)</title>', top).group(1)
    old_desc = re.search(r'<meta content="([^"]*)" name="description"/>', top).group(1)
    top = top.replace(f'<title>{old_title}</title>', f'<title>{esc(title)}</title>')
    top = top.replace(f'content="{old_title}"', f'content="{esc(title)}"')
    top = top.replace(f'content="{old_desc}"', f'content="{esc(desc)}"')
    url = f'{SITE}/{slug}/'
    top = top.replace(f'content="{SITE}/" property="og:url"', f'content="{url}" property="og:url"')
    top = top.replace(f'<link href="{SITE}/" rel="canonical"/>', f'<link href="{url}" rel="canonical"/>')
    top = re.sub(r'<script type="application/ld\+json">.*?</script>',
                 '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>', top, flags=re.S)
    top = top.replace('<link href="/clone.css', '<link href="/css/pages.css?v=1" rel="stylesheet"/>\n<link href="/clone.css', 1)
    crumbs = ('<div class="breadcrumbs"><div class="container"><ul class="breadcrumbs-list">'
              '<li class="breadcrumbs-list__item"><a class="breadcrumbs-list__item-link" href="/">Home</a></li>'
              f'<li class="breadcrumbs-list__item" aria-current="page">{crumb}</li></ul></div></div>\n')
    return top + '<main class="main">\n' + crumbs, shell_bottom


def breadcrumb_ld(slug, name):
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': f'{SITE}/'},
        {'@type': 'ListItem', 'position': 2, 'name': name, 'item': f'{SITE}/{slug}/'}]}


def title_block(h1, lead):
    return (f'<section class="page-title"><div class="container"><h1 class="section-title">{h1}</h1>'
            f'<p class="page-title__lead">{lead}</p><div class="page-cta-row">{offer_btn}{call_btn}</div></div></section>\n')


def faq_items(qs):
    return ''.join(f'<details class="faq-accordion__item faq-item"><summary class="faq-accordion__header font-bold color-blue">'
                   f'<span>{q}</span></summary><p class="faq-item__answer">{a}</p></details>\n' for q, a in qs)


def write(slug, title, desc, crumb, ld, body):
    top, bottom = shell(slug, title, desc, crumb, ld)
    out = ROOT / slug / 'index.html'
    out.parent.mkdir(exist_ok=True)
    out.write_text(top + body + bottom)
    print('built', out.relative_to(ROOT))


# ---------------------------------------------------------------- Locations
STATES = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware',
          'District of Columbia', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas',
          'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi',
          'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York',
          'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island',
          'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington',
          'West Virginia', 'Wisconsin', 'Wyoming']
loc_map = (map_block.replace('Nationwide service', 'Click your state for an instant offer')
           .replace('<h2 class="map__title section-title text-center">Cash for Junk Cars Near You, in Every State</h2>', ''))
loc_states = state_block.replace('Find our location near you:', 'Or choose your state from the list:')
loc_body = title_block(
    'Junk Car Removal Near Me: Service Across the USA',
    'Find cash for junk cars near you without calling around. Pick your state, enter your ZIP code in the offer form '
    'and we confirm pickup for your address, with free towing from your driveway, street, parking lot or repair shop.') + \
    loc_map + '\n' + loc_states + '\n' + '''
<section class="page-section"><div class="container"><div class="page-content">
<h2 class="section-title">How local junk car pickup works</h2>
<p>US Junk Cars works with licensed towing and recycling partners in cities, suburbs and rural areas across the country. When you request an offer, your ZIP code tells us who can reach your car fastest, so you are not paying for a tow from the other side of the state.</p>
<p>Most sellers get a pickup window within a day or two of accepting their offer. In many areas same-day or next-day junk car pickup is possible. The driver calls ahead, checks the car and paperwork, and pays you before towing it away.</p>
<h3>What the pickup crew needs from you</h3>
<ul>
<li>The car's title, or the documents your state accepts in place of a title</li>
<li>A valid photo ID that matches the name on the paperwork</li>
<li>The keys, if you still have them (a missing key is not a deal breaker)</li>
<li>Clear access to the car, even if it sits on flat tires or has no battery</li>
</ul>
</div>
<div class="page-cards">
<div class="page-card"><h3>Sell my junk car near me</h3><p>Your offer is based on your exact vehicle and location, so the price reflects local scrap and parts demand.</p></div>
<div class="page-card"><h3>Junk car pickup near me</h3><p>Pickup is free everywhere we operate, and nothing is deducted from your offer for towing.</p></div>
<div class="page-card"><h3>Cash for junk cars near me</h3><p>You get paid when the car is collected, not after an inspection days later.</p></div>
</div></div></section>
''' + cta + '\n'
write('locations', 'Junk Car Removal Near Me in All 50 States | US Junk Cars',
      'Junk car removal near you in every state. Get cash for junk cars with free pickup from your driveway, '
      'street or shop. Check your ZIP code for an instant offer.',
      'Locations',
      [{'@context': 'https://schema.org', '@type': 'Service', 'name': 'Junk car removal and cash for junk cars',
        'provider': {'@type': 'AutomotiveBusiness', 'name': 'US Junk Cars', 'url': f'{SITE}/', 'telephone': '+1-844-512-0697'},
        'areaServed': [{'@type': 'State', 'name': s} for s in STATES if s != 'District of Columbia'] +
                      [{'@type': 'AdministrativeArea', 'name': 'District of Columbia'}]},
       breadcrumb_ld('locations', 'Locations')],
      loc_body)

# ---------------------------------------------------------------- About
about_body = title_block(
    'About US Junk Cars: Junk Car Buyers Built Around the Seller',
    'We started US Junk Cars because selling an old car should not mean haggling with a scrapyard, '
    'meeting strangers from online listings or paying for a tow. Our job is to make the sale quick, fair and clear.') + f'''
<section class="page-section"><div class="container"><div class="page-content">
<h2 class="section-title">Why we do this</h2>
<p>Most junk cars sit for months because selling them is a hassle. Private buyers want running cars. Scrapyards quote one price on the phone and another at the gate. Towing companies charge before anyone has paid you a dollar.</p>
<p>US Junk Cars puts everything in one place: an offer you can see before you commit, a pickup that costs you nothing, and payment at the moment the car leaves. We buy junk cars, trucks, SUVs and vans in any condition, from clean-title daily drivers that finally gave out to wrecked, flooded or stripped vehicles.</p>
<h3>Powered by Super Intelligent pricing</h3>
<p>The .si in our name stands for Super Intelligent. Our offers come from pricing that weighs your car's year, make, model, condition and location against current scrap metal prices and used parts demand. That is how we can show you a real number in minutes instead of sending someone out to guess.</p>
<h3>What you can count on</h3>
<ul>
<li><strong>A clear offer first.</strong> You see the price before you schedule anything.</li>
<li><strong>Free towing.</strong> No pickup fee and no surprise deductions for hauling.</li>
<li><strong>Payment at pickup.</strong> You are paid when the car is collected.</li>
<li><strong>Honest answers.</strong> If your paperwork or location is a problem, we tell you up front.</li>
<li><strong>Responsible recycling.</strong> Fluids, batteries and tires are handled by licensed recyclers, and usable parts get a second life.</li>
</ul>
</div></div></section>
''' + steps + '\n' + cta + '\n'
write('about', 'About US Junk Cars | Fair Junk Car Buyers, Powered by Super Intelligent',
      'US Junk Cars buys junk cars across the USA with clear instant offers, free towing and payment at pickup. '
      'Learn how our Super Intelligent pricing works.',
      'About',
      [{'@context': 'https://schema.org', '@type': 'AboutPage', 'name': 'About US Junk Cars', 'url': f'{SITE}/about/',
        'about': {'@type': 'AutomotiveBusiness', 'name': 'US Junk Cars', 'url': f'{SITE}/', 'telephone': '+1-844-512-0697',
                  'slogan': 'Powered by Super Intelligent', 'areaServed': {'@type': 'Country', 'name': 'United States'}}},
       breadcrumb_ld('about', 'About')],
      about_body)

# ---------------------------------------------------------------- FAQ
FAQ = [
    ('Getting an offer', [
        ('How do I sell a junk car?',
         'Request an instant offer online or by phone, accept the price you see, choose a pickup time, and get paid when the tow truck collects the car. Most sellers finish the whole process in a day or two.'),
        ('How much will you pay for my junk car?',
         'Every offer is calculated for your vehicle. The year, make, model, condition, location and current scrap and parts prices all matter. A newer car with sellable parts usually earns more than its scrap weight alone.'),
        ('How much do junkyards pay for cars?',
         'Scrapyards mostly pay by weight, so the price follows scrap steel markets and changes week to week. Because our offers also count the value of reusable parts, they can beat a weight-only quote, and towing is included.'),
        ('Is the offer guaranteed?',
         'Your offer holds as long as the car matches what you described. If the driver finds something major that was not mentioned, such as a missing engine, the price may be adjusted before pickup. You can always decline.'),
    ]),
    ('Title and paperwork', [
        ('Can I sell a car without a title?',
         'Often, yes. Rules depend on your state and the age of the vehicle. Many states accept a current registration plus a photo ID, and older vehicles may need less. Tell us what paperwork you have and we will confirm before pickup.'),
        ('Do I need a title to junk my car?',
         'A title makes it fastest, but it is not always required. If your title is lost, you can usually request a duplicate from your state DMV, or we can check whether your registration is enough.'),
        ('What do I need to junk my car?',
         'Have the title (or accepted alternative), a valid photo ID, and the keys if you have them. Remove your personal items and license plates before the driver arrives.'),
        ('Can I sell a car that is still financed?',
         'If there is an active loan, the lender holds the title, so the loan must be paid off before the car can be sold for scrap. Contact your lender for a payoff amount first.'),
    ]),
    ('Pickup and payment', [
        ('Is towing really free?',
         'Yes. Pickup is free and nothing is subtracted from your offer for towing, whether the car runs or not.'),
        ('How fast can you pick up my car?',
         'Most pickups happen within one to two days of accepting your offer, and same-day pickup is often possible. Your available time slots appear when you schedule.'),
        ('Do I have to be there during pickup?',
         'Usually someone needs to hand over the title and keys and sign the paperwork. If you cannot be present, tell us when you schedule and we will explain the options for your state.'),
        ('How will I be paid?',
         'You are paid at pickup, when the driver collects the car. The payment method is shown when you schedule.'),
    ]),
    ('Car condition and after the sale', [
        ('Do you buy cars that do not run?',
         'Yes. We buy non-running cars, cars with blown engines or failed transmissions, and wrecked, flooded, burned or stripped vehicles.'),
        ('How do I sell a car that does not run?',
         'Describe the problem honestly in the offer form. A car that does not start can still be worth more than scrap, and our tow truck handles cars that cannot move under their own power.'),
        ('What should I do after the car is picked up?',
         'Cancel your insurance, return or transfer the license plates as your state requires, and file a notice of sale or release of liability with your DMV if your state has one.'),
    ]),
]
all_q = [qa for _, group in FAQ for qa in group]
faq_body = title_block(
    'Junk Car FAQ: Titles, Pickup, Payment and Prices',
    'Answers to the questions sellers ask most before they junk a car, from selling without a title to what happens after the tow truck leaves.') + \
    '<section class="section faq"><div class="container"><div class="faq-accordion faq-accordion--answered">' + \
    ''.join(f'<div class="faq-group"><h2 class="faq-group__title">{name}</h2>{faq_items(group)}</div>' for name, group in FAQ) + \
    '</div></div></section>\n' + cta + '\n'
write('faq', 'Junk Car FAQ: Sell Without a Title, Pickup & Payment | US Junk Cars',
      'Can you sell a car without a title? How much do junkyards pay? Get clear answers about junking a car, '
      'free pickup, payment and paperwork.',
      'FAQ',
      [{'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
          {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in all_q]},
       breadcrumb_ld('faq', 'FAQ')],
      faq_body)

# ---------------------------------------------------------------- Contact
contact_body = title_block(
    'Contact US Junk Cars',
    'Talk to a person about your car, your paperwork or a scheduled pickup, or skip the call and get your instant offer online at any hour.') + f'''
<section class="page-section"><div class="container">
<div class="page-cards">
<div class="page-card"><h3>Call us</h3><a class="page-card__big" href="{TEL}">{PHONE}</a><p>Questions about an offer, a title problem or a pickup you already booked.</p></div>
<div class="page-card"><h3>Get an instant offer</h3><p style="margin-bottom:14px">See your price online in a few minutes, day or night. No call needed.</p>{offer_btn}</div>
<div class="page-card"><h3>Service area</h3><p>We buy junk cars across the United States. <a href="/locations/">Check coverage for your state</a>.</p></div>
</div>
<div class="page-content" style="margin-top:40px">
<h2 class="section-title">Before you call</h2>
<p>Having these details ready makes your offer faster and more accurate:</p>
<ul>
<li>Year, make, model and approximate mileage</li>
<li>Whether the car starts and drives</li>
<li>Any major damage or missing parts</li>
<li>Your ZIP code and the title status (clean, salvage or missing)</li>
</ul>
<p>Looking for quick answers? Our <a href="/faq/">junk car FAQ</a> covers titles, pickup and payment.</p>
</div></div></section>
'''
write('contact', 'Contact US Junk Cars | Call 1-844-512-0697 for Cash for Junk Cars',
      'Contact US Junk Cars at 1-844-512-0697 or get an instant cash offer for your junk car online. '
      'Free towing and payment at pickup across the USA.',
      'Contact us',
      [{'@context': 'https://schema.org', '@type': 'ContactPage', 'name': 'Contact US Junk Cars', 'url': f'{SITE}/contact/',
        'mainEntity': {'@type': 'AutomotiveBusiness', 'name': 'US Junk Cars', 'url': f'{SITE}/',
                       'contactPoint': {'@type': 'ContactPoint', 'telephone': '+1-844-512-0697',
                                        'contactType': 'customer service', 'areaServed': 'US', 'availableLanguage': 'English'}}},
       breadcrumb_ld('contact', 'Contact us')],
      contact_body)

# ---------------------------------------------------------------- Privacy Policy
EFFECTIVE = 'October 15, 2026'
PRIVACY_EMAIL = 'privacy@usjunkcars.si'
P_SECTIONS = [
    ('overview', 'Who we are and what this policy covers', f'''
<p>US Junk Cars ("US Junk Cars", "we", "us") operates <a href="/">usjunkcars.si</a>, a service that helps people across the United States get cash offers for junk, damaged and unwanted vehicles and arrange free pickup. This Privacy Policy explains what personal information we collect, how we use and share it, and the choices and rights you have.</p>
<p>It applies to our website, phone calls, text messages and emails, and the instant offer form on our site. It does not apply to websites or services run by others, even if we link to them.</p>'''),
    ('collect', 'Information we collect', '''
<p>We collect only what we need to give you an offer, complete the pickup and run our service.</p>
<table class="legal-table"><thead><tr><th>Category</th><th>Examples</th><th>Where it comes from</th></tr></thead><tbody>
<tr><td>Contact details</td><td>Name, phone number, email address</td><td>You, when you request an offer or call us</td></tr>
<tr><td>Vehicle details</td><td>Year, make, model, trim, mileage, condition, VIN, photos you share</td><td>You, and vehicle data services used to confirm the details</td></tr>
<tr><td>Location</td><td>ZIP code and pickup address</td><td>You</td></tr>
<tr><td>Ownership and identity</td><td>Title status, the name on the title, a photo ID shown at pickup</td><td>You and the pickup driver</td></tr>
<tr><td>Payment details</td><td>The name and details needed to pay you</td><td>You, at or before pickup</td></tr>
<tr><td>Communications</td><td>Call recordings where permitted and disclosed, messages and emails</td><td>You and us</td></tr>
<tr><td>Device and usage data</td><td>IP address, browser type, pages visited, referring site, approximate location</td><td>Your browser, through cookies and similar technologies</td></tr>
</tbody></table>
<p>We do not knowingly collect sensitive personal information such as Social Security numbers, and we do not ask for it to make an offer.</p>'''),
    ('use', 'How we use your information', '''
<ul>
<li>To calculate and present your instant cash offer, and to confirm that it matches your vehicle.</li>
<li>To schedule and complete the pickup, verify ownership, and pay you.</li>
<li>To contact you about your offer, your pickup or questions you send us.</li>
<li>To keep records required by state vehicle, salvage and anti-theft laws.</li>
<li>To improve our pricing, website and service, including our Super Intelligent pricing models, using information that is aggregated or de-identified where possible.</li>
<li>To prevent fraud, protect our users and partners, and comply with the law.</li>
<li>To send service updates and, only with your permission, marketing messages you can opt out of at any time.</li>
</ul>'''),
    ('share', 'How we share information', '''
<p>We do not sell your personal information for money. We share it only as needed to deliver the service:</p>
<ul>
<li><strong>Offer and purchasing partners.</strong> Instant offers on our site are provided through our partner Peddle, LLC. Information you enter in the offer form is collected by Peddle to create and honor your offer, and is handled under Peddle's own privacy policy.</li>
<li><strong>Towing and recycling partners.</strong> Licensed tow operators and auto recyclers who pick up and process your vehicle receive the details needed to do so, such as your name, phone number, pickup address and vehicle details.</li>
<li><strong>Service providers.</strong> Companies that host our website, handle calls and messages, provide analytics or verify vehicle data, under contracts that limit their use of your information.</li>
<li><strong>Legal and safety reasons.</strong> Government agencies, law enforcement or others when required by law, such as state reporting of purchased salvage vehicles, or to protect rights, property and safety.</li>
<li><strong>Business transfers.</strong> A buyer or successor if our business is sold, merged or reorganized, subject to this policy.</li>
</ul>'''),
    ('cookies', 'Cookies and analytics', '''
<p>We use cookies and similar technologies to keep the site working, remember your preferences, understand how visitors use our pages, and measure the performance of our advertising. Some of these are set by third parties such as analytics and advertising providers.</p>
<p>You can block or delete cookies in your browser settings, and the site will still work, though some features may be limited. Where required by law, we honor Global Privacy Control (GPC) browser signals as a request to opt out of targeted advertising and the "sale" or "sharing" of personal information.</p>'''),
    ('messages', 'Calls, text messages and email', f'''
<p>If you give us your phone number, we may call or text you about your offer and pickup. We will only send automated marketing calls or texts with your prior express written consent, and consent is never a condition of selling your car. Message and data rates may apply.</p>
<p>Reply <strong>STOP</strong> to any text to opt out of further texts, or <strong>HELP</strong> for help. You can unsubscribe from marketing emails using the link in any email, or by contacting us at {PRIVACY_EMAIL}. We may still contact you about an offer or pickup that is in progress.</p>'''),
    ('rights', 'Your privacy rights', '''
<p>Depending on where you live, you may have the right to:</p>
<ul>
<li>Know what personal information we have about you and get a copy of it.</li>
<li>Correct inaccurate personal information.</li>
<li>Delete your personal information, subject to legal exceptions such as records we must keep.</li>
<li>Opt out of targeted advertising, the "sale" or "sharing" of personal information, and certain profiling.</li>
<li>Not be treated differently for exercising these rights.</li>
</ul>
<p><strong>California residents</strong> have these rights under the California Consumer Privacy Act as amended by the CPRA. In the past 12 months we collected the categories listed in the "Information we collect" section, for the purposes in "How we use your information", and disclosed them to the recipients in "How we share information". Residents of states with similar laws, including Virginia, Colorado, Connecticut, Utah, Texas, Oregon and others, have comparable rights, and may appeal a decision we make about their request by replying to our response.</p>
<p>To make a request, contact us using the details below. We will verify your identity before acting on a request, and you may use an authorized agent where the law allows.</p>'''),
    ('security', 'How we protect and keep your information', '''
<p>We use administrative, technical and physical safeguards appropriate to the information we handle, such as encrypted connections (HTTPS), access controls and limited staff access. No method of transmission or storage is completely secure, so we cannot guarantee absolute security.</p>
<p>We keep personal information only as long as needed for the purposes in this policy, including to meet legal, tax and vehicle-record requirements, and then delete or de-identify it.</p>'''),
    ('children', "Children's privacy", '''
<p>Our service is for adults who own or are authorized to sell a vehicle. We do not knowingly collect personal information from children under 16. If you believe a child has given us information, contact us and we will delete it.</p>'''),
    ('changes', 'Changes to this policy', '''
<p>We may update this policy as our service or the law changes. We will post the new version on this page and update the effective date above. If we make material changes, we will provide additional notice where required.</p>'''),
    ('contact', 'Contact us', f'''
<p>Questions or privacy requests can be sent to:</p>
<ul>
<li>Email: <a href="mailto:{PRIVACY_EMAIL}">{PRIVACY_EMAIL}</a></li>
<li>Phone: <a href="{TEL}">{PHONE}</a></li>
<li>Website: <a href="/contact/">usjunkcars.si/contact</a></li>
</ul>'''),
]
toc = ''.join(f'<li><a href="#{i}">{t}</a></li>' for i, t, _ in P_SECTIONS)
body = ''.join(f'<section id="{i}"><h2>{n}. {t}</h2>{c}</section>' for n, (i, t, c) in enumerate(P_SECTIONS, 1))
privacy_body = f'''<section class="page-title"><div class="container"><h1 class="section-title">Privacy Policy</h1>
<p class="page-title__lead">How US Junk Cars collects, uses and protects your information when you sell us your car.</p>
<div class="legal-meta"><span><b>Effective:</b> {EFFECTIVE}</span><span><b>Last updated:</b> {EFFECTIVE}</span><span><b>Applies to:</b> usjunkcars.si</span></div></div></section>
<section class="page-section"><div class="container">
<div class="legal-glance">
<div class="page-card"><h3>We never sell your data</h3><p>Your information is used to make your offer and complete your pickup, not sold for money.</p></div>
<div class="page-card"><h3>Only what we need</h3><p>Contact, vehicle and pickup details. No Social Security number is needed for an offer.</p></div>
<div class="page-card"><h3>You stay in control</h3><p>Ask to see, correct or delete your data, and opt out of marketing at any time.</p></div>
<div class="page-card"><h3>Shared to get the job done</h3><p>Only with our offer partner, tow and recycling partners, and service providers.</p></div>
</div></div></section>
<section class="page-section page-section--tint"><div class="container"><div class="legal-layout">
<nav class="legal-toc" aria-label="Privacy policy sections"><p>On this page</p><ol>{toc}</ol></nav>
<div class="legal-body page-content">{body}</div>
</div></div></section>
'''
write('privacy-policy', 'Privacy Policy | US Junk Cars',
      'How US Junk Cars collects, uses, shares and protects your personal information, and your privacy rights '
      'when you sell your junk car.',
      'Privacy Policy',
      [{'@context': 'https://schema.org', '@type': 'WebPage', 'name': 'Privacy Policy', 'url': f'{SITE}/privacy-policy/',
        'datePublished': '2026-10-15', 'dateModified': '2026-10-15',
        'publisher': {'@type': 'Organization', 'name': 'US Junk Cars', 'url': f'{SITE}/'}},
       breadcrumb_ld('privacy-policy', 'Privacy Policy')],
      privacy_body)
