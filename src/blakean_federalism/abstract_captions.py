# Copyright (c) 2026 Daniel Ari Friedman
"""Explanatory captions tied to the current abstract figures and recomputed summaries."""

from .abstract_analysis import corpus_diagnostics, repair_diagnostics
from .analysis_figures import FOCUS
from .models import ResearchError
from .workbench_models import Workbench


def uses_analytical_abstracts(report: Workbench) -> bool:
    return report.producer_version == "0.14.0" and any(a.asset_id == "J1" for a in report.images)


def cover_caption() -> str:
    return (
        "Three illustrative persons participate in two national formations that articulate three "
        "poetic states. Solid lines encode affiliation A; dashed lines encode interpretation I. "
        "Neither relation establishes an institution's competence C to impose a decision D. "
        "The lower rows distinguish these warrants and identify translation, passage and "
        "non-exhaustion as institutional requirements. Jerusalem's frontispiece places the "
        "relations beside a bearer, lamp and threshold. The network is a conceptual example; "
        "Blake's enduring persons and time's productions are quoted from Milton 32 and Marriage 7."
    )


def analytical_captions(report: Workbench) -> tuple[str, str, str, str]:
    stats, experiment = report.corpus_statistics, report.institutional_experiments
    if stats is None or experiment is None:
        raise ResearchError("publication_statistics", "Abstract captions require analytical inputs")
    queries = {q.query_id: q for q in corpus_diagnostics(stats, FOCUS)}
    repairs = repair_diagnostics(experiment)
    failing = repairs.baseline_failing
    bounded = repairs.baseline_admissible
    unique = sum(bool(c.baseline_failed_rules) and c.unique_minimal_bundle for c in repairs.cases)
    n = len(experiment.catalog)
    structure = (
        (
            f"All {unique} failing cases have one inclusion-minimal repair bundle. "
            "Their admissible "
            f"subsets are exactly its supersets: with minimum size $m(d)$, the count is "
            f"$2^{{{n}-m(d)}}$. "
        )
        if unique == failing.decisions and unique
        else (
            "The matrix marks operators present in every admissible subset; alternative "
            "minimal bundles "
            "remain explicit in the analytical data. "
        )
    )
    states, particulars, imagination = (
        queries[k] for k in ("states", "particulars", "imagination")
    )

    def rate(value: float | None) -> str:
        return "N/A" if value is None else f"{value:.3f}"

    scholarly = (
        "Six selected lines connect poetic scenes, attributed scholarly arguments and the "
        "institutional tests developed here. The person/state distinction is read alongside "
        "particularity and persistent identity [@damrosch1980, pp. 15-21; @lee2026, pp. 1-10]. "
        "Mutual creation is placed beside national incorporation and disputes about gendered "
        "agency [@fallon2015, ms. pp. 10-12; @mellor1982, pp. 148-153; @kaplan1996Patriarchy, "
        "p. 82, n. 27]. "
        "The lion/ox maxim asks how equal standing can require differentiated provision; "
        "opposition raises the power to challenge a common interpretation. Los's restraint and "
        "the released family's backward glance connect review to the distribution of harm and "
        "the practical means of release. The shortened Q38 and Q39 cells show single identified "
        "lines from the longer main-text quotations. Read each row across; the institutional "
        "column is this article's construction, with refusal, collective opposition, review and "
        "labor supplying different tests [@simpson2007, pp. 67-78; @fraser1992PublicSphere, "
        "pp. 122-124; "
        "@shachar2005, pp. 75-77; @moyer2014Cotton, paras. 3-10,14-16]."
    )
    repair = (
        (
            f"An exhaustive comparison of {n} declared field interventions "
            f"across {len(repairs.cases)} "
            "hypothetical decision records. Each filled dot marks an essential intervention; "
            "MIN is "
            "the smallest admissible bundle. A dash records absence from the essential set, not an "
            "unmeasured value. "
        )
        + structure
        + (
            f"The partition bar separates {bounded.admissible_subsets:,} admissible subsets from "
            f"already-admissible baselines, {failing.admissible_subsets:,} from failing baselines, "
            f"and {repairs.total_subsets - repairs.total_admissible_subsets:,} subsets that still "
            f"fail. "
            f"Thus the failing-baseline denominator is {failing.subset_count:,}, while the whole "
            f"comparison contains {repairs.total_subsets:,} labelled subsets. There are "
            f"{repairs.total_distinct_states} distinct within-case records in total: many operator "
            "choices leave the same fields unchanged. The independent upper-set calculation "
            "reconciles every cardinality bin with the saved predicate experiment. These are exact "
            "combinatorial descriptions of the specified records. Persons, actions, resources, "
            "affected populations and treaty triggers remain fixed while the listed fields change."
        )
    )
    corpus = (
        f"Eight declared lexical groups in {stats.primary_source_units} primary reading extracts, "
        f"{stats.primary_work_groups} recorded source families and {stats.primary_tokens:,} "
        f"Unicode "
        "word tokens. Red points divide the equal-family mean rate by the pooled rate; the "
        "vertical reference at 1 preserves the pooled baseline. Grey spans divide the minimum "
        "and maximum one-family-deletion rates by that same baseline. The spans describe "
        "finite-collection sensitivity, not sampling uncertainty. Exact pooled and equal-family "
        "rates per 10,000 tokens and the leading family's occurrence share appear at right. "
        f"Particulars has {particulars.top_family_occurrences}/{particulars.occurrences} "
        f"occurrences "
        f"in {', '.join(particulars.top_family_ids)} and appears in {particulars.matched_families} "
        f"families; its rate changes from {rate(particulars.pooled_rate)} to "
        f"{rate(particulars.equal_family_rate)}. "
        f"Imagination moves from {rate(imagination.pooled_rate)} to "
        f"{rate(imagination.equal_family_rate)}. "
        f"For states, omitting {', '.join(states.loo_min_family_ids)} gives the minimum "
        f"deletion rate, {rate(states.loo_min_rate)}, although {', '.join(states.top_family_ids)} "
        "has the largest count. Counts, source length and family weighting therefore answer "
        "different questions. Zero-hit positive-token families remain in the equal-family mean."
    )
    return cover_caption(), scholarly, repair, corpus
