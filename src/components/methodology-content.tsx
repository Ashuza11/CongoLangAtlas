import Link from "next/link";
import LanguageSwitcher from "@/components/language-switcher";
import type { Locale } from "@/lib/i18n";

const content = {
  en: {
    back: "← Explore the atlas", project: "Project methodology", title: "Evidence first, uncertainty visible, communities involved.",
    intro: "CongoLangAtlas connects Congolese languages with geographic evidence, linguistic documentation, datasets, models, and research. It is a research guide, not a definitive map of where languages begin or end.",
    onPage: "On this page", principles: "Principles", workflowLink: "Evidence workflow", contribute: "Contribute", principlesEyebrow: "01 · Principles", promises: "What the atlas promises",
    principleItems: [
      ["Evidence before appearance", "Every public claim should point to a traceable source, citation, page or table, or documented community review."],
      ["Geography is context", "Province and territory polygons support navigation. They are not presented as language boundaries or complete distributions."],
      ["Uncertainty stays visible", "Candidate records, approximate locations, historical estimates, conflicting names, and unresolved varieties keep their limitations."],
      ["Metadata is not permission", "Licence, download access, and redistribution rights are tracked independently. Finding a resource does not make it reusable."],
      ["Human review matters", "Automated checks can identify errors, but they cannot promote a draft claim or replace linguistic and community expertise."],
      ["Safety sets the boundary", "The public atlas contains metadata and permitted aggregates, never restricted corpus content, credentials, personal data, or sensitive locations."],
    ],
    workflowEyebrow: "02 · Evidence workflow", workflowTitle: "From source lead to public record", workflowIntro: "A visible result may be a reviewed catalogue record or a source-linked candidate awaiting review. The interface keeps that distinction explicit.",
    workflow: [
      ["01", "Discover", "Find catalogues, publications, datasets, models, repositories, and documented community knowledge."],
      ["02", "Describe", "Record identity, geographic scope, dates, licence, access conditions, provenance, and uncertainty as separate fields."],
      ["03", "Validate", "Run schema, reference, geography, publication-safety, and reproducibility checks without treating automation as approval."],
      ["04", "Review", "Ask a named human reviewer to resolve language variety, location, licence, access, and attribution questions."],
      ["05", "Publish", "Generate a metadata-only public bundle and retain citations, limitations, and review history beside each claim."],
    ],
    readMap: "How to read the map", mapNote: "Administrative areas show where evidence has been associated with a place. Counts describe indexed evidence coverage, not demographic totals, proficiency, exclusivity, or completeness.",
    contributionEyebrow: "03 · Contributions", contributionTitle: "Improve the evidence with us", contributionIntro: "You can add a resource, correct a claim, review a language profile, improve validation, or help develop the interface.",
    contributions: [
      ["Data and corrections", "Document the change", "Provide the language or variety, the exact field to change, a source and locator, geographic precision, relevant dates, licence and access terms, uncertainty notes, and your preferred credit."],
      ["Community review", "Add lived expertise", "Share preferred names, local usage, variety distinctions, and geographic context. Community knowledge is valuable and should be represented with consent, attribution, and clear review notes."],
      ["Technical work", "Strengthen the atlas", "Add tests or validation for changed behavior, preserve accessibility and low-bandwidth support, and keep generated artifacts reproducible from their documented sources."],
    ],
    doNotSubmit: "Do not submit", warning: "Copyrighted corpus text, restricted audio, passwords or credentials, private correspondence, personal information, or sensitive community locations.",
    guide: "Read the contribution guide", correction: "Propose a correction", repository: "Browse the repository", projectBy: "CongoLangAtlas is a project by", return: "Return to the atlas",
  },
  fr: {
    back: "← Explorer l’atlas", project: "Méthodologie du projet", title: "Les données d’abord, l’incertitude visible, les communautés impliquées.",
    intro: "CongoLangAtlas relie les langues congolaises à des données géographiques, de la documentation linguistique, des jeux de données, des modèles et des travaux de recherche. C’est un guide de recherche, et non une carte définitive des limites linguistiques.",
    onPage: "Sur cette page", principles: "Principes", workflowLink: "Cycle des données", contribute: "Contribuer", principlesEyebrow: "01 · Principes", promises: "Les engagements de l’atlas",
    principleItems: [
      ["Les sources avant l’apparence", "Chaque information publique doit renvoyer à une source traçable, une citation, une page ou un tableau, ou à une vérification communautaire documentée."],
      ["La géographie est un contexte", "Les polygones des provinces et territoires facilitent la navigation. Ils ne représentent ni des frontières linguistiques ni des répartitions complètes."],
      ["L’incertitude reste visible", "Les fiches candidates, lieux approximatifs, estimations historiques, noms contradictoires et variétés non résolues conservent leurs limites."],
      ["Les métadonnées ne sont pas une autorisation", "La licence, l’accès au téléchargement et les droits de redistribution sont suivis séparément. Trouver une ressource ne la rend pas réutilisable."],
      ["La vérification humaine compte", "Les contrôles automatisés peuvent repérer des erreurs, mais ils ne peuvent ni valider une piste ni remplacer l’expertise linguistique et communautaire."],
      ["La sécurité fixe la limite", "L’atlas public contient des métadonnées et des agrégats autorisés, jamais des corpus restreints, identifiants, données personnelles ou lieux sensibles."],
    ],
    workflowEyebrow: "02 · Cycle des données", workflowTitle: "D’une piste à une fiche publique", workflowIntro: "Un résultat visible peut être une fiche de catalogue vérifiée ou une piste liée à une source et en attente d’examen. L’interface distingue clairement ces deux états.",
    workflow: [
      ["01", "Découvrir", "Trouver des catalogues, publications, jeux de données, modèles, dépôts et connaissances communautaires documentées."],
      ["02", "Décrire", "Consigner séparément l’identité, la portée géographique, les dates, la licence, les conditions d’accès, la provenance et l’incertitude."],
      ["03", "Valider", "Contrôler les schémas, références, données géographiques, règles de publication et la reproductibilité sans confondre automatisation et approbation."],
      ["04", "Vérifier", "Demander à une personne identifiée de résoudre les questions de variété linguistique, lieu, licence, accès et attribution."],
      ["05", "Publier", "Générer un ensemble public limité aux métadonnées et conserver les citations, limites et l’historique de vérification avec chaque information."],
    ],
    readMap: "Comment lire la carte", mapNote: "Les zones administratives indiquent où des données ont été associées à un lieu. Les comptes décrivent la couverture des données répertoriées, et non des totaux démographiques, le niveau de maîtrise, l’exclusivité ou l’exhaustivité.",
    contributionEyebrow: "03 · Contributions", contributionTitle: "Améliorez les données avec nous", contributionIntro: "Vous pouvez ajouter une ressource, corriger une information, vérifier une fiche de langue, améliorer la validation ou contribuer à l’interface.",
    contributions: [
      ["Données et corrections", "Documenter la modification", "Indiquez la langue ou variété, le champ précis à modifier, une source et son emplacement, la précision géographique, les dates utiles, les conditions de licence et d’accès, les incertitudes et la mention souhaitée."],
      ["Vérification communautaire", "Apporter une expertise vécue", "Partagez les noms privilégiés, les usages locaux, les distinctions entre variétés et le contexte géographique. Les savoirs communautaires doivent être représentés avec consentement, attribution et notes de vérification claires."],
      ["Travail technique", "Renforcer l’atlas", "Ajoutez des tests ou validations pour tout changement, préservez l’accessibilité et l’usage à faible débit, et gardez les artefacts générés reproductibles depuis leurs sources documentées."],
    ],
    doNotSubmit: "Ne soumettez pas", warning: "De textes de corpus protégés, d’enregistrements restreints, de mots de passe ou identifiants, de correspondance privée, de données personnelles ou de lieux communautaires sensibles.",
    guide: "Lire le guide de contribution", correction: "Proposer une correction", repository: "Parcourir le dépôt", projectBy: "CongoLangAtlas est un projet de", return: "Retourner à l’atlas",
  },
};

export default function MethodologyContent({ locale }: { locale: Locale }) {
  const c = content[locale];
  const home = locale === "fr" ? "/fr" : "/";
  return (
    <main className="methodology-page">
      <header className="methodology-header">
        <Link href={home} className="wordmark" aria-label={c.return}><span className="wordmark__mark">CL</span><span className="wordmark__name">Atlas</span></Link>
        <div className="methodology-header__actions"><Link className="methodology-back" href={home}>{c.back}</Link><LanguageSwitcher locale={locale} page="methodology" /></div>
      </header>
      <section className="methodology-hero">
        <p className="eyebrow">{c.project}</p><h1>{c.title}</h1><p>{c.intro}</p>
        <nav className="methodology-jump" aria-label={c.onPage}><a href="#principles">{c.principles}</a><a href="#workflow">{c.workflowLink}</a><a href="#contribute">{c.contribute}</a></nav>
      </section>
      <section className="methodology-section" id="principles">
        <div className="methodology-section__heading"><p className="eyebrow">{c.principlesEyebrow}</p><h2>{c.promises}</h2></div>
        <div className="principle-grid">{c.principleItems.map(([title, description]) => <article key={title}><strong>{title}</strong><p>{description}</p></article>)}</div>
      </section>
      <section className="methodology-section methodology-section--dark" id="workflow">
        <div className="methodology-section__heading"><p className="eyebrow">{c.workflowEyebrow}</p><h2>{c.workflowTitle}</h2><p>{c.workflowIntro}</p></div>
        <ol className="methodology-workflow">{c.workflow.map(([number, title, description]) => <li key={number}><span>{number}</span><div><strong>{title}</strong><p>{description}</p></div></li>)}</ol>
        <div className="methodology-note"><strong>{c.readMap}</strong><p>{c.mapNote}</p></div>
      </section>
      <section className="methodology-section" id="contribute">
        <div className="methodology-section__heading"><p className="eyebrow">{c.contributionEyebrow}</p><h2>{c.contributionTitle}</h2><p>{c.contributionIntro}</p></div>
        <div className="contribution-grid">{c.contributions.map(([label, title, description]) => <article key={label}><span>{label}</span><h3>{title}</h3><p>{description}</p></article>)}</div>
        <div className="contribution-warning"><strong>{c.doNotSubmit}</strong><p>{c.warning}</p></div>
        <div className="methodology-actions">
          <a className="methodology-action methodology-action--primary" href="https://github.com/Ashuza11/CongoLangAtlas/blob/main/CONTRIBUTING.md" target="_blank" rel="noreferrer"><span>{c.guide}</span><i aria-hidden>↗</i></a>
          <a className="methodology-action" href="https://github.com/Ashuza11/CongoLangAtlas/issues" target="_blank" rel="noreferrer"><span>{c.correction}</span><i aria-hidden>↗</i></a>
          <a className="methodology-action" href="https://github.com/Ashuza11/CongoLangAtlas" target="_blank" rel="noreferrer"><span>{c.repository}</span><i aria-hidden>↗</i></a>
        </div>
      </section>
      <footer className="methodology-footer"><p>{c.projectBy} <a href="https://kivulinguaai.org/" target="_blank" rel="noreferrer">KivuLingua AI</a>.</p><Link href={home}>{c.return}</Link></footer>
    </main>
  );
}
