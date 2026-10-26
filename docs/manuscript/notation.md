# Notation and reading conventions {#sec:notation .unnumbered}

The notation separates poetic interpretation, institutional claims and measured text. A relation in the model records an affiliation, reading or claim; the warrant for exercising power is assessed separately. Subscripts identify a query, rule, source unit or source family.

| Symbol | Meaning and first use |
|:----------------------|:------------------------------------------------------------|
| $P$, $S$, $N$ | Represented persons, interpretations of poetic states, and historical national formations. [@def:typed] |
| $J$, $D$; $j$, $d$ | Institutions claiming jurisdiction and proposed decisions; a particular institution and decision. $J$ names a sort, not the territory or persons reached by an act. [@def:typed] |
| $A\subseteq P\times N$ | Affiliation: persons may participate in several national formations. [@eq:relations] |
| $I\subseteq N\times S$ | Interpretation: a national formation can disclose several poetic-state readings. [@eq:relations] |
| $C\subseteq J\times D$ | Claimed institutional competence. Neither affiliation nor interpretation determines it. [@prop:no-transfer] |
| $d=(e,r,a,w,\tau,c,\rho,\epsilon,q)$ | Entity, assigned role, asserting institution, stated warrants, temporal scope, consequence, affected reach, enforcement actor/limits, contestation route. Here $q$ is a contestation route and $w$ a warrant; subscripts $q,w$ below index queries and families. [@def:decision] |
| $r_k(d)$; $K$; $T(d)$ | Boolean result of safeguard $k$; the 15 programmed predicates; their conjunction. Condition-absent checks are displayed separately from active satisfied checks. [@def:trace] |
| $x$, $\ell$ | Tested decision fields and excluded descriptive labels in the label-invariance comparison. [@prop:ablation] |
| $F(d)$; $\pi(d)$ | Failed-rule set and protected material/jurisdictional context. [@def:repair] |
| $\mathcal O$; $B$; $d_B$ | The 12 declared interventions; a selected bundle; the resulting decision after fixed-order application. [@def:repair] |
| $\mathcal A(d)$; $m(d)$ | Admissible bundles and minimum bundle cardinality; the minimum is undefined if no bundle admits the record. [@eq:repair] |
| $\Delta_{ij}(d)$ | Admission complementarity of interventions $i,j$, measured on the conjunction, not on an extra resolved rule. [@def:interaction] |
| $U$, $V$, $u$ | Eligible source units, a selected subset, and one unit. The rate analysis selects primary units; literal search declares its eligible role/plane universe. [@def:coverage; @def:search-scope] |
| $t_u$, $c_{uq}$, $h_{uq}$ | Word-token count, query occurrences and presence indicator in unit $u$. [@def:coverage] |
| $C_q(V)$; $R_q(V)$ | Matched-unit coverage and occurrences per 10,000 word tokens. Subscripted $C_q$ is a proportion, distinct from competence relation $C$. [@eq:coverage] |
| $U_w$; $W$, $W_+$ | Units with source-family ID $w$; recorded families and positive-token families. A family ID is an archive grouping, not a claim that copies are identical. [@def:family-rate] |
| $\overline R_q$; $\mathcal D_q$ | Equal-family mean rate and the complete finite set of leave-one-family-out rates. [@eq:family-rate] |
| $X_q$, $X_r$; $n$ | Query-presence sets and size of the declared comparison universe. [@def:association] |
| $\operatorname{Jac}(q,r)$; $\Pr(r\mid q)$; $\operatorname{Lift}(q,r)$ | Jaccard overlap, directional conditional presence and lift. These statistics do not use the person/institution sorts $P,J$. [@eq:association] |
| $Q$; $H_q(u)$; $M$ | Literal query terms, character-aligned matches and admitted source units. ALL requires every term in one stored unit. [@def:search-scope] |
| $O$; $B_{\mathrm{match}}$; $L$ | Total term-labeled occurrences, matched-unit count and displayed-record limit. The cap leaves all counts and facets unchanged. [@eq:search-counts] |

An empty denominator yields an undefined statistic, reported as N/A; a populated denominator with no matches yields zero. Subset counts and distinct resulting decision records are reported separately. The diagrams use solid affiliation lines, dashed interpretation lines and a distinct red competence relation; these marks describe different claims rather than stages of one automatic authorization.
