# State of AI in the DRC, 2026: evidence draft for three workstreams

This note proposes material for the paper **State of AI in the Democratic
Republic of Congo 2026: Ecosystem, Capabilities, Applications and Future
Directions**. It covers:

1. AI applications: what has actually been applied;
2. the NLP landscape: languages, datasets, models, tasks, and gaps; and
3. AI infrastructure: data centres, cloud and GPU access, connectivity,
   computing resources, and data availability.

The central question is whether the DRC is moving from consuming AI made
elsewhere to contributing, building, and owning AI infrastructure, data,
research, and applications.

## A note on evidence and terminology

The paper should not use *application*, *pilot*, *model*, and *deployment* as
synonyms. Use the following maturity scale for every case study:

| Level | Meaning | Minimum evidence |
|---|---|---|
| A0 — proposed | A use case, recommendation, or announced project | Public proposal or project description |
| A1 — research prototype | A model or experiment was built and evaluated on research data | Paper, repository, model card, or reproducible results |
| A2 — field pilot | Used with intended users in a real DRC setting for a limited period | Site, dates, users, protocol, and pilot results |
| A3 — operational deployment | In routine organizational use | Named operator, active period, user or transaction evidence, and support process |
| A4 — scaled and independently evaluated | Used across multiple sites or at population scale with externally assessed outcomes | Independent audit, impact results, safeguards, and continuing budget |

Repositories and organizations may describe their own work, but first-party
claims should be labelled as such until independently corroborated. “No public
evidence found” is not the same as “does not exist.”

## 1. AI applications: what has been applied?

### Proposed finding

Public evidence available in 2026 shows an ecosystem dominated by research
prototypes, informal use of general-purpose AI, and early locally designed
products. There are credible Congolese contributions, particularly in language
technology and university research, but very few applications for which public
documentation establishes routine deployment, scale, independent evaluation,
and Congolese ownership of the underlying model and compute. The strongest
conclusion is therefore **early application, not yet broad institutional
adoption**.

### Cases to include

| Domain and case | What the evidence establishes | Maturity | What must not be claimed yet |
|---|---|---:|---|
| Public health, Ibanda Health Zone | A 2026 study combined interviews with 11 health professionals and a review of 56 DRC and African documents. It found informal consumer-generative-AI use but no institutionally implemented clinical AI system in the health zone. Connectivity, paper records, skills, regulation, and governance were major barriers. | A0 / informal individual use | Do not present Ibanda as a clinical-AI deployment or evidence of clinical effectiveness in the DRC. |
| Urban planning, Goma water–energy–food nexus | Researchers combined a survey of 90 households, remote sensing, machine-learning methods, and system-dynamics scenarios to model resource demand through 2050. This is a DRC-grounded analytical application. | A1 | It is not evidence that the City of Goma operates an AI planning system or has implemented the recommended infrastructure. |
| Child labour in artisanal cobalt mining | The 2026 article organizes challenges, data gaps, forecasting possibilities, and AI-driven recommendations for prevention. | A0 | Do not report an operational child-labour prediction system unless a named implementer, dataset, field validation, and safeguarding protocol are located. |
| Congolese-language speech recognition | Published work provides 4.3 hours of labelled Lingala read speech and 741 hours of unlabelled radio audio covering Lingala, Tshiluba, Kikongo, and Congolese Swahili, with public data and code. | A1 | A research corpus and ASR experiment do not by themselves establish production use or national-language coverage. |
| Congolese Swahili–French MT for humanitarian communication | Research evaluated machine translation in a COVID-19 chatbot context. It is evidence of task-specific experimentation for a DRC-relevant variety. | A1, unless field-use evidence is separately verified | Do not equate chatbot-context evaluation with a sustained humanitarian service. |
| Libraries | A mixed-method study of 368 professionals, users, and experts studies the inclusion/exclusion implications of adopting AI in Congolese libraries and highlights structural and digital-divide constraints. | Readiness/adoption study, not deployment evidence | Do not list “AI in libraries” as operational solely from this article. |
| Education and national examinations | AI-supported marking of the state examination has been publicly reported. | Provisional A2/A3, pending primary records | Obtain procurement documents, technical method, subjects covered, years, human appeals, error analysis, data protection assessment, and independent audit before treating it as a national success. |
| SME and cultural platforms | Wanzzo is presented as AI-assisted SME management and finance-readiness software. KwetuBest lists CulturaZik AI and other locally designed digital products. Nodes Technology reports AI automation and training. | First-party product evidence; maturity undetermined | User numbers, active usage, model origin, accuracy, customer outcomes, data governance, and local IP ownership remain to be verified. |

### Additional sectors the fieldwork should test

The literature identifies plausible uses in agriculture, mining, finance,
education, public administration, climate, disaster response, and health. The
paper should only promote a sector from “opportunity” to “application” when it
can name the system, developer, operator, location, dates, users, input data,
model, outcome measure, and present operating status.

For each candidate application, collect these fields:

| Field | Question |
|---|---|
| Problem | What decision or service does the system support? |
| Product and organization | Who built it and who operates it? |
| Status | Proposal, prototype, pilot, operational, scaled, or discontinued? |
| Place and period | In which provinces, facilities, or communities, and since when? |
| Users and scale | Active users, sites, transactions, or decisions per month? |
| Technical system | Locally trained model, adapted open model, API wrapper, rules, or ordinary automation? |
| Data | Origin, consent, language, representativeness, licence, storage, and controller? |
| Compute and hosting | On-device, DRC data centre, regional cloud, or foreign cloud? |
| Ownership | Who owns the data, code, model weights, trademarks, and derived IP? |
| Evaluation | Accuracy plus real-world outcome, baseline, failure modes, and independent evaluator? |
| Safeguards | Human oversight, appeal, security, privacy, bias testing, and incident reporting? |
| Sustainability | Paying customer or public budget, maintenance team, and cost of operation? |

### Interpretation against the research question

These applications show that Congolese researchers and firms are beginning to
select local problems and build or adapt AI artefacts. However, the public
record is much stronger for **experimentation and contribution** than for
**institutional deployment, scale, and ownership**. The paper should therefore
separate four dimensions in its conclusion: local problem definition, local
development, local operation, and local ownership. A project may satisfy one
without satisfying the others.

## 2. NLP landscape: language models and datasets

### Proposed finding

NLP is currently the clearest area in which the DRC is moving beyond pure
consumption. Congolese actors and collaborators have created parallel corpora,
speech datasets, benchmarks, and fine-tuned translation or speech models.
Nevertheless, coverage is sharply unequal, many resources are religious or
synthetic, geographic and variety provenance is often weak, and most compute
and hosting depend on platforms outside the DRC. The result is **growing data
and research contribution without full data, compute, or platform
sovereignty**.

### Evidence already produced by CongoLangAtlas and CongoLangBench

The generated CongoLangAtlas research bundle dated 5 October 2026 provides a
reproducible baseline:

| Indicator | Current value | Interpretation |
|---|---:|---|
| Provisional DRC-associated language profiles | 236 | Inventory coverage, not proof of exact modern speaker geography |
| Curated benchmark tracks | 47 | Languages/varieties with audited bitext tracks |
| Validated processed bitext pairs | 2,233,244 | Aggregate scale; highly uneven between languages and domains |
| Imported resource records before public-card consolidation | 94 | Two resource records per benchmark track in the import layer |
| Public resource cards | 47 | The web bundle consolidates each track into one preferred card |
| Open-download tracks | 21 | Public availability does not by itself establish quality or DRC-specific provenance |
| Gated tracks | 2 | Access and licence conditions require review |
| Unavailable/restricted tracks | 24 | Metadata may be catalogued, but source content cannot be redistributed |
| DRC-labelled tracks | 26 | Source metadata explicitly associates the material with the DRC |
| Cross-border tracks | 14 | Availability does not prove a DRC-specific variety |
| Geographically uncertain tracks | 7 | Provenance remains unresolved |
| Discovery leads | 1,338 | Includes 1,149 provider candidates plus 189 Glottolog catalogue links |
| Hugging Face candidates | 217 | Dataset/model leads requiring human review |
| GitHub candidates | 40 | Repository leads requiring identity and relevance review |
| OpenAlex candidates | 656 | Research leads; ambiguous names create false positives |
| OLAC pages | 236 | One catalogue search page per language profile |

All 47 benchmark tracks remain deferred pending named human approval. The
atlas currently reports zero approved geographic claims. These qualifications
should travel with the counts wherever they appear in the paper.

### Representative resources and models

| Language or group | Resource/model examples | What they demonstrate | Main limitation to record |
|---|---|---|---|
| Nande / Kinande / Yira | Nande–French corpora of about 14.5k and 26.2k pairs; Kinande speech subset of 8.15 hours and 2,871 clips; reported T5 baselines | Local parallel-data and speech creation plus model adaptation | Naming, dialect, orthography, speaker geography, and exact model evaluation must not be collapsed across Nande/Kinande/Yira |
| Tshiluba | 11.24 hours and 3,532 AfriSpeech clips; public Tshiluba–English and Tshiluba–French NLLB fine-tunes; synthetic coding-dialogue dataset | Speech collection and adaptation of a 600M multilingual MT base model | Bible-domain training, independent evaluation, synthetic-data quality, and distinction from Kiluba |
| Lingala | 4.3 hours labelled read speech; radio audio within the 741-hour corpus; LiSTra English–Lingala speech translation; SSA-MTE French–Lingala evaluation; Belebele | Speech, speech translation, MT evaluation, and comprehension benchmarking | Small labelled speech set; benchmark coverage is not DRC cultural or factual coverage |
| Kikongo / Kikongo ya Leta / Kituba | Radio audio, Kituba speech subsets, Google SMOL Kituba (DRC), and a gated generic Kikongo configuration | Emerging text and speech coverage | The collective “Kikongo” label must not erase Koongo varieties or be merged automatically with Kikongo ya Leta/Kituba |
| Congo Swahili | Gamayun parallel data, radio audio, humanitarian MT research | DRC-relevant language technology with a concrete public-interest use case | Must distinguish Congo Swahili from generic or East African Swahili data and evaluations |
| Shi / Mashi | French–Shi parallel corpus of roughly 31.9k pairs and an audited DRC Bible edition | Contribution for an eastern DRC language | Cross-border identity, domain narrowness, provenance, and quality need continued review |
| Long tail of DRC languages | CongoLangBench covers 47 tracks; the atlas exposes 236 profiles even when no usable NLP resource is verified | Makes absence visible instead of equating “not indexed” with “not a language” | Most languages still lack balanced, consented, reusable text and speech data or evaluated models |

### Tasks to map in the paper

Adapting the structure of the Kenya survey and the 2025 African NLP landscape
review, build a DRC task-by-language matrix for:

- machine translation and parallel text;
- automatic speech recognition and speech translation;
- text-to-speech;
- language identification;
- information retrieval and question answering;
- sentiment and social-media analysis;
- named-entity recognition and information extraction;
- summarization;
- spelling, morphology, tokenization, and keyboards;
- OCR and document digitization;
- safety, toxicity, misinformation, and bias evaluation; and
- culturally grounded LLM evaluation.

For every dataset or model, record language name, ISO 639-3 code, Glottocode,
variety, orthography, collection location, speaker demographics where
consented, modality, domain, human/synthetic status, size, split, deduplication,
licence, access, version, creator location, funding, hosting, and evaluation.

### Analytical points to make

1. **Language count is not capability.** A multilingual model listing Lingala
   or Swahili does not prove useful performance, Congolese-variety coverage, or
   local cultural knowledge.
2. **Rows are not quality.** Large synthetic or translated corpora can contain
   artifacts and cannot replace human-authored, community-reviewed data.
3. **Religious corpora are important but narrow.** They support bootstrapping
   while creating domain and register bias.
4. **Cross-border languages need provenance.** Bemba, Alur, Lunda, Fuliiru,
   Kakwa, and others require country-, place-, and variety-level labels.
5. **Open hosting is not local ownership.** Hugging Face and GitHub improve
   visibility, but governance, compute, and platform control remain external.
6. **Community review is a core capability.** Speakers should participate in
   naming, consent, validation, error analysis, access rules, and benefit
   sharing—not only annotation.

### NLP indicators for annual tracking

Report both totals and the distribution across languages:

- number and percentage of DRC languages with any verified digital resource;
- number with reusable text, parallel text, labelled speech, dictionaries,
  grammars, OCR data, keyboards, benchmarks, and model cards;
- median dataset size, not only total size;
- percentage with clear licences, consent/provenance statements, DRC-specific
  collection evidence, and community review;
- number of models led by DRC-based authors or institutions;
- percentage of model weights and training code openly released;
- number evaluated on fixed, contamination-checked, DRC-specific test sets;
- number supporting offline or low-resource inference; and
- share of funding, compute, data rights, and IP held by Congolese entities.

## 3. AI infrastructure

### Proposed finding

The DRC has begun to acquire the general digital substrate required for AI,
but public evidence does not yet establish a national AI-compute layer. The
opening of a modern carrier-neutral data centre is important for reliable local
hosting and lower latency. It does not establish the availability of GPUs,
affordable research compute, a domestic hyperscale cloud region, or Congolese
ownership of the facilities and platforms on which AI workloads run. Low
internet and electricity access also make infrastructure inequality a national
AI constraint rather than a secondary ICT issue.

### Data centres and hosting

Raxio states that DRC1 opened in Kinshasa in August 2024 following a USD 30
million investment. The operator describes a Tier III Uptime-certified,
carrier-neutral facility spanning 1,542 square metres, with capacity for up to
400 racks and 1.5 MW of IT power. This is credible evidence of operational
colocation capacity and an improved foundation for local hosting.

The paper must immediately add three caveats:

1. The facility specification is an operator-reported claim and should be
   cross-checked against the Uptime Institute certificate and customer data.
2. Colocation capacity is not an AI cluster: no public inventory was located
   showing GPU type, count, interconnect, storage throughput, utilization, or
   prices available to Congolese researchers and startups.
3. Hosting in the DRC is not automatically sovereign: ownership, operator
   control, data-controller roles, backup location, cloud contracts, applicable
   law, and dependency on foreign hardware/software must be separately mapped.

Recommended data-centre table fields are facility, city, operator, beneficial
owner, operating status, certification, IT load, rack count, power sources and
backup, network carriers, cloud on-ramps, public-sector tenants, GPU services,
data residency terms, pricing, and independent verification date.

### Cloud and GPU access

The current evidence supports a cautious statement: Congolese developers can
use foreign-hosted cloud platforms and public model repositories, but this is
not equivalent to affordable, locally controlled compute. The paper should not
claim “there are no GPUs in the DRC.” It should state that **no comprehensive
public inventory of research or commercial AI accelerators was located**.

The field survey should ask universities, laboratories, telecom operators,
data centres, startups, banks, mining firms, and government agencies for:

- accelerator vendor/model, count, memory, interconnect, and acquisition year;
- location, owner, operator, and eligible users;
- queue time, utilization, uptime, and power interruptions;
- hourly or project cost and availability of academic credits;
- storage capacity, backup, cybersecurity, and data-residency conditions;
- cloud vendor and region actually used;
- foreign-currency and payment barriers;
- workloads trained locally versus fine-tuned or inferred through an API; and
- procurement, maintenance, cooling, and hardware-replacement arrangements.

This lets the paper distinguish **access** from **ownership** and distinguish
an API-based product from a locally trained model.

### Connectivity

The World Bank indicator series reports that 19.67% of the DRC population used
the internet in 2024, the latest non-null observation in the series retrieved
for this draft. This national average conceals urban/rural, gender, income,
conflict, disability, and provincial gaps. For AI, the relevant measures are
not only population coverage but also actual adoption, affordability, latency,
international capacity, outage frequency, and the ability to upload speech,
image, or geospatial datasets.

Add the following connectivity indicators:

- population covered by 3G, 4G, and 5G versus active users;
- fixed and mobile broadband subscriptions per 100 people;
- median download/upload speed and latency by province;
- cost of 1 GB and of an entry-level device as a share of monthly income;
- kilometres and ownership of national fibre, cross-border links, and
  redundancy;
- internet-exchange traffic kept local;
- school, university, hospital, and research-lab connectivity; and
- outage data, especially in conflict-affected and rural areas.

### Electricity and physical reliability

The World Bank series reports electricity access for 22.5% of the population
in 2024. Reliable AI services need more than a nominal grid connection: data
centres and labs require continuous power quality, cooling, backup generation,
fuel logistics, and equipment maintenance. The paper should therefore combine
the national access rate with facility-level measures: hours of outage,
effective cost per kWh, generator dependence, renewable share, power-usage
effectiveness, and the carbon and water footprint of computing.

### Data availability as infrastructure

Data should be treated as infrastructure rather than merely an input to a
model. CongoLangAtlas demonstrates both emerging capability and the scale of
the deficit: it provides structured metadata for 236 language profiles, 739
geographic leads, and 1,338 discovery leads, but all 47 audited NLP tracks and
all mapped geographic claims still require named-human approval. It also shows
why a repository count can mislead: 24 of 47 tracks are unavailable or
restricted for corpus reuse, 14 are cross-border, and seven have uncertain
geographic scope.

The national data-infrastructure inventory should cover:

- census, civil registration, health, education, agriculture, weather,
  geological, transport, company, procurement, and administrative data;
- spatial and temporal coverage, update cadence, missingness, and machine
  readability;
- controller, custodian, storage location, access procedure, and retention;
- licence, personal-data basis, consent, safeguards, and permitted reuse;
- interoperability standards, identifiers, documentation, and APIs;
- language and provincial representation;
- public, research-only, commercial, restricted, or unavailable status; and
- locally governed repositories, persistent identifiers, and preservation.

### Infrastructure scorecard to add to the paper

| Layer | Evidence in 2026 | Ownership test | Current assessment |
|---|---|---|---|
| Data-centre colocation | Operational Tier III facility publicly documented in Kinshasa | Who owns and operates it, and under which contracts/law? | Emerging |
| National AI compute | No public national GPU inventory or shared national research-compute service located | Are accelerators physically in the DRC and allocable to local institutions? | Not demonstrated |
| Cloud | Foreign cloud/API access is available to connected organizations | Where are workloads and data hosted, and who sets price and access? | Accessible but externally dependent |
| Connectivity | Internet use reached 19.67% in 2024 in the cited World Bank series | Who owns backbone and exchange infrastructure, and who is excluded? | Major constraint |
| Power | Electricity access reached 22.5% in 2024 in the cited World Bank series | Can facilities obtain reliable, affordable, maintainable power? | Major constraint |
| Research data | Strong emerging language-data contribution; fragmented administrative and sectoral data | Are governance, licences, repositories, and benefits locally controlled? | Emerging but uneven |
| Standards and audit | CongoLangAtlas provides a concrete evidence and provenance workflow | Can this approach be institutionalized across sectors? | Early capability |

## Cross-cutting conclusion for the paper

The evidence supports a qualified transition. The DRC is no longer only an AI
consumer: Congolese researchers, communities, and firms are producing language
datasets, adapting models, publishing locally grounded studies, and designing
applications. Yet the transition is incomplete. The strongest evidence is for
**contribution and experimentation**; the weakest is for **scaled deployment,
independent impact evaluation, domestic compute ownership, durable financing,
and control of high-value data and intellectual property**.

A useful 2030 test is therefore not “How many AI projects exist?” but:

> How many systems addressing Congolese priorities are locally governed,
> trained or meaningfully adapted on lawful and representative data, operated
> on affordable infrastructure, independently evaluated, sustainably financed,
> and accountable to the communities affected by them?

## Suggested figures and tables

1. **Application maturity matrix:** sectors on rows and A0–A4 maturity on
   columns, showing the highest verified level for each case.
2. **NLP coverage heat map:** 236 languages by resource/task type, with separate
   markers for verified, candidate, restricted, cross-border, and synthetic
   resources.
3. **Resource inequality chart:** dataset-size distribution across the 47
   CongoLangBench tracks; report median and quartiles alongside the 2.23 million
   aggregate.
4. **AI infrastructure stack:** power → connectivity → data centres/cloud/GPU →
   data → models → applications, with ownership at every layer.
5. **Builder/owner scorecard:** for each case, score local problem definition,
   team, data rights, model/IP, compute, operation, funding, and governance.

## Core sources

- Alabi, J. O., Hedderich, M. A., Adelani, D. I., & Klakow, D. (2025).
  [Charting the Landscape of African NLP: Mapping Progress and Shaping the Road
  Ahead](https://aclanthology.org/2025.emnlp-main.1414/). The survey analyzes
  884 African-NLP papers published over five years.
- Amol, C. J., et al. (2024). [State of NLP in Kenya: A
  Survey](https://arxiv.org/abs/2410.09948). Used here as a country-survey
  structural reference, not as evidence about the DRC.
- UNESCO (2026). [Rapport d'évaluation de la préparation à l'intelligence
  artificielle — République démocratique du
  Congo](https://unesdoc.unesco.org/ark:/48223/pf0000396494), CC BY-SA 3.0 IGO.
- Karemere, H., et al. (2026). [Opportunities and barriers to implementing
  artificial intelligence for public health in the Democratic Republic of
  Congo](https://link.springer.com/article/10.1186/s12913-026-15492-0).
- [Urban–artificial intelligence and system dynamics modelling of the
  water–energy–food nexus in
  Goma](https://link.springer.com/article/10.1007/s41207-025-00863-6) (2025).
- Lee, M. (2026). [Forecasting and Preventing Child Labor in Artisanal Cobalt
  Mining in the
  DRC](https://doi.org/10.36838/ijhsr813.64).
- [Problématique de l'intelligence artificielle sur les bibliothèques en
  République démocratique du
  Congo](https://revuestest.imist.ma/index.php/JIS/article/view/59078).
- Raxio Group (2024). [DRC inaugurates USD 30 million Raxio data
  centre](https://www.raxiogroup.com/drc-inaugurates-30-million-raxio-data-centre-to-catalyse-digital-economy/).
- World Bank. [Individuals using the Internet (% of population),
  DRC](https://api.worldbank.org/v2/country/COD/indicator/IT.NET.USER.ZS?format=json)
  and [access to electricity (% of population),
  DRC](https://api.worldbank.org/v2/country/COD/indicator/EG.ELC.ACCS.ZS?format=json).
- CongoLangAtlas. [Data readiness](DATA_READINESS.md), [verification
  policy](VERIFICATION_POLICY.md), and [CongoLangBench import
  notes](CONGOLANGBENCH_IMPORT.md).
- Ashuza. [AI in the Democratic Republic of the
  Congo](https://github.com/Ashuza11/Ai-in-drCongo).

## Claims that still require primary-source follow-up

- the exact status and audit trail of AI-supported state-examination marking;
- an institution-by-institution GPU and research-compute inventory;
- cloud regions, local points of presence, customer prices, and data-residency
  terms actually available in the DRC;
- independent usage and impact evidence for Congolese startup products;
- operational AI systems in agriculture, mining, finance, government, or
  climate beyond proposals and research prototypes;
- dataset consent, provenance, licence, dialect, and community-review records;
  and
- interviews with system users, affected communities, maintainers, regulators,
  telecom operators, data-centre operators, and university laboratories.
