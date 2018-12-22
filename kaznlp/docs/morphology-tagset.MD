=== Tag set ===


The tag set employed in this release is a rather simple one, that gives up a lot of grammatical nuance for the sake of clarity and easier (faster) tagging. For example, no distinction is made between pronouns and determiners, copulas are not acknowledged, time-aspect-mood continuum is simplified to the extent possible, etc.


= POS tags =
```
R_ZE	Noun, common (жалпы есім)
R_ZEQ	Noun, personal (жалқы есім)
R_ET	Verb (етістік)
R_ETK	Verb, auxiliary (көмекші етістік)
R_ETP	Verb, special action* (арнайы етістік жатыр, отыр, тұр, жүр)
R_ETPK	Verb, special action, auxiliary (арнайы көмекші етістік жатыр, отыр, тұр, жүр)
R_ETB	Verb, negative (жоқ, емес only, e.g. барған жоқ)
R_SE	Adjective (сын есім)
R_SIM	Pronoun (есімдік)
R_US	Adverb (үстеу)
R_ZHL	Conjunct (both coordinating and subordinating) - (салалас және сабаұтас жалғаулық шылаулар)
R_SN	Numeral (сан есім)
R_SH	Adposition / Particle (шылау, бөлшек)
R_MOD	Modal word (модаль сөз)
R_OS	Interjection (оқшау сөз)
R_ELK	Imitative (еліктеуіш)
R_SYM	Symbol (#, $, +, etc.)
R_BOS	Foreign word (бөтен / шетелдік сөз)
R_X	Un-analyzed (талданбаған)
```
\* special action verbs (жатыр, отыр, тұр, жүр) are considered as a separate category, because only they can receive agreement markers being in a base form, i.e. жатыр/отыр/тұр/жүр + мын/мін/сың/сің... is possible, but же + мін (or any other verb and agreement marker) is impossible directly, there has to be something in between, e.g. же + й + мін, же + р + мін, же + ме + й + сің, etc.


= punctuation =
```
R_NKT	.
R_UTR	,
R_DPH	-
R_ATRN	«
R_ZTRN	»
R_TRN	"
R_QNKT	:
R_SUR	?
R_AZZ	(
R_ZZZ	)
R_LEP	!
R_UNKT	;
R_SLH	/
R_APS	'
R_BSLH	\
```

= non-transitional morphemes =
```
N1	plural (көптік жалғау)
N1S	plural, after possessive, e.g. мама_R_ZE м_S1 дар_N1S
S1	possessive  (тәуелдік жалғау), first singular (1-ші жақ, жекеше)
S2	possessive, second singular
S3	possessive, third singular/plural
S4	possessive, second singular, formal
S5	possessive, first plural
S9	possessive, special (-ныкі, -дыкі, -тыкі)
S3SIM	possessive, third singular/plural, after pronouns
C2	genitive case (ілік септік)
C3	dative case (барыс септік)
C4	accusative case (табыс септік)
C5	locative case (жатыс септік)
C6	ablative case (шығыс септік)
C7	instrumental case (көмектес септік)
LATT	locative-attributive (-дағы, -дегі, -тағы, -тегі)
SML	similative (-дай, -дей, -тай, -тей)
ABE	abessive (-сыз, -сіз)
EQU	equative (-ша, -ше, e.g. балаша)
CMP	comparative, (adjectives and adverbs)
V1	reflexive voice (өздік етіс)
V2	passive voice (ортақ етіс)
V3	cooperative voice (өздік етіс)
V4	causative voice (өзгелік етіс)
M2	imperative mood (бұйрық рай)
M3	desiderative mood (қалау рай)
M4	conditional mood (шартты рай)
T1	aorist (ауыспалы осы/келер шақ)
T2	future tense (болжамды/мақсатты келер шақ)
T3	past tense (жедел/бұрынғы өткен шақ)
T3E	past tense, modified after е_R_ET (e.g., е_R_ET т_T3E)
P1	agreement (жіктік жалғау), 1st singular (1-ші жақ, жекеше)
P2	agreement, 2nd singular
P3	agreement, 3rd singular
P4	agreement, 2nd singular, formal
P5	agreement, 1st plural
P6	agreement, 2nd plural
P7	agreement, 3rd plural
P8	agreement, 2nd plural, formal
```

= transitional morphemes =
```
ET_KSE	verbal adverb, participle (көсемше)
ET_ESM	verbal adjective, noun (есімше)
ET_ETU	gerund (тұйық етістік)
ET_ETB	negated verb (болымсыз етістік)
```

Transitional morphemes consist of two underline-separated parts («1_2») that indicate the transition from one (pseudo-) POS to another.
This concerns only transitions between types of verbs.

The four basic transitions are given above and others are possible, e.g. a verb can be negated and then turned into a gerund, which results in two transitions ET_ETB and ETB_ETU.

There is a total of 19 transitional morphemes, which are: ET_KSE, ET_ESM, ET_ETU, ET_ETB, ETP_KSE, ETP_ESM, ETP_ETU, ETP_ETB, ETK_KSE, ETK_ESM, ETK_ETU, ETK_ETB, ETPK_KSE, ETPK_ESM, ETPK_ETU, ETPK_ETB, ETB_KSE, ETB_ESM, ETB_ETU.
