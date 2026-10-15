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


home = link_nav((ROOT / 'index.html').read_text())
(ROOT / 'index.html').write_text(home)

head_end = home.index('<main class="main">')
shell_top, shell_bottom = home[:head_end], home[home.index('</main>'):]
steps = re.search(r'<div class="hiw">\s*<div class="container container--small">.*?</ul>\s*</div>\s*</div>', home, re.S).group(0)
cta = re.search(r'<div class="hiw">\s*<div class="container">\s*<div class="hiw__cta".*?</div>\s*</div>\s*</div>\s*</div>', home, re.S).group(0)
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
state_list = ''.join(f'<li><a data-peddle-offer="" href="{TEL}">Junk car removal in {s}</a></li>' for s in STATES)
loc_body = title_block(
    'Junk Car Removal Near Me: Service Across the USA',
    'Find cash for junk cars near you without calling around. Enter your ZIP code in the offer form and we confirm '
    'pickup for your address, with free towing from your driveway, street, parking lot or repair shop.') + f'''
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
<section class="page-section page-section--tint"><div class="container"><div class="page-content">
<h2 class="section-title">Choose your state</h2>
<p>We buy junk cars in every state listed below. Service reaches most ZIP codes; select your state to start an offer and the form confirms coverage for your exact address.</p>
</div>
<ul class="state-grid">{state_list}</ul>
</div></section>
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
