# EMLDS Hindustani lexemes: audit and enrichment

## Outcome (29 September 2026)

After the audit, 26 of the strongest candidates were enriched on Wikidata from `final/final_wikidata_edits.csv`. All 93 planned changes were applied in 40 revisions by Abxxra, then re-fetched and verified. The changes were:

- 26 senses, each with an English gloss;
- 12 concept links (P5137);
- 15 genders (P5185);
- 6 transitivity values (P9295);
- 25 Platts page references;
- 7 Urdu Lughat IDs;
- 2 usage examples, for فوراً and بخار.

Every change was recorded, with its revision ID, in `final/applied_changes.csv`. None was rejected. The uncertain items listed in section 5 were held back and not edited.

The audit that follows is the original proposal. Its statements about the lexemes' state describe them before enrichment.

Status of the audit below: it was written before any edits. Every figure below comes from the cached API responses in `raw/` (fetched 29 September 2026) and can be regenerated with `python3 build.py`.

## 1. The 117 lexemes

- **IDs:** L1732271 to L1732387, a continuous range. The full list is in `audit_117.csv`.
- **Created by me:** yes. The MediaWiki API (`list=usercontribs`, `ucshow=new`, namespace 146) shows that account **Abxxra** created exactly 117 lexemes, and they are these 117. The latest revision of every one is still Abxxra's creation, so nobody else has edited them.
- **Language:** all 117 use **Hindustani (Q11051)**, with an Urdu-script `ur` lemma. This matches the 83 existing lexemes the duplicate check matched against, which are also Q11051. Keep Q11051. Do not switch to Urdu (Q1617).
- **Lexical categories:** 75 nouns, 21 verbs, 16 adjectives and 5 adverbs. Query 02 on query.wikidata.org returns the same counts.
- **Current state:**
  - 0 senses and 0 glosses.
  - 0 statements, so no P5137 item, gender, Urdu Lughat ID or references.
  - No IPA.
  - Only a `ur` lemma. All 83 existing matched lexemes have both `ur` and `hi` lemmas.
  - 30 forms on 27 lexemes, and **none of them has grammatical features**.

## 2. Strongest enrichment candidates (50)

In the table below, **A** means strong: at least one addition is confident and the sense is unambiguous. **B** means worth doing, but a key fact needs human review first.

| Tier | Lexeme | Lemma | Category | Proposed sense (en) | Gender / transitivity | P5137 item |
|---|---|---|---|---|---|---|
| A | L1732273 | مدد | noun | help, assistance | f (PL, UL, WT) | none fits |
| A | L1732274 | سانس | noun | breath, breathing | f (PL, WT) | Q9530 |
| A | L1732281 | بجلی | noun | electricity; lightning | f (PL, WT; UL says m, flagged) | Q12725 / Q33741 |
| A | L1732282 | بخار | noun | fever | m (PL, UL, WT) | Q38933 |
| A | L1732287 | درد | noun | pain | m (PL, WT) | Q81938 |
| A | L1732296 | ہوش | noun | consciousness | m (PL, WT) | Q7087 |
| A | L1732312 | حادثہ | noun | accident | m (PL, WT) | Q171558 |
| A | L1732313 | حملہ | noun | attack, assault | m (PL, WT) | Q1174599 |
| A | L1732319 | دھماکہ | noun | explosion | m (WT only, review) | Q179057 |
| A | L1732324 | سیلاب | noun | flood | m (PL, WT) | Q8068 |
| A | L1732327 | عمارت | noun | building | f (PL, WT) | Q41176 |
| A | L1732348 | چنگاری | noun | spark | f (PL) | none found |
| A | L1732359 | گلی | noun | lane, alley | f (PL, WT) | Q1251403 |
| A | L1732363 | خراش | noun | scratch, abrasion | f (PL, WT) | Q939378 |
| A | L1732364 | ٹانگ | noun | leg | f (PL, WT) | Q6027402 |
| A | L1732370 | تھانہ | noun | police station | m (PL, WT) | Q861951 |
| A | L1732381 | نہر | noun | canal | f (PL) | Q12284 |
| A | L1732382 | پڑوسی | noun | neighbour | m (PL, WT) | Q1986893 |
| A | L1732286 | توڑنا | verb | to break | transitive (PL, WT) | |
| A | L1732305 | بلانا | verb | to call, summon | transitive (PL) | |
| A | L1732343 | پھیلنا | verb | to spread | intransitive (PL) | |
| A | L1732345 | پہنچنا | verb | to arrive, reach | intransitive (PL) | |
| A | L1732358 | پھنسنا | verb | to get stuck, be trapped | intransitive (PL) | |
| A | L1732367 | بتانا | verb | to tell, inform | transitive (PL) | |
| A | L1732368 | بجھانا | verb | to extinguish | transitive (PL) | |
| A | L1732383 | پھسلنا | verb | to slip | intransitive (PL) | |
| A | L1732290 | شدید | adj | severe, intense | | |
| A | L1732321 | زخمی | adj | wounded, injured | | |
| A | L1732300 | اچانک | adv | suddenly | | |
| A | L1732271 | فوراً | adv | immediately | | |
| A | L1732272 | جلدی | adv | quickly | | |
| B | L1732275 | ایمبولینس | noun | ambulance | unknown | Q180481 |
| B | L1732276 | ایکسیڈنٹ | noun | accident | unknown | Q171558 |
| B | L1732355 | ہسپتال | noun | hospital | unknown | Q16917 |
| B | L1732365 | ڈاکٹر | noun | doctor | m (WT only) | Q39631 |
| B | L1732328 | فائرنگ | noun | gunfire | unknown | Q2992372? |
| B | L1732298 | الرجی | noun | allergy | WT contradicts itself | Q42982 |
| B | L1732295 | گیس | noun | gas (fuel) | m (WT only) | none yet |
| B | L1732325 | سینہ | noun | chest | m (WT only) | Q9645 |
| B | L1732347 | چاقو | noun | knife | m (WT only) | Q32489 |
| B | L1732350 | ڈاکو | noun | bandit | m (WT only) | Q16144978 |
| B | L1732369 | بدبو | noun | stench | unknown | Q1519476 |
| B | L1732372 | جلن | noun | burning sensation | "s.m. & f." (PL) | Q3645517 |
| B | L1732374 | دورہ | noun | fit, attack (of illness) | m (PL) | medical sense not attested |
| B | L1732338 | ٹکر | noun | collision | f (WT only) | none (Q9687 too narrow) |
| B | L1732322 | زخمی | noun | wounded person | none: common gender | none (Q1230687 is a Polish legal term) |
| B | L1732366 | گھسنا | verb | ghusnā "enter" or ghisnā "rub"? | homograph | |
| B | L1732384 | پھٹنا | verb | to burst | not found in PL | |
| B | L1732316 | خطرناک | adj | dangerous | | |
| B | L1732333 | مشکوک | adj | suspicious | | |

The other 63 lexemes are not selected yet. Most are peripheral to the emergency domain (for example کزن, پارک, سائیکل) or are homographs that need a sense decision first (بس "bus/enough", کار "car/work", بو, تار, خانہ, چاہیے). Each one has a reason in `audit_117.csv`.

**Sources:**
- **PL:** Platts, *A Dictionary of Urdu, Classical Hindi, and English* (1884; Q108916279), read through DSAL.
- **UL:** Urdu Lughat, the Urdu Dictionary Board (Q18625803).
- **WT:** English Wiktionary. It is used only as corroboration and is never the sole basis for a "confident" value.

## 3. Candidates for sourced usage examples

**Ready, with a verified quotation** (text checked verbatim against the Urdu Lughat entry, pre-1950 source):

| Lexeme | Lemma | Sense | Attestation |
|---|---|---|---|
| L1732282 | بخار | fever | سیرۃ النبی ج ۳ ص ۱۳۷ (1923) |
| L1732281 | بجلی | electricity | رسالہ حسن ۳، ۸: ۷۲ (1890) |
| L1732271 | فوراً | immediately | خیابان آفرینش ۵۲ (1887) |
| L1732280 | کوشش | effort | خیابانِ آفرینش ۴ (1887) |
| L1732279 | شخص | person | باقیات بجنوری ۴۸ (1911) |

**Quotation found, but the source is post-1950, so check licensing first:**

| Lexeme | Lemma | Sense | Attestation |
|---|---|---|---|
| L1732278 | سائیکل | bicycle | کارِ جہاں دراز ہے (1978) |
| L1732284 | تار | telegraph wire | اردو دائرہ معارف اسلامیہ (1968) |

**Good targets that still need their Urdu Lughat entry read.** The site blocked this computer's address after 16 lookups, so I stopped rather than work around the block:

| Lexeme | Lemma | Note |
|---|---|---|
| L1732312 | حادثہ | Urdu Lughat ID 91290 is already identified |
| L1732313 | حملہ | |
| L1732324 | سیلاب | |
| L1732319 | دھماکہ | |
| L1732321 | زخمی | |
| L1732370 | تھانہ | |
| L1732368 | بجھانا | |

That gives 5 examples that are ready now and about 14 once the Urdu Lughat lookups resume. A quick check of Urdu Wikisource (public-domain texts) mostly turned up poetry with figurative uses of these words, so I did not use it.

## 4. What to add to each group

The pattern follows the 83 existing Hindustani lexemes.

- **Every A-tier lexeme:**
  - A sense with an English gloss.
  - An Urdu gloss, written as a short paraphrase rather than a copied Urdu Lughat definition.
  - P1343 "described by source" = Platts (Q108916279), with page (P304).
  - P11350 Urdu Lughat ID where the entry has been matched.
- **Nouns:**
  - P5185 grammatical gender: masculine Q499327 or feminine Q1775415.
  - P5137 "item for this sense", added on the sense, only where the item is an exact match.
  - Forms with direct case Q1751855 or oblique case Q1233197, singular Q110786 or plural Q146786, plus gender. Proposed as review items because they come from the regular paradigm, not from attestations.
- **Verbs:** P9295 transitivity, using transitive Q116946936 or intransitive Q116946937, which are the items already used by 22 existing Hindustani lexemes.
- **Usage examples:** P5831 on the sense, referenced with P248 "stated in" = Urdu Lughat plus P11350, and the original work and year.
- **The 30 existing forms:** add grammatical features, or remove any that are not paradigm forms (for example بڑھتی on بڑھنا is a participle, not a citation form).

## 5. Uncertain cases

- **بجلی gender:** the online Urdu Lughat header says masculine, while Platts and Wiktionary say feminine.
- **الرجی:** Wiktionary contradicts itself on the gender.
- **زخمی (noun):** has common gender, so P5185 should not be set.
- **دورہ:** the medical "fit/seizure" sense is not attested yet.
- **گھسنا:** it is unclear which homograph was intended.
- **Five English loanwords** (ایمبولینس, ایکسیڈنٹ, ہسپتال, فائرنگ, سیوریج): no dictionary gender was reached.
- **Hindi (Devanagari) lemmas:** proposed only as review items, because transliteration is an editorial decision.
- **IPA:** intentionally not proposed for any lexeme. The only IPA available is Wiktionary's template-generated IPA, which is not an attestation.

## 6. CSV structure

`enriched-lexemes.csv` has one row per proposed change, 443 rows in all. The columns are:

`lexeme_id, lemma, lexical_category, existing_sense, proposed_enrichment, property, proposed_value, evidence_source, source_url, confidence (high/medium/low), status, notes`

`status` takes one of four values:
- `missing_confident`
- `uncertain_review`
- `do_not_add`
- `already_present`

No row is `already_present` today, because the lexemes are empty.

`audit_117.csv` has one row per lexeme, with its current state, what is missing, its candidacy and the reason.

## 7. SPARQL queries (`sparql/`)

- **01** lists the 117 lexemes with language, category and sense/form counts.
- **02** summarises by language and category, and counts how many lexemes have senses, gender and a Urdu Lughat ID.
- **03** lists senses, glosses, P5137 items and usage examples with their sources.

All three queries were verified on query.wikidata.org:

- **01** returned the 117 lexemes.
- **02** returned 75/21/16/5.
- **03** returns 0 rows for now, because none of the lexemes has a sense yet. With an existing lexeme added (L1082246), it returned that lexeme's senses, glosses and a sourced usage example, so the query itself works.

## 8. Is it worthwhile?

Yes, if it stays small. The 117 lexemes are currently bare entries with a lemma and a category. Adding a sourced sense, gender or transitivity, a P5137 link and a dictionary reference to about 30 core emergency terms would make them usable for the task EMLDS needs, which is linking emergency vocabulary to concepts. Each claim would also be traceable to Platts or Urdu Lughat.

The weakest parts are:
- the loanwords, which have no dictionary gender yet;
- the usage examples, which depend on Urdu Lughat access and on the licensing of post-1950 quotations.

The proposal therefore treats both as review items rather than padding the lexemes with statements.
