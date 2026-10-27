# Federated inference, evidence weighting and institutional standing

## Source identities

Friston, Karl J., Thomas Parr, Conor Heins, Axel Constant, Daniel Friedman, Takuya Isomura, Chris Fields, Tim Verbelen, Maxwell Ramstead, John Clippinger and Christopher D. Frith. **Federated inference and belief sharing.** *Neuroscience and Biobehavioral Reviews* 156 (January 2024), 105500. Published online 5 December 2023. DOI [10.1016/j.neubiorev.2023.105500](https://doi.org/10.1016/j.neubiorev.2023.105500); PMID [38056542](https://pubmed.ncbi.nlm.nih.gov/38056542/); PMCID PMC11139662. No issue number is supplied. The successful full-text retrieval is the [EuropePMC JATS endpoint](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11139662/fullTextXML), whose license text names CC BY 4.0. The initial PMC web page returned a recaptcha.

Friedman, Daniel Ari. **Robust Belief Sharing in Federated Active Inference: A Recovery-Tested Generalized-Variational Framework for Categorical Contamination-Aware Consensus.** Zenodo, version 1.1.0, 19 September 2026. Version-specific DOI [10.5281/zenodo.22149133](https://zenodo.org/records/22149133); distinct concept DOI 10.5281/zenodo.21864003. The record is catalogued as software and contains one 90-page manuscript PDF. The record's MIT-license field should not be silently expanded into a separate blanket PDF/figure-rights claim. The [official API](https://zenodo.org/api/records/22149133) and [deposited PDF](https://zenodo.org/api/records/22149133/files/active_fedference_combined.pdf/content) were successfully downloaded after initial web-tool failures.

## Technical distinctions used in the manuscript

Friston et al. §3.1, Eqs. 6–8 and Figs. 3–5 provide the direct comparison: observers communicate beliefs about common latent states in a common reference frame; likelihood mappings express content and confidence; identity/permutation mappings align the required meanings. Agents exclude their own messages, and the simultaneous exchange uses predictions grounded in earlier observations. These details make representation, translation, confidence and independence part of a communication mechanism rather than a general synonym for political agreement.

The robust framework separates local updating from server aggregation. Section 5.7 gives the local robust-loss route. Sections 5.8–5.9 distinguish a fixed-weight logarithmic pool, a divergence-reweighted heuristic and a separate objective-backed variational aggregator. Under finite positive common support, posterior-log-potential inputs and fixed weights, Theorem 5 and Corollary 6 identify a categorical specialization of Friston's Eq. 7 combination term. Setting server robustness to zero returns the project's own logarithmic pool. This recovers a defined mathematical limit, not every source message-construction, self-exclusion, scheduling or generative-model component. The raw primary text at physical PDF 16–19 (printed 15–18) was independently read by root.

The claim ownership remains separate: bounded local losses have their stated source assumptions; heuristic aggregation has a recovery identity and conditional contamination contrasts; the variational route has its own objective/descent and raw-effective-weight properties. A decrease of that objective and correct inference in a declared contamination experiment answer different questions. The new manuscript does not reproduce either paper's numerical experiments or import their measurements as new project results.

## Institutional construction and visual use

The substantive connection is to keep a report's evidential contribution distinct from the author's standing, provision and access to review. A disagreement can challenge a report within agreed categories or challenge the categories and jurisdiction themselves. The existing classification-decision record can name the grounds for a reliability judgment and a route for reopening it. The proposed body diagram aligns these records; its institutional connections are this manuscript's construction. It does not depict political actors as interchangeable compute nodes or infer an institutional mandate from a high-confidence consensus.

The main-text integration is deliberately concise: three new paragraphs before the CRR section and a focused addition to the final computational discussion. The conceptual body figure contains no borrowed quantitative curve. Its caption cites the source mechanisms and identifies the institutional construction. The existing notation table and sixteen formal blocks/eleven equations do not acquire new mathematical symbols or new theorem claims.

## Reading record

The scholarship ledger contains 49 entries, including two selected-full-text readings added in 0.12.0. Exact locators, source URLs, private cache paths and SHA-256 appear in `research/scholarship-reading-0.12.0.json`. The original 47 entries retain their reading status. The official metadata and full source bodies are stored under ignored `local_data/research/v0.12.0`; they are excluded from release assets.

The Friston journal year is 2024, with online publication in December 2023. The Zenodo citation names version 1.1.0 and its version DOI 22149133, separately from concept DOI 21864003. Neither selected reading is credited as a complete paper, complete supplement or replication.
