import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Methodology & contributions | CongoLangAtlas",
  description: "How CongoLangAtlas sources, reviews, maps, and publishes evidence, and how to contribute corrections, resources, or code.",
};

const workflow = [
  ["01", "Discover", "Find catalogues, publications, datasets, models, repositories, and documented community knowledge."],
  ["02", "Describe", "Record identity, geographic scope, dates, licence, access conditions, provenance, and uncertainty as separate fields."],
  ["03", "Validate", "Run schema, reference, geography, publication-safety, and reproducibility checks without treating automation as approval."],
  ["04", "Review", "Ask a named human reviewer to resolve language variety, location, licence, access, and attribution questions."],
  ["05", "Publish", "Generate a metadata-only public bundle and retain citations, limitations, and review history beside each claim."],
];

export default function MethodologyPage() {
  return (
    <main className="methodology-page">
      <header className="methodology-header">
        <Link href="/" className="wordmark" aria-label="Return to CongoLangAtlas">
          <span className="wordmark__mark">CL</span><span className="wordmark__name">Atlas</span>
        </Link>
        <Link className="methodology-back" href="/">← Explore the atlas</Link>
      </header>

      <section className="methodology-hero">
        <p className="eyebrow">Project methodology</p>
        <h1>Evidence first, uncertainty visible, communities involved.</h1>
        <p>CongoLangAtlas connects Congolese languages with geographic evidence, linguistic documentation, datasets, models, and research. It is a research guide, not a definitive map of where languages begin or end.</p>
        <nav className="methodology-jump" aria-label="On this page">
          <a href="#principles">Principles</a><a href="#workflow">Evidence workflow</a><a href="#contribute">Contribute</a>
        </nav>
      </section>

      <section className="methodology-section" id="principles">
        <div className="methodology-section__heading"><p className="eyebrow">01 · Principles</p><h2>What the atlas promises</h2></div>
        <div className="principle-grid">
          <article><strong>Evidence before appearance</strong><p>Every public claim should point to a traceable source, citation, page or table, or documented community review.</p></article>
          <article><strong>Geography is context</strong><p>Province and territory polygons support navigation. They are not presented as language boundaries or complete distributions.</p></article>
          <article><strong>Uncertainty stays visible</strong><p>Candidate records, approximate locations, historical estimates, conflicting names, and unresolved varieties keep their limitations.</p></article>
          <article><strong>Metadata is not permission</strong><p>Licence, download access, and redistribution rights are tracked independently. Finding a resource does not make it reusable.</p></article>
          <article><strong>Human review matters</strong><p>Automated checks can identify errors, but they cannot promote a draft claim or replace linguistic and community expertise.</p></article>
          <article><strong>Safety sets the boundary</strong><p>The public atlas contains metadata and permitted aggregates, never restricted corpus content, credentials, personal data, or sensitive locations.</p></article>
        </div>
      </section>

      <section className="methodology-section methodology-section--dark" id="workflow">
        <div className="methodology-section__heading"><p className="eyebrow">02 · Evidence workflow</p><h2>From source lead to public record</h2><p>A visible result may be a reviewed catalogue record or a source-linked candidate awaiting review. The interface keeps that distinction explicit.</p></div>
        <ol className="methodology-workflow">
          {workflow.map(([number, title, description]) => <li key={number}><span>{number}</span><div><strong>{title}</strong><p>{description}</p></div></li>)}
        </ol>
        <div className="methodology-note"><strong>How to read the map</strong><p>Administrative areas show where evidence has been associated with a place. Counts describe indexed evidence coverage, not demographic totals, proficiency, exclusivity, or completeness.</p></div>
      </section>

      <section className="methodology-section" id="contribute">
        <div className="methodology-section__heading"><p className="eyebrow">03 · Contributions</p><h2>Improve the evidence with us</h2><p>You can add a resource, correct a claim, review a language profile, improve validation, or help develop the interface.</p></div>
        <div className="contribution-grid">
          <article><span>Data and corrections</span><h3>Document the change</h3><p>Provide the language or variety, the exact field to change, a source and locator, geographic precision, relevant dates, licence and access terms, uncertainty notes, and your preferred credit.</p></article>
          <article><span>Community review</span><h3>Add lived expertise</h3><p>Share preferred names, local usage, variety distinctions, and geographic context. Community knowledge is valuable and should be represented with consent, attribution, and clear review notes.</p></article>
          <article><span>Technical work</span><h3>Strengthen the atlas</h3><p>Add tests or validation for changed behavior, preserve accessibility and low-bandwidth support, and keep generated artifacts reproducible from their documented sources.</p></article>
        </div>
        <div className="contribution-warning"><strong>Do not submit</strong><p>Copyrighted corpus text, restricted audio, passwords or credentials, private correspondence, personal information, or sensitive community locations.</p></div>
        <div className="methodology-actions">
          <a className="methodology-action methodology-action--primary" href="https://github.com/Ashuza11/CongoLangAtlas/blob/main/CONTRIBUTING.md" target="_blank" rel="noreferrer"><span>Read the contribution guide</span><i aria-hidden>↗</i></a>
          <a className="methodology-action" href="https://github.com/Ashuza11/CongoLangAtlas/issues" target="_blank" rel="noreferrer"><span>Propose a correction</span><i aria-hidden>↗</i></a>
          <a className="methodology-action" href="https://github.com/Ashuza11/CongoLangAtlas" target="_blank" rel="noreferrer"><span>Browse the repository</span><i aria-hidden>↗</i></a>
        </div>
      </section>

      <footer className="methodology-footer"><p>CongoLangAtlas is a project by <a href="https://kivulinguaai.org/" target="_blank" rel="noreferrer">KivuLingua AI</a>.</p><Link href="/">Return to the atlas</Link></footer>
    </main>
  );
}
