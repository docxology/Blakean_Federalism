# Abstract {.unnumbered .unlisted}

Institutional review depends on who can bring a challenge, what participation requires, when protection begins and what the reviewer can change. This supplement develops that claim through Blake's accounts of provision and misdirected punishment, Pettit's contestatory democracy, Shachar's allocation of review initiative and Tully's contestable procedures of recognition. A person-specific computational audit holds one institutional decision fixed while comparing fourteen declared review procedures for a member and an affected nonmember. It checks admission, remaining affiliated, usable preparation hours, filing readiness, continuity of protection, issuer separation and power to revise. The comparison exposes failures concealed by a named forum: aggregate participation capacity can coexist with an individual's shortfall; a late response can leave a gap before or after interim protection; and making protection conditional on filing can expose a person before the filing window opens. Two data-derived figures retain each condition and trace the uncovered hours. These calculations specify access under stated procedures. Their contribution is to make the work, timing and authority of review inspectable alongside the decision being challenged.

# Notation and event order {.unnumbered}

The symbols below are local to this supplement. Hours measure exact event time from notice at hour zero; they do not represent calendar days or an estimated response distribution.

| Symbol | Meaning and type |
|---|---|
| $i$ | One explicitly listed affected individual; membership does not determine standing |
| $t_o,t_c,t_r$ | Filing opens, filing closes, response takes effect; nonnegative integer hours, $t_o\leq t_c\leq t_r$ |
| $t_i^a,t_i^f$ | Completed-prerequisite readiness and earliest filing; $t_i^f=\max(t_o,t_i^a)$ |
| $t_i^q$ | Time the specified consequence reaches individual $i$, in hours |
| $h_i^a,h_i^s,h_i^r$ | Available, support-enabled and required preparation hours for $i$ |
| $P_i$ | Active interim-protection interval, or the empty set |
| $G_i,U_i$ | Uncovered waiting intervals and their summed duration in hours |
| $B_i^{\mathrm{admit}},B_i^{\mathrm{remain}},B_i^{\mathrm{hours}},B_i^{\mathrm{file}},B_i^{\mathrm{wait}}$ | The five individual Boolean conditions in document order |
| $B_{\mathrm{office}},B_{\mathrm{revise}}$ | Procedure has distinct issuing/reviewing office IDs; procedure can revise the act |
| $B_{\mathrm{review}}$ | Conjunction of the seven declared conditions for every listed individual |

Filing at the closing instant is permitted. A response effective at the consequence instant acts first. Protection covers a half-open interval $[a,b)$: an end at the response instant covers the preceding wait. Readiness records completed prerequisites, not the start of preparation. Available and support-enabled hours are declared usable, nonoverlapping preparation time within the filing window; their sum cannot exceed its duration.

# Review must reach the person who bears the consequence

Blake places provision inside an unresolved conflict. At Los's porches, troubling Spectres receive sustenance:

> The Sons of Los clothe them & feed, & provide houses & gardens

William Blake, *Jerusalem* 73:49, E229. [@blakeJerusalem].

The recipients have not become an exemplary public whose disputes are over. Provision sustains people amid the feuds of Albion's cities; it accompanies the passage through states rather than rewarding a completed reconciliation. A procedure that recognizes the right to challenge a provider but lets food, housing or essential supply disappear during the challenge separates standing from the conditions needed to exercise it. Our review comparison makes that separation visible through preparation capacity and continuity of protection. Blake supplies the practical pressure on the question; the particular filing rules are our construction.

Los also asks where a remedy's force falls:

\Needspace{7\baselineskip}

> If I should dare to lay my finger on a grain of sand\
> In way of vengeance; I punish the already punishd: O whom\
> Should I pity if I pity not the sinner who is gone astray!

William Blake, *Jerusalem* 45:33–35, E194. [@blakeJerusalem].

Los sees injury but cannot identify an adequate target for vengeance. In its surrounding theological argument, the lament refuses the easy passage from recognizing suffering to authorizing punishment. A water authority that cuts supply to punish an association's officers can burden the residents whose deprivation occasioned review. Continuing provision, changing an allocation and sanctioning an official are different acts. A review record should identify the consequence being challenged, the people exposed to it and the duties that continue while the challenge is heard [@blakeJerusalem, 45:2–38, E194; 73:34–54, E228–229].

Pettit's distinction between collective electoral control and plural contestation gives an institutional reason to record individual access. An affected person's appeal need not wait for a representative body to endorse the objection [@pettit2005, pp. 1–4, 9]. An association's place in a federal council therefore cannot substitute for a dissenting member's or affected nonmember's standing. Nor should remaining in an affiliation make a person ineligible to challenge what its authorities do. Shachar's reversal points allow recourse across authorities; her account of loyalty pressures explains why informed choice alone can leave a vulnerable member unable to use that recourse [@shachar2005, pp. 72–76]. The audit records whether a hearing requires affiliation exit. Residence, livelihood and protection against retaliation demand their own institutional commitments.

# Initiative, independence and revision are different powers

Shachar's arbitration example makes the burden of initiating review explicit. Mandatory scrutiny before an award becomes enforceable removes the requirement that a vulnerable party start the protective process [@shachar2005, p. 76 and nn. 89–90]. This is a different mechanism from merely telling the person where to complain. The comparison below distinguishes automatic protection from protection triggered by a feasible filing. Both name a provider and an interval. Their consequences differ when the threatened deprivation begins before the filing window opens.

An office's separate identity also records less than independence. Pettit assumes independent and impartial appeals [@pettit2005, p. 9]. Distinct office identifiers do not establish independent appointments, budgets or evidence access. The audit calls this predicate **issuer separation**. It records a relationship that can be checked without treating a different name as evidence of impartiality. Similarly, suspension, advice and revision do different work. A forum that can suspend an act can interrupt its operation; a forum that can revise can change it. Shachar's power to overrule an inequitable aspect of an agreement supplies a concrete comparator for consequential review [@shachar2005, p. 77]. A claimant need not win for review to matter, but an advisory recommendation and a binding revision do not confer the same power.

The disagreement about procedures goes deeper. Pettit's account presupposes admissible reasons through which decisions can be challenged; Tully opens the procedures and criteria of reasonable argument themselves to contestation [@pettit2005, pp. 8–9; @tully2006Recognition, pp. 25–27]. A forum might hear objections to a water allocation while refusing objections to the categories defining whose interests count. Revising that allocation, revising the classification rule and contesting the forum's competence are distinct questions. Tully's separation of dialogue from decision keeps other institutional routes available when negotiation leaves minorities exposed [@tully2006Recognition, p. 29]. Individual admission in the present audit supplies no mandate to determine a people's collective or treaty claim.

# Fourteen procedures expose what a named forum leaves unspecified

::: {.definition #def:review-wait title="Uncovered waiting time"}
For individual $i$, let the waiting interval be $[t_i^q,t_r)$ when $t_i^q<t_r$, and empty otherwise. Remove the active protection interval $P_i$ to obtain $G_i$. Its total duration is $U_i$:

$$
G_i=\begin{cases}[t_i^q,t_r)\setminus P_i,&t_i^q<t_r,\\\varnothing,&t_i^q\geq t_r,\end{cases}
\qquad U_i=\sum_{[a,b)\in\operatorname{components}(G_i)}(b-a).
$$ {#eq:review-wait}

Automatic protection starts at its declared start. Filing-triggered protection can start only after admission, remaining affiliated, enough preparation hours and filing readiness all hold; its start is the later of the declared start and $t_i^f$. An expired interval does not activate. The timing condition is $B_i^{\mathrm{wait}}\equiv(U_i=0)$.
:::

\Needspace{10\baselineskip}

::: {.definition #def:review-profile title="Seven declared review conditions"}
Individual admission and remaining affiliated are declared separately. The hours condition is $h_i^a+h_i^s\geq h_i^r$; filing readiness is $t_i^f\leq t_c$. Together with the timing condition and the two procedure-level predicates, the profile is

$$
B_{\mathrm{review}}=B_{\mathrm{office}}\land B_{\mathrm{revise}}\land
\bigwedge_i\left(B_i^{\mathrm{admit}}\land B_i^{\mathrm{remain}}\land B_i^{\mathrm{hours}}\land B_i^{\mathrm{file}}\land B_i^{\mathrm{wait}}\right).
$$ {#eq:review-profile}

The conjunction preserves each person's conditions. It does not add their preparation hours together or substitute association representation for individual admission.
:::

All fourteen procedures retain the same `E-bounded` institutional decision and its existing safeguard assessment. Each lists one member and one affected nonmember. The ordinary filing window is 2–8 h; the member has 6 usable preparation hours and needs 4, while the nonmember has 1 available plus 3 support-enabled hours and needs 4. The consequences begin at 18 h and 12 h respectively. H01 responds at 10 h. H02 removes one support-enabled hour from the nonmember: the two people still have 9 h against 8 h total requirements, but the nonmember's own requirement is unmet. H03 makes that person ready at 9 h, after closing.

::: {.proposition #prop:review-underdetermined title="Completed safeguard fields do not determine review access"}
The original institutional decision and its safeguard result do not determine the review-access profile in [@def:review-profile]. H01 and H04 preserve that decision exactly but differ in response timing; the former satisfies the timing condition and the latter fails it for both individuals. This pair is a constructive counterexample to deriving access from the original record alone.
:::

![The fourteen procedures keep the original E-bounded decision and its fifteen safeguard fields unchanged. Open circles mark a condition holding; red crosses identify a failed condition, with the first five columns requiring both listed individuals. H02 isolates person-specific capacity; H03 isolates readiness; H04, H06, H07 and H14 isolate uncovered waiting intervals. H08 and H09 distinguish admission from remaining affiliated. H10 has revision power but no issuer separation; H11 has separation and suspension power but cannot revise. H12 satisfies the seven declared conditions while retaining retaliation and disputed forum competence outside the audit. The marks are calculated from the stored procedure inputs, not assigned as institutional ratings.](../figures/institutional-review.png){#fig:review-matrix width=98%}

\Needspace{8\baselineskip}

For H04–H07 the response occurs at 20 h. Without protection the nonmember waits 8 uncovered hours and the member 2. Automatic protection over $[12,20)$ removes both gaps. Starting the nonmember's protection at 13 h or ending it at 19 h leaves a one-hour gap at a different end of the interval. H13 and H14 move filing to 14–18 h and reduce the member's declared capacity to fit that shorter window. Automatic protection can begin at 12 h in H13; filing-triggered protection starts at 14 h in H14. The nonmember consequently has two uncovered hours in H14, even though the filing and protection records are complete.

![Seven selected traces follow the affected nonmember on one zero-based event-hour scale. The thin bracket is the filing window; the red vertical mark is the 12 h consequence; the open circle is the response; the elevated black band is active protection; and the red horizontal band is uncovered waiting time calculated by [@def:review-wait]. A response at 10 h precedes the consequence in H01. H04 leaves all eight hours uncovered, H05 covers the full interval, and H06/H07 leave an initial/final one-hour gap. H13 and H14 share the late filing window but differ in activation: automatic protection covers 12–14 h, whereas protection awaiting a feasible filing does not. Protection ending exactly at the response covers the wait under the declared half-open interval convention.](../figures/review-continuity.png){#fig:review-timeline width=98%}



H12 satisfies all seven conditions while retaining retaliation and disputed forum competence as named unassessed issues. Investigation must establish that people can use the declared time and assistance, that protection continues, that revision binds the responsible actor and that people can contest the forum's own authority. The audit identifies these questions alongside the conditions it calculates.
