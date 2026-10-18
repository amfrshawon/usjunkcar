"""Write the Terms and Conditions page into content/ and register it (same design as the Privacy Policy).

Run: python3 scripts/build-terms.py
"""
import html, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE, PHONE, TEL = 'https://usjunkcars.si', '1-844-512-0697', 'tel:+18445120697'
EFFECTIVE, ISO = 'October 18, 2026', '2026-10-18'
EMAIL = 'support@usjunkcars.si'
PATH, ID = '/terms-and-conditions/', 'terms-and-conditions'

SECTIONS = [
    ('agreement', 'Agreement to these terms', '''
<p>These Terms and Conditions ("Terms") govern your use of <a href="/">usjunkcars.si</a> and of the services offered by USJunkCars, doing business as US Junk Cars, of Jacksonville, FL 32224 ("US Junk Cars", "we", "us"), including instant cash offers, vehicle pickup and payment. By using the website, requesting an offer, scheduling a pickup or selling a vehicle through us, you agree to these Terms and to our <a href="/privacy-policy/">Privacy Policy</a>.</p>
<p>If you do not agree, please do not use the website or our services.</p>'''),
    ('eligibility', 'Who can sell a vehicle', '''
<ul>
<li>You must be at least 18 years old and able to enter into a binding agreement.</li>
<li>You must be the legal owner of the vehicle, or be authorized in writing by the owner to sell it.</li>
<li>The vehicle must be located in an area we serve. Your ZIP code is checked when you request an offer.</li>
</ul>'''),
    ('offers', 'How offers work', '''
<p>Your offer is based on the information you provide about the vehicle, including its year, make, model, mileage, condition, location and title status, and on current scrap and parts values.</p>
<ul>
<li><strong>Accurate details.</strong> You agree to describe the vehicle truthfully and completely, including major damage, missing parts and whether it starts and drives.</li>
<li><strong>Verification at pickup.</strong> The driver checks the vehicle and paperwork before payment. If the vehicle differs materially from your description, the offer may be revised. You can accept the revised offer or decline the sale at no cost to you.</li>
<li><strong>Expiration.</strong> Offers are valid for the period shown with the offer. After that, a new offer may be needed because scrap and parts values change.</li>
<li><strong>No obligation.</strong> Requesting an offer does not obligate you to sell, and we may decline to make an offer for any lawful reason.</li>
</ul>'''),
    ('title', 'Title, ownership and paperwork', '''
<p>By selling a vehicle you confirm that you have the right to sell it and that, to your knowledge, it is free of liens and undisclosed claims, or that any lien will be released at the sale.</p>
<ul>
<li>You agree to provide the title or the ownership documents your state accepts, and a valid government-issued photo ID that matches them.</li>
<li>Rules for selling without a title differ by state. We tell you before pickup whether your documents are sufficient, and we do not buy vehicles where the law does not allow the sale.</li>
<li>We may be required to report vehicle purchases to state agencies or anti-theft databases.</li>
</ul>'''),
    ('pickup', 'Pickup and towing', '''
<ul>
<li>Towing is free for accepted offers in our service area. Nothing is deducted from your offer for pickup.</li>
<li>You agree to provide safe, legal access to the vehicle at the scheduled time and location. If the vehicle cannot be reached, for example because it is blocked or on private property without permission, the pickup may be rescheduled.</li>
<li>Pickup times are estimates. We will contact you if a driver is delayed.</li>
<li>Remove all personal belongings before pickup. We are not responsible for items left in the vehicle.</li>
</ul>'''),
    ('payment', 'Payment', '''
<p>You are paid when the vehicle is collected, after the vehicle and paperwork are verified. The payment method is shown when you schedule the pickup. Ownership and risk pass to the buyer when payment is made and the paperwork is signed.</p>'''),
    ('after-sale', 'Your responsibilities after the sale', '''
<ul>
<li>Remove and keep, return or transfer your license plates as your state requires.</li>
<li>Cancel your insurance and any toll or parking accounts linked to the vehicle.</li>
<li>File any notice of sale or release of liability that your state requires.</li>
</ul>'''),
    ('communications', 'Calls, texts and emails', f'''
<p>By giving us your phone number or email, you agree that we and our partners may contact you about your offer, pickup and sale. Marketing calls or texts using automated technology are sent only with your prior express written consent, which is never a condition of selling your vehicle. Message and data rates may apply. Reply <strong>STOP</strong> to opt out of texts or <strong>HELP</strong> for help.</p>'''),
    ('partners', 'Offer partner and third-party services', '''
<p>Instant offers on our website are provided through our partner Peddle, LLC. When you use the offer form, Peddle's own terms and privacy policy also apply to the information you submit and to any offer it makes. Pickups may be carried out by licensed independent towing and recycling partners. Links to third-party websites are provided for convenience; we are not responsible for their content or practices.</p>'''),
    ('website', 'Using our website', '''
<p>You agree not to misuse the website, including by submitting false information or someone else's details, attempting to access systems or data without permission, interfering with its operation, or copying content for commercial use without our written permission.</p>
<p>The US Junk Cars name, logo, text and graphics on this website are owned by or licensed to us and are protected by intellectual property laws.</p>'''),
    ('disclaimers', 'Disclaimers and limitation of liability', '''
<p>The website and its content are provided "as is" for general information. Estimates, guides and FAQs are not legal, tax or financial advice. To the fullest extent permitted by law, we disclaim implied warranties, and we are not liable for indirect, incidental or consequential damages arising from your use of the website or services. Our total liability for any claim relating to a sale is limited to the amount paid for the vehicle involved.</p>
<p>Nothing in these Terms limits rights you have under applicable consumer protection law that cannot be waived.</p>'''),
    ('indemnity', 'Your responsibility for false information', '''
<p>You agree to compensate US Junk Cars and its partners for losses caused by information you knowingly misstate, including selling a vehicle you do not have the right to sell or concealing a lien.</p>'''),
    ('disputes', 'Disputes and governing law', '''
<p>If you have a concern, please contact us first so we can try to resolve it informally. These Terms are governed by the laws of the State of Florida and applicable federal law, without regard to conflict-of-law rules, unless the law of your state of residence requires otherwise.</p>'''),
    ('changes', 'Changes to these terms', '''
<p>We may update these Terms as our services or the law change. The updated version is posted on this page with a new effective date. Terms in effect when you accepted an offer apply to that sale.</p>'''),
    ('contact', 'Contact us', f'''
<p>Questions about these Terms can be sent to:</p>
<ul>
<li>Email: <a href="mailto:{EMAIL}">{EMAIL}</a></li>
<li>Phone: <a href="{TEL}">{PHONE}</a></li>
<li>Mail: USJunkCars, Jacksonville, FL 32224, United States</li>
<li>Website: <a href="/contact/">usjunkcars.si/contact</a></li>
</ul>'''),
]

toc = ''.join(f'<li><a href="#{i}">{t}</a></li>' for i, t, _ in SECTIONS)
body = ''.join(f'<section id="{i}"><h2>{n}. {t}</h2>{c}</section>' for n, (i, t, c) in enumerate(SECTIONS, 1))
page = f'''<div class="breadcrumbs"><div class="container"><ul class="breadcrumbs-list"><li class="breadcrumbs-list__item"><a class="breadcrumbs-list__item-link" href="/">Home</a></li><li class="breadcrumbs-list__item" aria-current="page">Terms and Conditions</li></ul></div></div>
<section class="page-title"><div class="container"><h1 class="section-title">Terms and Conditions</h1>
<p class="page-title__lead">The rules for using usjunkcars.si and selling your junk car to US Junk Cars, written in plain English.</p>
<div class="legal-meta"><span><b>Effective:</b> {EFFECTIVE}</span><span><b>Last updated:</b> {EFFECTIVE}</span><span><b>Applies to:</b> usjunkcars.si and all sales</span></div></div></section>
<section class="page-section"><div class="container">
<h2 class="section-title">Key terms at a glance</h2>
<div class="legal-glance">
<div class="page-card"><h3>No obligation to sell</h3><p>Get an offer, ask questions and decline at any time before the sale is complete.</p></div>
<div class="page-card"><h3>Describe the car honestly</h3><p>Your offer depends on accurate details. Big differences found at pickup can change the price.</p></div>
<div class="page-card"><h3>Free towing, paid at pickup</h3><p>Pickup costs you nothing, and you are paid when the car and paperwork are verified.</p></div>
<div class="page-card"><h3>Proof of ownership</h3><p>Bring the title or the documents your state accepts, plus a matching photo ID.</p></div>
</div></div></section>
<section class="page-section page-section--tint"><div class="container"><div class="legal-layout">
<nav class="legal-toc" aria-label="Terms and conditions sections"><p>On this page</p><ol>{toc}</ol></nav>
<div class="legal-body page-content">{body}</div>
</div></div></section>
'''
(ROOT / 'content/pages' / f'{ID}.html').write_text(page)

reg_path = ROOT / 'content/publication.json'
reg = json.loads(reg_path.read_text())
route = {
    'id': ID, 'path': PATH, 'family': 'legal',
    'title': 'Terms and Conditions | USJunkCars',
    'description': 'Terms for using usjunkcars.si and selling your junk car: offers, title and ownership, free pickup, payment at pickup and your responsibilities.',
    'lastModified': ISO,
    'jsonLd': [
        {'@context': 'https://schema.org', '@type': 'WebPage', 'name': 'Terms and Conditions', 'url': f'{SITE}{PATH}',
         'datePublished': ISO, 'dateModified': ISO, 'publisher': {'@type': 'Organization', 'name': 'US Junk Cars', 'legalName': 'USJunkCars', 'url': f'{SITE}/'}},
        {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': f'{SITE}/'},
            {'@type': 'ListItem', 'position': 2, 'name': 'Terms and Conditions', 'item': f'{SITE}{PATH}'}]}],
    'status': 'review', 'environments': ['local', 'development'], 'approval': None,
}
existing = next((r for r in reg['routes'] if r['id'] == ID), None)
if existing:
    route.update(status=existing['status'], environments=existing['environments'], approval=existing['approval'])
    reg['routes'][reg['routes'].index(existing)] = route
else:
    reg['routes'].append(route)
reg_path.write_text(json.dumps(reg, indent=2, ensure_ascii=False) + '\n')
print('wrote', PATH, '| registry routes:', len(reg['routes']))
