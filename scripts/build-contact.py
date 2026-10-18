"""Write the Contact page into content/ (seller guide: reach us, what happens next, paperwork, value tips,
pickup checklist, scam safety, FAQ) and refresh its structured data.

Run: python3 scripts/build-contact.py
"""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE, PHONE, TEL, EMAIL = 'https://usjunkcars.si', '1-844-512-0697', 'tel:+18445120697', 'support@usjunkcars.si'
LEGAL, ADDR = 'USJunkCars', 'Jacksonville, FL 32224'
ARROW = '<svg class="icon icon--arrow-left" height="20" width="11"> <use xlink:href="#icon-arrow-left"></use> </svg>'
OFFER_BTN = f'<a class="button button--default" data-peddle-offer="" href="{TEL}"><span class="button__inner">Get My Instant Offer {ARROW}</span></a>'
CALL_BTN = f'<a class="button button--red" href="{TEL}"><span class="button__inner">Call {PHONE}</span></a>'

FAQ = [
    ('Can I sell a junk car without a title?',
     'Often, yes. Many states accept a current registration with a matching photo ID, and some do not require a title for older vehicles. Tell us what documents you have when you request your offer and we will confirm before pickup.'),
    ('Who pays the most for junk cars?',
     'The best price usually comes from a buyer who values the whole car, including reusable parts, not only its scrap weight, and who includes towing for free. Compare offers by the amount you actually receive after any towing or paperwork fees.'),
    ('How fast can you pick up my car?',
     'Most pickups happen within one to two days of accepting your offer, and same-day pickup is often possible. You choose the time slot that works for you.'),
    ('Do I have to be there for the pickup?',
     'Usually someone needs to hand over the keys and sign the title or bill of sale. If you cannot be there, tell us when you schedule and we will explain the options your state allows.'),
    ('What areas do you serve?',
     'We buy junk cars across the United States. Enter your ZIP code in the offer form to confirm pickup for your address.'),
]


def faq_html(items):
    return ''.join(f'<details class="faq-accordion__item faq-item"><summary class="faq-accordion__header font-bold color-blue"><span>{q}</span></summary>'
                   f'<p class="faq-item__answer">{a}</p></details>\n' for q, a in items)


def checklist(items):
    return '<ul class="checklist">' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'


page = f'''<div class="breadcrumbs"><div class="container"><ul class="breadcrumbs-list"><li class="breadcrumbs-list__item"><a class="breadcrumbs-list__item-link" href="/">Home</a></li><li class="breadcrumbs-list__item" aria-current="page">Contact us</li></ul></div></div>
<section class="page-title"><div class="container"><h1 class="section-title">Contact US Junk Cars</h1><p class="page-title__lead">Talk to a person about your car, your paperwork or a scheduled pickup, or skip the call and get your instant offer online at any hour. Below you will find everything to prepare so your sale goes smoothly.</p><div class="page-cta-row">{OFFER_BTN}{CALL_BTN}</div></div></section>

<section class="page-section"><div class="container">
<h2 class="section-title">Ways to reach us</h2>
<div class="page-cards page-cards--four">
<div class="page-card"><h3>Call us, 24/7</h3><a class="page-card__big" href="{TEL}">{PHONE}</a><p>Offers, title questions or a pickup you already booked. We answer every day.</p></div>
<div class="page-card"><h3>Instant offer online</h3><p style="margin-bottom:14px">See your price in about two minutes, day or night. No call needed.</p>{OFFER_BTN}</div>
<div class="page-card"><h3>Email</h3><a class="page-card__link" href="mailto:{EMAIL}">{EMAIL}</a><p>Best for documents and non-urgent questions. We reply within one business day.</p></div>
<div class="page-card"><h3>Business address</h3><p><strong>{LEGAL}</strong><br/>{ADDR}<br/>United States</p><p class="page-card__note">We buy junk cars nationwide. <a href="/locations/">Check coverage for your state →</a></p></div>
</div></div></section>

<section class="page-section page-section--tint"><div class="container">
<h2 class="section-title">What happens after you reach out</h2>
<ol class="steps-timeline">
<li><span class="steps-timeline__time">About 2 minutes</span><h3>Get your offer</h3><p>Answer a few questions about the year, make, model and condition. Your cash offer appears right away, online or on the phone.</p></li>
<li><span class="steps-timeline__time">Same or next day</span><h3>Schedule the pickup</h3><p>Accept the offer and choose a time slot. You get a confirmation with the pickup window and what to have ready.</p></li>
<li><span class="steps-timeline__time">About 15 minutes</span><h3>Driver arrives</h3><p>The driver calls ahead, checks that the car matches your description and reviews the paperwork with you.</p></li>
<li><span class="steps-timeline__time">On the spot</span><h3>Get paid</h3><p>You sign the title or bill of sale and get paid before the car is towed away. Towing is free.</p></li>
</ol>
</div></section>

<section class="page-section"><div class="container">
<h2 class="section-title">What paperwork do I need to junk a car?</h2>
<p class="section-lead">Find your situation. Requirements vary by state, so we confirm your documents before the driver comes out.</p>
<div class="page-cards">
<div class="page-card"><h3>I have the title</h3>{checklist(['The signed-over title, or your signature at pickup', 'A photo ID that matches the name on the title', 'Keys, if you still have them'])}</div>
<div class="page-card"><h3>The title is lost</h3>{checklist(['Current or recent registration in your name', 'A matching photo ID', 'Or a duplicate title from your state DMV, often available online'])}</div>
<div class="page-card"><h3>Inherited or in a relative's name</h3>{checklist(["Title plus the death certificate or a letter of administration", 'Or a signed authorization from the owner', 'Your photo ID'])}</div>
<div class="page-card"><h3>The car still has a loan</h3>{checklist(['A payoff letter from your lender', 'The lien release once the loan is paid', 'We cannot buy a car with an active lien'])}</div>
</div>
<p class="section-note">Not sure what you have? Call {PHONE} or read the <a href="/faq/">junk car FAQ</a>.</p>
</div></section>

<section class="page-section page-section--tint"><div class="container"><div class="page-split">
<div class="page-content">
<h2 class="section-title">How to get the most money for your junk car</h2>
{checklist([
    '<strong>Describe it honestly.</strong> Accurate details mean the offer you see is the offer you get at pickup.',
    '<strong>Keep the valuable parts on.</strong> A missing catalytic converter, battery, wheels or engine lowers the price.',
    '<strong>Have your paperwork ready.</strong> A clean title or accepted documents avoids delays and price changes.',
    '<strong>Sell sooner.</strong> Cars sitting outside lose value to rust, flat tires and missing parts, and keep costing registration and insurance.',
    '<strong>Compare the real total.</strong> A higher quote with towing or "paperwork" fees can pay less than a free-towing offer.',
])}
</div>
<div class="page-content">
<h2 class="section-title">Get ready for pickup day</h2>
{checklist([
    'Remove personal items from the glovebox, trunk and under the seats',
    'Take off your license plates, unless your state says otherwise',
    'Remove toll tags, parking stickers and garage door openers',
    'Make sure the driver can reach the car, even if it does not run',
    'After the sale, cancel your insurance and file a notice of sale with your DMV if your state requires one',
])}
</div>
</div></div></section>

<section class="page-section"><div class="container">
<h2 class="section-title">Stay safe: how to spot a junk car scam</h2>
<div class="page-cards">
<div class="page-card"><h3>Never pay for towing</h3><p>Legitimate junk car buyers include pickup in the offer. A fee requested on arrival is a red flag.</p></div>
<div class="page-card"><h3>Get paid before the car leaves</h3><p>Do not hand over the title or keys for a promise to pay later. Payment happens at pickup.</p></div>
<div class="page-card"><h3>Watch for bait-and-switch</h3><p>A big phone quote that drops for no clear reason at the curb is a common trick. Ask what can change the price before you schedule.</p></div>
<div class="page-card"><h3>Sign only your own paperwork</h3><p>Fill in the buyer's details on the title and keep a copy of the bill of sale for your records.</p></div>
</div>
</div></section>

<section class="section faq"><div class="container">
<h2 class="section-title text-center">Questions sellers ask before calling</h2>
<div class="faq-accordion faq-accordion--answered"><div class="faq-accordion__column">
{faq_html(FAQ[:3])}</div><div class="faq-accordion__column">
{faq_html(FAQ[3:])}</div></div>
<div class="page-cta-row page-cta-row--center">{OFFER_BTN}{CALL_BTN}</div>
</div></section>
'''
(ROOT / 'content/pages/contact.html').write_text(page)

reg_path = ROOT / 'content/publication.json'
reg = json.loads(reg_path.read_text())
route = next(r for r in reg['routes'] if r['id'] == 'contact')
route['description'] = ('Contact US Junk Cars 24/7 at 1-844-512-0697 or online. See what paperwork you need to junk a car, '
                        'how to get the most money, pickup-day tips and how to avoid junk car scams.')
contact_ld = next(x for x in route['jsonLd'] if x.get('@type') == 'ContactPage')
point = contact_ld['mainEntity'].setdefault('contactPoint', {})
point.update({'@type': 'ContactPoint', 'telephone': '+1-844-512-0697', 'email': EMAIL, 'contactType': 'customer service',
              'areaServed': 'US', 'availableLanguage': 'English', 'hoursAvailable': {
                  '@type': 'OpeningHoursSpecification', 'opens': '00:00', 'closes': '23:59',
                  'dayOfWeek': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']}})
route['jsonLd'] = [x for x in route['jsonLd'] if x.get('@type') != 'FAQPage'] + [{
    '@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in FAQ]}]
reg_path.write_text(json.dumps(reg, indent=2, ensure_ascii=False) + '\n')
print('contact page written; structured data types:', [x['@type'] for x in route['jsonLd']])
