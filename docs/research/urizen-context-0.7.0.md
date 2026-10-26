# Urizen: distinguish lexical repetition from independent evidence

The `states` query matches whole-word `state` and `states`, without case sensitivity. In the pinned primary reading plane, the seven retained `urizen` source units contain 49 matches. Every match falls inside one of seven repetitions of *a state of dismal woe* in each input. The seven input text hashes differ; exact-text deduplication therefore retains them.

The audit loads the imported corpus through `load_import`, which verifies the pinned index and payload identities, selects primary reading units with `work_id == "urizen"`, and evaluates two regular expressions against each unit's original text:

~~~python
state = re.compile(r"\bstates?\b", re.I)
refrain = re.compile(r"\ba\s+state\s+of\s+dismal\s+woe\b", re.I)
for hit in state.finditer(text):
    assert any(
        phrase.start() <= hit.start() and hit.end() <= phrase.end()
        for phrase in refrain.finditer(text)
    )
~~~

[The text-free result](../../research/urizen-refrain-audit-0.7.0.json) retains source, edition and copy identifiers, URLs, text hashes and per-input counts. It is a context audit of the preserved projection, rather than a collation of the original illuminated copies. The complete primary bodies remain in ignored local storage.

The [ASU transcription](https://blake.lib.asu.edu/html/book_of_urizen.html) places the refrains at 10:44, 11:9, 11:18, 11:25, 13:3, 13:11 and 13:19, E75–76. Reading plates 4, 10–13 and 28 connects this bodily sequence with Urizen’s unifying laws and the later attribution of prudential rules to divine eternity. The two additional quotation records preserve 4:34–40, E72, and 28:6–7, E83.

Rates and family-deletion ranges retain their original definitions. This audit adds an interpretive explanation for the concentration that those measurements expose. It changes neither the query nor its denominator and does not count repeated refrains as independent arguments.
