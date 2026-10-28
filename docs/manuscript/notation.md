# Notation and reading conventions {#sec:notation .unnumbered}

The model distinguishes poetic interpretation, institutional claims and measured text. Relations record claims; their authority requires a separate assessment. Subscripts are local to the definition cited in the right column.

| Symbol | Meaning and first use |
|:----------------------|:------------------------------------------------------------|
| $P$, $S$, $N$ | Persons, poetic-state interpretations and historical national formations. [@def:typed] |
| $J$, $D$; $j$, $d$ | Institutions and proposed decisions; one institution and decision. $J$ is a sort, not an act's territorial reach. [@def:typed] |
| $A\subseteq P\times N$ | Affiliation: a person can participate in several nations. [@eq:relations] |
| $I\subseteq N\times S$ | Interpretation: nations can disclose several poetic-state readings. [@eq:relations] |
| $C\subseteq J\times D$ | Claimed competence, assessed independently of $A,I$. [@prop:no-transfer] |
| $d=(e,r,a,w,\tau,c,\rho,\epsilon,q)$ | Entity, assigned role, issuer, warrants, time, consequence, affected reach, enforcement and contestation route. Here $q,w$ name route and warrants; elsewhere $q,w$ index queries and families. [@def:decision] |
| $r_k(d)$; $K$; $T(d)$ | Boolean safeguard $k$; number of safeguards ($K=15$); their conjunction. Inactive conditions contribute 1 and are distinguished from active satisfied checks. [@def:trace] |
| $x$, $\ell$ | Tested fields and excluded descriptive labels. [@prop:ablation] |
| $F(d)$; $\pi(d)$; $F,G$; $f_i$ | Failed-rule set; protected context; abstract failure sets and an intervention acting on them. [@def:repair; @prop:monotone-repair] |
| $\mathcal O$; $B,B'$; $d_B$ | Twelve declared interventions; selected bundles; resulting record in fixed catalog order. [@def:repair] |
| $\mathcal A(d)$; $m(d)$; $\Delta_{ij}(d)$ | Admissible bundles, minimum size (undefined if none exists) and admission complementarity. Here $i,j$ index interventions, not institutions. [@eq:repair; @def:interaction] |
| $U$, $V$, $u$ | Eligible source units, a subset and one unit. Each analysis declares role and plane eligibility. [@def:coverage; @def:search-scope] |
| $t_u$, $c_{uq}$, $h_{uq}$ | Word tokens, query occurrences and presence in unit $u$. [@def:coverage] |
| $C_q(V)$; $R_q(V)$ | Unit coverage and occurrences per 10,000 tokens. $C_q$ is distinct from competence relation $C$. [@eq:coverage] |
| $U_w$; $W$, $W_+$ | Units in recorded family $w$; all recorded and positive-token families. A family groups witnesses without identifying their texts. [@def:family-rate] |
| $\overline R_q$; $\mathcal D_q$ | Equal-family mean and family-indexed deletion rates; ties retain their family identities. [@eq:family-rate] |
| $X_q$, $X_{q'}$; $n$ | Query-presence sets and comparison-universe size. [@def:association] |
| $\operatorname{Jac}(q,q')$; $\Pr(q'\mid q)$; $\operatorname{Lift}(q,q')$ | Jaccard overlap, directional conditional presence and lift. [@eq:association] |
| $Q$; $H_q(u)$; $M$ | Nonempty casefold-distinct literal terms, per-term nonoverlapping original-text matches and admitted units. [@def:search-scope] |
| $O$; $B_{\mathrm{match}}$; $L$ | Term-labeled occurrences, matched units and display cap. All counts precede the cap. [@eq:search-counts] |
| $b$; $\mathcal T_u$; $\nu_u(a,z)$ | Optional word budget, original-text token intervals and tokens intersecting envelope $[a,z)$. [@def:window] |
| $\eta=[s_\eta,e_\eta)$; $\Omega_b(u)$; $H_q^b(u)$ | Hit interval, qualifying complete match tuples and participating term matches. [@eq:window] |

A zero denominator is N/A; a populated denominator with no matches is zero. Subset counts differ from distinct resulting records. Solid affiliation, dashed interpretation and red competence links denote different claims, rather than successive authorization steps.


\clearpage

## Local notation for person-specific review {.unnumbered .unlisted}

These symbols apply to the person-specific review subsections of [@sec:s5],
beginning with [@sec:individual-review]. Here $i$ identifies an affected person,
not an intervention index; $P_i$ denotes protection rather than sort $P$; $G_i$
denotes uncovered intervals rather than a failure set; $U_i$ is hours rather than
the source-unit universe $U$. Boolean $B$ labels are distinct from intervention
bundles $B,B'$ and matched-unit count $B_{\mathrm{match}}$. Event time is measured
in integer hours from notice, with the event-order conventions stated in
[@def:review-wait; @def:review-profile].

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
