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

## Status / next
Done: parser, Europe PMC client (live OK), scaffold pushed.
Todo: (1) LLM extractor with fixed JSON schema, run on Book III first (most uses in Staub); (2) F1 vs Staub at pair level;
(3) Greek name -> taxon via GBIF (check Wikidata SPARQL, OpenAlex needs mailto: 429 without); (4) evidence layer + preparation-mismatch detector;
(5) retrospective test on a pre-registered list of known plant-derived drugs; (6) demo UI (search plant -> claims + evidence + heatmap); (7) README + pitch.
Manual check of 30 evidence judgements for accuracy; report it.

## Environment notes
Cloud sandbox network is allowlisted: Europe PMC, PubMed, ChEMBL, GBIF OK. Subagents for batch extraction need the user's explicit OK (usage cost) – not yet given.
Git commit trailers: Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com> + Claude-Session link.
