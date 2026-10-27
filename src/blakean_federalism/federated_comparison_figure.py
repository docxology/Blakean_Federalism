# Copyright (c) 2026 Daniel Ari Friedman
"""Conceptual alignment without transferring technical success into political warrant."""

from reportlab.pdfgen.canvas import Canvas

from .figure_style import BLACK, GREY, MUTED, RED, line, text


def draw_federated_comparison(c: Canvas) -> None:
    """Draw an original, nonquantitative two-lane comparison of record requirements."""
    text(c, "Shared inference; accountable authority", 20, 431, 500, 19)
    text(
        c,
        "Technical records specify evidence; institutional records specify powers and remedies.",
        20,
        400,
        500,
        9,
    )
    line(c, 20, 378, 520, 378, RED, 1.5)
    text(c, "INFERENCE INFRASTRUCTURE", 20, 365, 225, 10)
    text(c, "INSTITUTIONAL AUTHORITY", 295, 365, 225, 10, RED)
    rows = (
        (
            336,
            "Shared latent categories / reference frame",
            "Which variables and meanings are aligned?",
            "Standing / provision",
            "Who can appear, refuse a classification and retain essential provision?",
        ),
        (
            259,
            "Confidence-bearing reports / self-exclusion",
            "What confidence is reported, and whose own message is excluded?",
            "Specific-act warrant / reach",
            "Who may decide this act, over whom, on which reviewable warrant?",
        ),
        (
            182,
            "Local updating / server combination",
            "Client robust loss; server: log pool, reweighted heuristic or variational objective.",
            "Effective challenge / revised forum",
            "Who can change the act or its reviewing forum while provision persists?",
        ),
    )
    for top, technical, question, political, challenge in rows:
        text(c, technical, 20, top, 225, 11)
        text(c, question, 20, top - 34, 225, 9, MUTED)
        text(c, political, 295, top, 225, 11, RED)
        text(c, challenge, 295, top - 34, 225, 9, MUTED)
        line(c, 20, top - 68, 520, top - 68, GREY, 0.6)
    line(c, 270, 118, 270, 367, GREY, 1)
    text(c, "Changing evidential weight must not erase a person's standing.", 20, 104, 500, 11, RED)
    text(
        c,
        "Outward agreement can coexist with effective review or dependency; compare the routes.",
        20,
        82,
        500,
        9,
    )
    text(
        c,
        "Friston et al. 2024, §3.1, Eqs.6-8 · Robust Belief Sharing 1.1, §5.8",
        20,
        59,
        500,
        8,
        BLACK,
    )
    text(
        c,
        """Zero robustness recovers the specified log pool; shared-support conditions
identify its Eq.7 message-combination term.""",
        20,
        43,
        500,
        8,
        MUTED,
    )
