# Copyright (c) 2026 Daniel Ari Friedman
"""Generate both figure captions from the exact timing selection and summary."""

from .institutional_review_models import ReviewInput
from .review_timing import RESIDENT
from .review_timing_models import TimingCell, TimingFigureData, TimingSummary


class TimingCaptions(ReviewInput):
    readiness: str
    protection: str


def _band_label(cell: TimingCell) -> str:
    band = cell.configuration.band
    return "absent" if band is None else f"[{band.starts_hour},{band.ends_hour})"


def _resident_gap(cell: TimingCell) -> str:
    person = next(p for p in cell.review.claimants if p.claimant_id == RESIDENT)
    return " and ".join(f"[{start},{end})" for start, end in person.uncovered_intervals) or "empty"


def timing_captions(summary: TimingSummary, data: TimingFigureData) -> TimingCaptions:
    """Derive every count from the actual complete run and its declared figure selection."""
    cells = {str(c.configuration.configuration_id): c for c in data.timeline_cells}
    initial = cells["T.original-duty.r20.a06.automatic.s13.e20"]
    terminal = cells["T.original-duty.r20.a06.automatic.s12.e19"]
    automatic = cells["T.early-threat.r20.a06.automatic.s03.e20"]
    filing = cells["T.early-threat.r20.a06.on_filing.s03.e20"]
    response = len({c.configuration.response_hour for c in data.readiness})
    readiness = len({c.configuration.resident_ready_hour for c in data.readiness})
    closing = data.readiness[0].review.procedure.filing_closes_hour
    geometry_response = data.geometry[0].configuration.response_hour
    geometry_ready = data.geometry[0].configuration.resident_ready_hour
    bands = len(
        {
            (c.configuration.band.starts_hour, c.configuration.band.ends_hour)
            for c in data.geometry
            if c.configuration.band is not None
        }
    )
    return TimingCaptions(
        readiness=(
            f"Response and completed readiness in {len(data.readiness):,} stipulated cells. "
            "Two duty rows retain resident-b's consequences at 12 h and 3 h; columns show "
            "no, automatic and filing-activated protection. "
            f"Each {response} by {readiness} panel shows "
            "resident-b's uncovered integer hours on a common 0-24 h scale; the adjacent "
            "strip retains member-a separately. A cross marks readiness after inclusive "
            f"closing at {closing} h, including a zero-exposure cell with failed access. "
            "Protected bands start at the resident consequence and expire at 20 h for each "
            "person; activation is computed individually. All intervals are half open. "
            f"The complete union has {summary.configurations:,} configurations and "
            f"{summary.person_records:,} person records; {summary.shared_memberships:,} cells "
            "belong to both slices. These are parameter cells, not observed institutions; "
            "all four practical relations remain unassessed."
        ),
        protection=(
            f"Position of protection in {len(data.geometry):,} endpoint cells at response "
            f"{geometry_response} h and resident readiness {geometry_ready} h. "
            f"Each triangle contains the {bands} bands "
            "0 <= start < end <= 24; invalid bands are grey exclusions, not zeros. "
            "Colours distinguish empty, initial, terminal, two-component and wholly "
            "uncovered waits for resident-b. "
            f"{len(data.timeline_cells)} selected two-person timelines retain "
            "their exact cell identities and expose member-a separately. The original-duty "
            f"{_band_label(initial)} and {_band_label(terminal)} bands leave resident gaps "
            f"{_resident_gap(initial)} and {_resident_gap(terminal)}; "
            f"the early-threat {_band_label(filing)} band leaves a filing-triggered "
            f"{_resident_gap(filing)} gap versus {_resident_gap(automatic)} automatic exposure. "
            "These anchors extend existing H/P contrasts to the "
            "declared two-person grid; they are not rediscovered observations or an "
            "across-duty ranking. No gap colour establishes practical safety or legitimacy."
        ),
    )
