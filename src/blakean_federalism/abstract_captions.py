# Copyright (c) 2026 Daniel Ari Friedman
"""Captions explain the question, evidence and operations used in each opening figure."""

from .abstract_analysis import corpus_diagnostics, repair_diagnostics
from .abstract_explanation import display_frequency, top_family_examples
from .analysis_figures import FOCUS
from .models import ResearchError
from .publication_profiles import ANALYTICAL_PRODUCERS
from .workbench_models import Workbench


def uses_analytical_abstracts(report: Workbench) -> bool:
    return report.producer_version in ANALYTICAL_PRODUCERS and any(
        a.asset_id == "J1" for a in report.images
    )


def cover_caption() -> str:
    return (
        "The illustrative network makes two overlaps visible: person p2 participates in both "
        "national formations, and both formations draw on state reading s2. Red outlines highlight "
        "these overlaps. Solid links record "
        "affiliation A; dashed links record interpretation I. Neither supplies competence C "
        "for institution J to impose decision D. The lower rows distinguish these domains. "
        "Accessible reasons, support for changing affiliation and limits on total identity "
        "claims state the political requirements developed in the article. Milton 32 separates "
        "enduring persons from changing states; Marriage 7 values time's productions. The "
        "uncropped Jerusalem frontispiece places a bearer, lamp and threshold beside this argument."
    )


def analytical_captions(report: Workbench) -> tuple[str, str, str, str]:
    stats, experiment = report.corpus_statistics, report.institutional_experiments
    if stats is None or experiment is None:
        raise ResearchError("publication_statistics", "Abstract captions require analytical inputs")
    queries = {q.query_id: q for q in corpus_diagnostics(stats, FOCUS)}
    repairs = repair_diagnostics(experiment)
    failing, bounded = repairs.baseline_failing, repairs.baseline_admissible
    unique = sum(bool(c.baseline_failed_rules) and c.unique_minimal_bundle for c in repairs.cases)
    catalog_size = len(experiment.catalog)
    check_count = len(
        {state.code for row in experiment.decisions for state in row.baseline_rule_states}
    )
    structure = (
        (
            f"Each of the {unique} failing records has one smallest repair bundle. Every passing "
            f"selection contains it: with minimum size $m(d)$, "
            f"there are $2^{{{catalog_size}-m(d)}}$ "
            "passing selections. "
        )
        if unique == failing.decisions and unique
        else (
            "The table names changes common to every passing selection; alternative minimal "
            "bundles remain explicit in the analytical data. "
        )
    )
    scholarly = (
        "Read each card from Blake's scene through its tension to the question developed here. "
        "Los seeks to deliver individuals from systems while his own making involves coercion. "
        "Clark's attention to dramatic speakers and White's reading of a priori construction "
        "prevent the maker's independence from settling the freedom of those inside the work "
        "[@clark1995Birenbaum, pp. 69-70; @white2005Science, pp. 116-117]. "
        "Mutual creation raises the distribution of agency within a national form "
        "[@fallon2015, ms. pp. 10-12; @mellor1982, pp. 148-153; "
        "@kaplan1996Patriarchy, p. 82, n. 27]. "
        "The lion and ox expose unequal burdens under one rule; the Angel's compelled vision "
        "complicates an endorsement of opposition. Los's question asks where protection directs "
        "its force; the released family's backward glance asks what dependence survives release. "
        "The institutional questions concern standing, effective challenge, continuing provision "
        "and supported exit [@heppner1983Adultery, pp. 55-56,59; @frosch1979Composite, p. 44; "
        "@simpson2007, pp. 67-78; @fraser1992PublicSphere, pp. 122-124; "
        "@shachar2005, pp. 75-77; @moyer2014Cotton, paras. 3-10,14-16]. "
        "Q38 and Q39 select complete lines from longer main-text quotations. "
        "The final column states this article's institutional construction."
    )
    repair = (
        (
            f"The hypothetical comparison has {failing.decisions} failing and "
            f"{bounded.decisions} already-passing "
            f"starting records. "
            f"The displayed failing records name the changes "
            f"required in every passing combination; "
            f"MIN is the fewest changes. Passing means satisfying the {check_count} stipulated "
            f"safeguards. All subsets of {catalog_size} declared field interventions are examined, "
            f"giving {1 << catalog_size:,} labelled combinations per alternative. "
        )
        + structure
        + (
            f"The bar separates {bounded.admissible_subsets:,} passing selections from already-"
            f"passing starts, {failing.admissible_subsets:,} after repair of failing starts, and "
            f"{repairs.total_subsets - repairs.total_admissible_subsets:,} still failing. "
            f"Thus failing starts contribute "
            f"{failing.admissible_subsets:,}/{failing.subset_count:,}; "
            f"all starts contribute "
            f"{repairs.total_admissible_subsets:,}/{repairs.total_subsets:,}. "
            f"The {repairs.total_subsets:,} labelled selections produce "
            f"{repairs.total_distinct_states} distinct within-case records, "
            f"because selecting another "
            "intervention need not change another field. The independent upper-set calculation "
            "reconciles every size bin with the saved predicate experiment. The four-box "
            "route distinguishes selecting field changes, applying them, checking every "
            "safeguard and recording the result. These are enumerated possibilities "
            "rather than empirical probabilities. Persons, actions, "
            "resources, affected populations and treaty triggers stay fixed."
        )
    )
    states, particulars, imagination = (
        queries[key] for key in ("states", "particulars", "imagination")
    )
    variants = {query.query_id: query.variants for query in stats.query_specs}
    examples = top_family_examples(stats, "imagination")
    example_text = " ".join(
        (
            f"The retained {row.title} family supplies {row.matches} imagination matches "
            f"in {row.words:,} words "
            f"({display_frequency(row.per_10000_words)} per 10,000)."
        )
        for row in examples
    )
    deletion = (
        (
            f"Omitting {', '.join(states.loo_min_family_ids)} gives the lowest "
            f"state/states deletion "
            f"frequency, {states.loo_min_rate:.3f} per 10,000. "
            "Deletion removes both matches and words. "
        )
        if states.loo_min_rate is not None
        else "No one-family deletion leaves a positive-word denominator. "
    )
    concentration = (
        (
            f"The particulars group occurs in {particulars.matched_families} families; "
            f"{particulars.top_family_occurrences} of {particulars.occurrences} matches are in "
            f"{', '.join(particulars.top_family_ids)}. "
        )
        if particulars.top_family_share is not None
        else "The particulars group has no recorded matches. "
    )
    corpus = (
        (
            f"The table counts the printed literal word forms in {stats.primary_source_units} "
            f"primary extracts containing {stats.primary_tokens:,} Unicode word tokens, "
            f"grouped into "
            f"{stats.primary_work_groups} recorded source families. "
            f"Matching is case-insensitive and "
            f"uses whole words. The second row groups {', '.join(variants['persons'])} "
            "under the query ID persons. "
            f"For {', '.join(variants['states'])}, {states.occurrences:,} matches divided "
            f"by {states.tokens:,} words "
            f"and multiplied by 10,000 gives {display_frequency(states.pooled_rate)}. "
            "'All words' combines every retained match and word. "
            "'Each family' calculates a frequency "
            "inside each positive-word family and averages those frequencies, including families "
            "with no matches. The family fraction counts groups with at least one match. "
        )
        + concentration
        + (
            f"Imagination changes from {display_frequency(imagination.pooled_rate)} to "
            f"{display_frequency(imagination.equal_family_rate)} under equal weighting. "
        )
        + example_text
        + " Each family receives the same weight despite different text lengths. "
        + deletion
        + (
            "Copies remain retained; family grouping does not assume independent works. These "
            "comparisons locate passages and source dependencies for close reading. "
            "The final inset gives the minimum and maximum remaining frequency after "
            "omitting one source family, with the pooled frequency marked as a point. "
            "Both inset plots use one frequency scale; deletion removes matches and words."
        )
    )
    return cover_caption(), scholarly, repair, corpus
