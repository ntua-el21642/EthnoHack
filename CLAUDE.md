# EthnoHack – Track 01 Traditional Knowledge Mining

Track question: *What did centuries of texts know about medicinal plants — and does modern science agree?*
Deadline: pitch (10 min) + working demo, ~24h from 2026-11-06 20:22 Europe/Bucharest. User speaks Greek; answer in Greek.

## Idea (decided)
Evidence-gap prioritisation of leads from Dioscorides, *De materia medica* (Greek).
1. Extract structured recipes from the Greek text: plant, plant part, indication, preparation, mode of administration, source passage (book.chapter).
2. For each plant–indication pair compute: ancient signal; modern research density (Europe PMC, split clinical / total);
   preparation mismatch (ancient preparation vs. preparations tested in modern abstracts – artemisinin precedent, our own hypothesis, novelty not verified);
   safety flags.
3. Output: ranked candidates + per-candidate dossier (Greek passage, translation, preparation to replicate, abstracts with PMIDs).
Wording rule: "no study found" = research gap/opportunity, never "science disagrees".

## Data
- `data/raw/tlg0656.tlg001.1st1K-grc1.xml` – First1KGreek, Wellmann ed., CC BY-SA 4.0 (commit OK).
- `data/gold/staub2016_S2.xlsx` – Staub et al. 2016 (Phytomedicine) Table S2, 5314 uses; Elsevier copyright, GITIGNORED, do not commit.
  Columns: Taxon, Family, Chapter (Matthioli numbering, e.g. I_114), Vernacular, Ailment (Italian), Ailment_interpretation, Part, Mode, Category.
- **Chapter numbers do NOT align** between Staub (Matthioli 1568) and Wellmann beyond the start of each book (e.g. I_114 = Acacia in Staub, κεράτια in Wellmann). Evaluate extractor at pair level
  (genus, Category / Part / Mode) over a whole book, not chapter by chapter. Staub has placeholder taxa "Genus_species_*".
- Not used: Beck translation (copyrighted), eLife 2024 Matthioli table (not needed).

## Code
- `src/parse_dioscorides.py` – XML -> `data/processed/dio_chapters.json` (827 chapters, ~95k words; apparatus stripped).
- `src/europepmc.py` – cached client. Queries restricted to TITLE_ABS (full-text matches are noisy), but then counts are low because papers say "opium"/"morphine" not the plant name:
  needs term expansion (synonyms/MeSH) and relevance check of top abstracts before any count is used as a score.

## Status / next (updated 2026-11-07 ~00:30)
Done: parser; free rule/lexicon extractor (category F1 0.68 / +mode 0.48, 206 genera, 1237 gold pairs; chapter numbers not used);
name->taxon map = manual (Book III) + LSJ lookup (Perseus, CC BY-SA; raw GitHub files downloaded outside repo) with confidence levels (`data/lexicon/taxa_map.json`);
gap table (388 genus x category rows, strict Europe PMC queries, percentile-based status, priority = ancient statements x (1 - modern percentile)); relevance audits in `eval/` (v3: ~54% relevant, 16% irrelevant, judged by Claude only);
preparation-mismatch detector (`src/prep_mismatch.py`, top 60 rows, 22 flagged).
Todo: demo UI (search plant -> ancient passage + prep + evidence + heatmap); human spot-check of the audit; pre-registered retrospective test on known drugs;
README + pitch. Known weaknesses: lexicon extractor (not LLM), mapping of LSJ-only names is medium confidence, indication term lists hand-written,
counts depend on query design (opium/morphine not matched by plant name), audit judge is the author.
Do not use "no study found" as "science disagrees".
