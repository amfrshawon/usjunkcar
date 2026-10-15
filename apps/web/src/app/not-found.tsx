import Link from 'next/link';

export default function NotFound() {
  return (
    <main className="main">
      <section className="page-title">
        <div className="container">
          <h1 className="section-title">Page not found</h1>
          <p className="page-title__lead">Sorry, that page does not exist. You can still get a cash offer for your junk car in minutes.</p>
          <div className="page-cta-row">
            <Link className="button button--default" href="/"><span className="button__inner">Go to the homepage</span></Link>
            <a className="button button--white" href="tel:+18445120697"><span className="button__inner" style={{ color: '#DE193E' }}>Call 1-844-512-0697</span></a>
          </div>
        </div>
      </section>
    </main>
  );
}
