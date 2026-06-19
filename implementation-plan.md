# Implementation Plan: Paradoxical & Modal Cards

## 1. Background & Problem Statement

The deck builder and card database currently treat a card's **name** as its gameplay
identity. This shows up in three places:

- **Deck editor JS** ([`edit_decklist.js`](cardDatabase/static/js/edit_decklist.js)) merges
  cards into a single stack by comparing the rendered `.deck-zone-card-name` text
  (`card.name`). Adding any printing of "X" just increments the quantity of the existing "X"
  stack — see [`edit_decklist.js:324-338`](cardDatabase/static/js/edit_decklist.js#L324-L338).
- **Reprints** ([`CardType.py:225-226`](cardDatabase/models/CardType.py#L225-L226)) is defined
  as *every other Card with the same `name`*.
- **Bans / rulings** ([`CardType.py:189-194`](cardDatabase/models/CardType.py#L188-L194),
  [`CardType.py:220-222`](cardDatabase/models/CardType.py#L220-L222)) also key off `name`.

Two new requirements break this "name == identity" assumption:

### 1a. Paradoxical cards
A new card version can be **paradoxical**. **`Paradoxical` is itself a new card type**, so the
marker is the presence of a `Paradoxical` `Type` on the card — *not* a new boolean field. A
paradoxical card shares the name of an older card but does **not** replace it. Both the original
and the paradoxical version can sit side by side in the same deck (they are distinct gameplay
objects with separate copy limits).

- **Bug today:** the paradoxical version is listed as a "reprint" of the original (same name),
  and in the deck editor the two collapse into one stack — it is impossible to run both.

### 1b. Modal cards (with legacy data)
Some physical cards carry **two halves on the same face — a top half and a bottom half**
(not a front/back flip). Historically these were imported as **two separate `Card` rows**
distinguished by the set-code suffix characters:

- `{Set-Code}` — top half (e.g. `XXX-064`, name `Split Heaven and Earth`)
- `{Set-Code}^` or `{Set-Code}*` — bottom half (e.g. `XXX-064^`, name `Groundsplitting Rabbit`)

These are wired together today only through the
[`other_sides`](cardDatabase/models/CardType.py#L196-L218) property — a **legacy workaround**
from earlier times — which matches on the shared set-number plus the
[`OTHER_SIDE_CHARACTERS`](fowsim/constants.py#L156-L161) (`J^`, `^`, `J`, `*`). The goal is to
replace that workaround with explicit modal modelling.

- **Bug today:** the deck editor only knows the **top half's** name (`Split Heaven and Earth`).
  A *standalone* card that is also named `Split Heaven and Earth` therefore collides with the
  modal card — only one of them can be added to a deck. In reality the modal card's gameplay
  name is the combined **`Split Heaven and Earth//Groundsplitting Rabbit`**, which is distinct
  and should coexist with the standalone card.

> ⚠️ **Legacy data warning:** modal cards already exist in the DB as `^`/`*` row pairs wired via
> `other_sides`. **But `^`/`*` is also used by genuine two-sided / transform cards that are NOT
> modal** — they share the exact same pool and mechanism. So we cannot treat every `^`/`*` pair
> as modal, and we cannot remove or repurpose `other_sides`. The migration must **extract only the
> truly modal pairs** (explicit, curated — see §4) and leave all other two-sided cards (including
> ruler ↔ J-ruler `J`/`J^` flips) exactly as they are.

---

## 2. Core Concept: a stored "deck grouping key"

The root cause is that *name* is overloaded as the gameplay identity. The fix is to introduce
an explicit, queryable **grouping key** that decides:

1. which printings collapse into one deck stack,
2. what counts as a "reprint",
3. what label the deck editor shows.

Define a new denormalised, indexed column on `Card`:

```
grouping_key   # the gameplay identity used for deck stacking & reprints
display_name   # what the deck editor / search result should label the card
```

Rules for computing them:

| Card kind             | `grouping_key`                                           | `display_name`                       |
|-----------------------|----------------------------------------------------------|--------------------------------------|
| Normal                | `name`                                                   | `name`                               |
| Paradoxical           | `name` + paradoxical marker (e.g. `"<name>\x1fPARADOXICAL"`) | `"<name> (Paradoxical)"`         |
| Modal (top half)      | combined modal name `"top//bottom"`                      | combined modal name `"top//bottom"`  |
| Modal (bottom half)   | same combined key as its top half                        | (not independently addable — see §6) |

> The paradoxical marker is derived from the card carrying the `Paradoxical` **card type**, not
> from a dedicated column (see §3).

Because the key is **stored** (not a Python `@property`), it can be used directly in ORM
filters (`reprints`, deck grouping, search) and indexed for speed. It is recomputed on
`Card.save()` via a `pre_save` signal (mirroring the existing image-resize signal at
[`CardType.py:258-285`](cardDatabase/models/CardType.py#L258-L285)) and back-filled by the
migration command in §4.

> Use a non-printable separator (e.g. `\x1f`, ASCII Unit Separator) inside `grouping_key` so it
> can never collide with a real card name. `grouping_key` is internal; `display_name` is what
> users see.

---

## 3. Data Model Changes

File: [`cardDatabase/models/CardType.py`](cardDatabase/models/CardType.py)

**Paradoxical is a card type, not a field.** Add `"Paradoxical"` to
[`CARD_TYPE_VALUES`](fowsim/constants.py#L82-L105) and to the appropriate
[`DATABASE_CARD_TYPE_GROUPS`](fowsim/constants.py#L432-L487) bucket (likely "Main Deck") so it
flows through the existing `Type` machinery and the card-type search select. A card is
paradoxical iff it has a `Type` named `Paradoxical` in its `types` M2M.

Add to the `Card` model (modal modelling + denormalised grouping only — **no `is_paradox`/`is_modal`
booleans**; modal status is implied by `modal_face`/`modal_partner`, paradoxical by the type):

```python
# --- Modal (top/bottom halves of one physical card) ---
MODAL_FACE_TOP = "top"
MODAL_FACE_BOTTOM = "bottom"
modal_face = models.CharField(max_length=8, null=True, blank=True)  # null => not modal
# Links the two halves together (top.modal_partner == bottom, and vice-versa).
modal_partner = models.ForeignKey(
    "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
)

# --- Denormalised grouping (see §2) ---
grouping_key = models.CharField(max_length=420, db_index=True, blank=True)
display_name = models.CharField(max_length=420, blank=True)
```

Add helper logic on `Card`:

```python
@property
def is_modal(self):
    return self.modal_face is not None

@property
def is_paradoxical(self):
    return self.types.filter(name=CONS.CARD_TYPE_PARADOXICAL).exists()

@property
def modal_combined_name(self):
    """top.name//bottom.name for a modal pair, computed from the top half."""
    if not self.is_modal:
        return self.name
    top = self if self.modal_face == self.MODAL_FACE_TOP else self.modal_partner
    bottom = top.modal_partner if top else None
    if top and bottom:
        return f"{top.name}{CONS.MODAL_NAME_SEPARATOR}{bottom.name}"
    return self.name

def compute_grouping_key(self):
    if self.is_modal:
        return self.modal_combined_name
    if self.is_paradoxical:
        return f"{self.name}{CONS.GROUPING_KEY_SEPARATOR}PARADOXICAL"
    return self.name

def compute_display_name(self):
    if self.is_modal:
        return self.modal_combined_name
    if self.is_paradoxical:
        return f"{self.name}{CONS.PARADOXICAL_DISPLAY_SUFFIX}"
    return self.name
```

> **Modal display.** The **stored** `display_name`/`grouping_key` use the canonical top-half
> form `top.name//bottom.name` regardless of which row computes them, so deck stacking is stable
> (and only the top half is ever added to a deck anyway, §6c). On an individual card's own detail
> page you may instead render `self.name//partner.name` ("currentcard//otherHalf") for
> readability — a presentation-only helper, not the grouping key.

> **M2M timing caveat.** `is_paradoxical`/`grouping_key` depend on the `types` M2M, which is set
> *after* `Card.save()`. The `pre_save` signal alone can't see it, so recompute the stored
> `grouping_key`/`display_name` from an **`m2m_changed` signal on `Card.types`** (plus the
> `pre_save` handler for the modal fields, and the back-fill command in §4). Keep the existing
> image-resize `pre_save` at [`CardType.py:258-285`](cardDatabase/models/CardType.py#L258-L285)
> untouched.

### Update existing identity-based properties

- **`reprints`** ([`CardType.py:225-226`](cardDatabase/models/CardType.py#L225-L226)) — match
  on `grouping_key` instead of `name`, so paradoxical & modal variants are **not** treated as
  reprints of the base card:

  ```python
  @property
  def reprints(self):
      return Card.objects.filter(grouping_key=self.grouping_key).exclude(id=self.id)
  ```

- **`other_sides`** ([`CardType.py:196-218`](cardDatabase/models/CardType.py#L196-L218)) — **leave
  unchanged.** It stays the mechanism for *all* genuine two-sided cards (ruler/J-ruler flips and
  real double-sided/transform cards), and still returns the partner half for modal cards too (so
  image hover keeps working). `modal_face`/`modal_partner` are **added alongside** it for the
  modal-specific behaviour (grouping key, deck label, search exclusion in §6) — they do not
  replace `other_sides`. Only deck-grouping/search logic keys off the new modal fields; rendering
  keeps using `other_sides`.

- **`bans` / `combination_bans`** — **paradoxical cards are NOT affected by the banlist of the
  non-paradoxical card** (decision §10.2). These currently filter by `card__name`
  ([`CardType.py:189-194`](cardDatabase/models/CardType.py#L188-L194)); switch them to filter by
  `card__grouping_key=self.grouping_key` so a ban on non-paradoxical "X" does not hit
  paradoxical "X" (and vice-versa):

  ```python
  @property
  def bans(self):
      return BannedCard.objects.filter(card__grouping_key=self.grouping_key)

  @property
  def combination_bans(self):
      return CombinationBannedCards.objects.filter(cards__grouping_key=self.grouping_key)
  ```

  This depends on the back-fill (§4) having populated `grouping_key` on the cards referenced by
  `BannedCard`/`CombinationBannedCards`. Note the banlist import
  ([`importBanlist`](cardDatabase/management/commands/)) resolves cards by name — confirm it
  targets the intended (non-paradoxical) printing.
- **`rulings`** ([`CardType.py:220-222`](cardDatabase/models/CardType.py#L220-L222)) — same
  treatment as bans (decision §10.2): switch from `card__name` to
  `card__grouping_key=self.grouping_key` so a paradoxical card and the normal card that shares its
  name do **not** show each other's rulings:

  ```python
  @property
  def rulings(self):
      return Ruling.objects.filter(card__grouping_key=self.grouping_key)
  ```

  Depends on the back-fill (§4) having populated `grouping_key` on the cards referenced by
  `Ruling`.

### Migration

`python manage.py makemigrations cardDatabase` then `migrate`. The new columns are nullable /
defaulted, so the schema migration is safe. A **data** back-fill happens in §4.

---

## 4. Legacy Data Migration (Management Command)

> 🚫 **`other_sides` is NOT being removed or repurposed.** It is the live mechanism for genuine
> two-sided cards — ruler ↔ J-ruler flips (`J`/`J^`) **and** real double-sided/transform cards
> (`^`/`*`). Modal cards happen to *also* live in that same `^`/`*` pool today. The task is to
> **extract only the modal pairs** out of that pool and add modal modelling on top — leaving every
> genuine two-sided card exactly as it is. Modal cards keep working with `other_sides` too (their
> halves still share a set-number, so image hover is unaffected); we only *add* `modal_face`/
> `modal_partner` to them.

Add `cardDatabase/management/commands/migrate_modal_cards.py` (follow the existing command
style in [`cardDatabase/management/commands/`](cardDatabase/management/commands/)).

**Do NOT auto-classify by card type.** A `^`/`*` pair of main-deck types can be a genuine
double-sided/transform card, not modal — a type heuristic would mis-tag real cards. Modal
identification must be **explicit and curated**, never inferred.

Responsibilities:

1. **Enumerate candidates (report only).** Iterate cards whose `card_id` ends in `^` or `*`
   (`DOUBLE_SIDED_CARD_CHARACTER`, `ALTERNATIVE_SIDE_CHARACTER`), pair each with its base via the
   existing `other_sides` logic (shared set-number, suffix stripped), and print the full list of
   pairs with names/types/ids. This is the human-review surface for deciding which pairs are
   actually modal vs. genuinely two-sided.
2. **Take an explicit modal list as input.** The command marks a pair as modal **only** when its
   base `card_id` appears in a supplied allow-list — e.g. a `--modal-ids XXX-064 ...` arg or a
   small committed fixture file `modal_cards.json` (list of base `card_id`s, the **top** half).
   Nothing is classified as modal without being named here. (Going forward, if the card JSON
   gains a `Modal`/`split` marker, the command can read that instead — see §10.4.)
3. **Dry-run by default.** Print exactly what will change and require `--commit` before writing,
   matching the cautious tone of the other import commands. Refuse (and warn) if a named id has a
   `J`/`J^` partner, as a guard against accidentally listing a ruler flip.
4. **Mark.** For each confirmed pair (no booleans — modal status is implied by the fields):
   - top half (the base `card_id`): `modal_face="top"`, `modal_partner=bottom`
   - bottom half (`^`/`*`): `modal_face="bottom"`, `modal_partner=top`
5. **Recompute** `grouping_key` & `display_name` for the two touched cards only.
6. **Back-fill all cards** (separate `--backfill-all` flag) recomputes `grouping_key`/`display_name`
   for the whole table so normal cards get `grouping_key == name`, paradoxical cards (carrying the
   `Paradoxical` type) get their marked key, and genuine two-sided non-modal cards are left with
   `grouping_key == name` (unchanged behaviour — they were never grouped specially anyway).

Paradoxical cards are **not** import-driven (decision §10.1): they already exist on prod and no
import will run, and future cards are created manually via the **Add Card** admin page (§8b).
- **Existing prod paradoxical cards** are marked once via §8c (attach the `Paradoxical` `Type`).
- **Future cards** get the `Paradoxical` checkbox in `AddCardForm` (§8b).
In both cases the `pre_save` + `m2m_changed` signals (§3) recompute `grouping_key`/`display_name`
on save, so attaching the type is enough to mark a card.

Run order: create the `Paradoxical` `Type` row (§8 data migration) → mark existing prod
paradoxical cards (§8c) → `migrate_modal_cards` for legacy modal pairs (this command) →
`--backfill-all` to recompute every card's `grouping_key`/`display_name`.

---

## 5. Search Filters (`database_base.html` + form + query)

### 5a. Form fields
File: [`cardDatabase/forms.py`](cardDatabase/forms.py) — in `AdvancedSearchForm`, mirror the
existing `solo_mode` BooleanField ([`forms.py:85`](cardDatabase/forms.py#L85)):

```python
paradoxical = forms.BooleanField(label="Paradoxical:", required=False)
modal = forms.BooleanField(label="Modal:", required=False)
```

(`Paradoxical` is also reachable via the existing card-type multiselect once added to
`DATABASE_CARD_TYPE_GROUPS`, but a dedicated toggle was explicitly requested.)

### 5b. Query helpers
File: [`search_context.py`](cardDatabase/views/utils/search_context.py) — mirror
`get_solo_mode_query` ([`search_context.py:366-370`](cardDatabase/views/utils/search_context.py#L366-L370)).
Paradoxical filters on the card **type**; modal filters on `modal_face`:

```python
def get_paradoxical_query(paradoxical):
    return Q(types__name=CONS.CARD_TYPE_PARADOXICAL) if paradoxical else Q()

def get_modal_query(modal):
    return Q(modal_face__isnull=False) if modal else Q()
```

Wire them into `advanced_search` alongside the other `.filter(...)` calls
([`search_context.py:120-140`](cardDatabase/views/utils/search_context.py#L120-L140)):

```python
paradoxical_query = get_paradoxical_query(advanced_form.cleaned_data["paradoxical"])
modal_query = get_modal_query(advanced_form.cleaned_data["modal"])
...
    .filter(paradoxical_query)
    .filter(modal_query)
```

### 5c. Template UI
File: [`database_base.html`](cardDatabase/templates/cardDatabase/html/database_base.html) — add
two checkboxes modelled exactly on the existing **Solo Mode** block at
[`database_base.html:79-86`](cardDatabase/templates/cardDatabase/html/database_base.html#L79-L86),
placed right after it:

```html
<div class="fieldWrapper paradoxical-mode-container">
    <div class="paradoxical-mode-input">
        {{ advanced_form.paradoxical }}
    </div>
    <label class="paradoxical-mode-label" for="id_paradoxical">
        Paradoxical
    </label>
</div>
<div class="fieldWrapper modal-mode-container">
    <div class="modal-mode-input">
        {{ advanced_form.modal }}
    </div>
    <label class="modal-mode-label" for="id_modal">
        Modal
    </label>
</div>
```

(Optionally reuse the `solo-mode-container` styling, or add matching rules in
`database_base.css`.)

---

## 6. Deck Editor Changes (the central fix)

The deck editor must stack & label cards by **grouping key / display name**, not raw `name`.

### 6a. Expose the key to the frontend
- **Search result template** ([`search.html:73-90`](cardDatabase/templates/cardDatabase/html/search.html#L73-L90)):
  add `data-grouping-key="{{ card.grouping_key }}"` and use `{{ card.display_name }}` for the
  visible label. Keep `data-card-id` (the save payload still references a concrete `card_id`).
- **Deck zone card template**
  ([`edit_decklist.html`](cardDatabase/templates/cardDatabase/html/edit_decklist.html#L59-L82)
  and [`edit_decklist_mobile.html`](cardDatabase/templates/cardDatabase/html/edit_decklist_mobile.html)):
  render `data-grouping-key="{{ card.card.grouping_key }}"` and display
  `{{ card.card.display_name }}` instead of `{{ card.card.name }}`.

### 6b. Key the JS by grouping key, not name
File: [`edit_decklist.js`](cardDatabase/static/js/edit_decklist.js) (and any `_mobile` variant).

- The merge check at
  [`edit_decklist.js:324-326`](cardDatabase/static/js/edit_decklist.js#L324-L326) currently does:
  ```js
  let card_matches = deck_zone_cards.find('.deck-zone-card').filter(function(){
      return $(this).find('.deck-zone-card-name').text() === card_name;
  });
  ```
  Change all such comparisons (also the drag/drop dedupe at
  [`edit_decklist.js:413`](cardDatabase/static/js/edit_decklist.js#L413) and the mobile
  add-to-zone at [`edit_decklist.js:537`](cardDatabase/static/js/edit_decklist.js#L537)) to
  compare `$(this).data('grouping-key') === grouping_key`.
- `createCardHtml` ([`edit_decklist.js:283-297`](cardDatabase/static/js/edit_decklist.js#L283-L297))
  must accept & render `data-grouping-key` and use the **display name** for the visible text.

**Result:**
- Normal "X" + paradoxical "X" → different `grouping_key` → two separate stacks, both runnable. ✅
- Modal `Split Heaven and Earth//Groundsplitting Rabbit` (grouping key = combined name) vs
  standalone `Split Heaven and Earth` → different keys → both addable. ✅
- Two different printings of plain "X" → same `grouping_key` → still merge into one stack
  (unchanged behaviour). ✅

### 6c. Modal bottom half must not be independently addable
A modal card is **one** physical card. Only the **top half** should appear as an addable
search result / deck entry; the bottom half's data is shown via the existing hover/other-sides
rendering.

- **Search results:** exclude modal bottom halves from the card list. Add an exclusion in
  `advanced_search`/`basic_search`
  ([`search_context.py:82`](cardDatabase/views/utils/search_context.py#L82),
  [`search_context.py:123-140`](cardDatabase/views/utils/search_context.py#L123-L140)), e.g.
  `.exclude(modal_face=Card.MODAL_FACE_BOTTOM)`, the same way unsupported sets are excluded via
  `get_unsupported_sets_query()`.
- **Image hover:** the top half's `other_sides`/`get_card_img_urls`
  ([`card_database_tags.py:489-495`](cardDatabase/templatetags/card_database_tags.py#L489-L495))
  already pulls in the bottom-half image, so the combined card still shows both halves on hover.

### 6d. Save path
File: [`save_decklist.py`](cardDatabase/views/post/save_decklist.py) — payload still sends a
concrete `card_id` ([`save_decklist.py:65`](cardDatabase/views/post/save_decklist.py#L65)),
which for a modal card is the **top half's** `card_id`. No change required to the lookup, since
each stack still carries exactly one representative `card_id`. Verify that decks saved before
the migration (which may reference a bottom-half `^`/`*` `card_id`) still load — add a small
normalisation: if a saved `card_id` resolves to a modal bottom half, swap to its top-half
partner on load. (Handle in [`edit_decklist.py`](cardDatabase/views/edit_decklist.py#L40-L47) /
[`view_decklist.py`](cardDatabase/views/view_decklist.py) context building.)

---

## 7. Card Detail / Reprints Display

- [`card_details.html:206-217`](cardDatabase/templates/cardDatabase/html/card_details.html#L206-L217)
  now shows only true reprints (same `grouping_key`), so paradoxical versions drop out of the
  Reprints list automatically once §3 lands.
- Consider adding a small **"Paradoxical version"** / **"Modal — see also <other half>"** info
  block next to Reprints so users can still discover the related original. Optional, but good UX.

---

## 8. Constants & the `Paradoxical` Type Row

File: [`fowsim/constants.py`](fowsim/constants.py):

- Add `"Paradoxical"` to [`CARD_TYPE_VALUES`](fowsim/constants.py#L82-L105) and a
  `CARD_TYPE_PARADOXICAL = "Paradoxical"` constant, and add it to the relevant
  [`DATABASE_CARD_TYPE_GROUPS`](fowsim/constants.py#L432-L487) bucket (likely "Main Deck").

  > ⚠️ **Must be in `DATABASE_CARD_TYPE_GROUPS`, not just `CARD_TYPE_VALUES`.** The `AddCardForm`
  > sorts its type checkboxes with `types_list.index(...)` over
  > `DATABASE_CARD_TYPE_GROUPS` ([`forms.py:176-180`](cardDatabase/forms.py#L176-L180)). Any type
  > present in the DB but **absent** from that list raises `ValueError` and breaks the add-card
  > page. Adding it to a group also makes it selectable in the card-type search select for free.

- Add near the side-character block ([`constants.py:151-161`](fowsim/constants.py#L151-L161)):

```python
PARADOXICAL_DISPLAY_SUFFIX = " (Paradoxical)"
GROUPING_KEY_SEPARATOR = "\x1f"
MODAL_NAME_SEPARATOR = "//"
MODAL_FACE_TOP = "top"
MODAL_FACE_BOTTOM = "bottom"
```

Keep `OTHER_SIDE_CHARACTERS` unchanged (still used for ruler flips & rendering).

**A `Type(name="Paradoxical")` row must exist in the DB** for the checkbox to appear in
`AddCardForm` and for `card.types` to reference it. Add a **data migration** that
`get_or_create`s this `Type` row (the `Type.name` field already has
`choices=listToChoices(CONS.CARD_TYPE_VALUES)`, [`CardType.py:74-78`](cardDatabase/models/CardType.py#L74-L78),
so once the constant is added the value is valid). This is the prod-safe way to introduce the
type, since **no card import will run** (see §8b).

---

## 8b. Admin "Add Card" Form (the real creation path — no import)

Paradoxical cards already exist on prod and **will not be re-imported**, and all future cards are
created manually through the admin **Add Card** page
([`add_card.py`](cardDatabase/views/admin/add_card.py),
[`AddCardForm`](cardDatabase/forms.py#L123-L167)). So the add-card flow — not `importjson` — is
where these markers must be selectable.

### Paradoxical — works automatically once §8 lands
`AddCardForm` already renders `types` as a `CheckboxSelectMultiple`
([`forms.py:158`](cardDatabase/forms.py#L158)). Once the `Paradoxical` `Type` row exists and is
in `DATABASE_CARD_TYPE_GROUPS`, a **"Paradoxical" checkbox appears automatically** alongside the
other type checkboxes — no form change needed beyond §8. Confirm the
[`add_card.html`](cardDatabase/templates/cardDatabase/html/add_card.html) template renders the
`types` checkboxes generically (it does, by iterating the field) so the new option shows without
a template edit; the form comment at [`forms.py:124`](cardDatabase/forms.py#L124) warns the
template must track field changes, so verify.

### Modal — needs new form controls
Modal pairing has no representation in `AddCardForm` today. Add two fields:

```python
# in AddCardForm
modal_face = forms.ChoiceField(
    required=False,
    choices=[("", "Not modal"), (Card.MODAL_FACE_TOP, "Top half"), (Card.MODAL_FACE_BOTTOM, "Bottom half")],
)
modal_partner = forms.CharField(
    required=False,
    help_text="card_id of the other half (e.g. the bottom half's XXX-064^)",
)
```

On save (override `AddCardForm.save()` or handle in
[`add_card.py`](cardDatabase/views/admin/add_card.py#L29-L34)):

1. Set `new_card.modal_face` and resolve `modal_partner` from the entered `card_id`.
2. **Link both directions symmetrically** — set `partner.modal_partner = new_card`,
   `partner.modal_face` to the opposite face, and save the partner too.
3. Saving recomputes `grouping_key`/`display_name` on both via the signals (§3).

Add the two fields to [`add_card.html`](cardDatabase/templates/cardDatabase/html/add_card.html)
(the form is rendered field-by-field per the comment at [`forms.py:124`](cardDatabase/forms.py#L124)).
Since the partner half often must exist first, the typical flow is: add the bottom half, then add
the top half and point `modal_partner` at the bottom half's `card_id` (linking back-fills both).

> If an `edit_card` view exists or is added later, mirror these controls there so existing prod
> cards can be paired without a command. Otherwise existing modal pairs are handled by
> `migrate_modal_cards` (§4) and existing paradoxical cards by §8c.

---

## 8c. Marking the existing prod paradoxical cards

The card JSON is the **source of truth** for which cards are paradoxical: a card is paradoxical
iff its `type` array contains `"Paradoxical"` (always listed *alongside* its base type, e.g.
`"type": ["Paradoxical", "Resonator"]` — confirming §10.6). Example from the `AVL` set:
`AVL-002, AVL-004, AVL-007, AVL-010, AVL-012, AVL-018, AVL-020, AVL-021, AVL-033, AVL-035,
AVL-036, ...`.

Because the `Paradoxical` type did not exist as a valid value when these cards were first
created, the prod rows do **not** yet carry the `Paradoxical` `Type` — so their `grouping_key`
would back-fill to plain `name` and still collide. No full content re-import is wanted, so mark
them with a **targeted type-attach pass driven by the same JSON**:

- A small management command reads the card JSON, and for every entry whose `type` array
  contains `"Paradoxical"`, looks up the existing `Card` by `card_id` and attaches the
  `Paradoxical` `Type` (idempotent `get_or_create` + `card.types.add(...)`).
- **Skip cards not yet in the DB** ("some are not added yet" — they'll get the type naturally
  when added via **Add Card**, §8b, or whenever they're imported).
- The `m2m_changed` signal (§3) recomputes `grouping_key`/`display_name` as the type is added.

This reuses the import JSON instead of a hand-maintained ID list. (Equivalently, the existing
`incrementalCardImport` could be pointed at the affected sets — but a narrow type-attach command
is lower-risk since it only touches the `types` M2M, not card text/images.)

Run the §4 `--backfill-all` **after** this marking so every card's `grouping_key` is correct.

---

## 9. Tests

Extend [`cardDatabase/tests/`](cardDatabase/tests/) (pytest + pytest-django, per CLAUDE.md):

- `test_models.py` — `grouping_key`/`display_name` computation for normal, paradoxical, and
  modal (top+bottom) cards; `reprints` no longer includes paradoxical/modal variants
  (extend existing `test_card_reprints` at
  [`test_models.py:145-159`](cardDatabase/tests/test_models.py#L145-L159)); the `m2m_changed`
  signal recomputes `grouping_key` when the `Paradoxical` type is added/removed; **`bans`,
  `combination_bans`, and `rulings` on a paradoxical card do not return the
  same-named normal card's bans/rulings (and vice-versa)**.
- New `test_modal_migration.py` — `migrate_modal_cards` marks **only** the pairs named in the
  explicit modal list (top→bottom linked symmetrically), **leaves genuine two-sided/transform
  `^`/`*` cards untouched** (no `modal_face` set, `other_sides` still returns them), refuses/warns
  on a `J`/`J^` partner, and is a no-op without `--commit`. Also assert `other_sides` behaviour is
  unchanged for a non-modal double-sided card.
- `test_search` — `paradoxical` / `modal` advanced-search filters return the right sets, and
  modal bottom halves are excluded from results.
- `test_add_card` — submitting `AddCardForm` with the `Paradoxical` type attaches it and yields
  the marked `grouping_key`; submitting modal fields links **both** halves symmetrically
  (`modal_partner`/`modal_face` set on each, both `grouping_key`s = the combined name). Guard
  against the `DATABASE_CARD_TYPE_GROUPS` sort `ValueError` (i.e. the add-card page renders with
  `Paradoxical` present).
- Deck round-trip — a deck containing both a standalone card and a same-named modal card (and
  both a normal + paradoxical card) saves and reloads with **two distinct stacks** each.

---

## 10. Resolved Decisions

1. **Source of truth for the markers — RESOLVED.** The card **JSON** marks paradoxical cards via
   `"Paradoxical"` in the `type` array (alongside the base type). No full content re-import is
   wanted; paradoxical cards are already on prod and future cards are added via the manual
   **Add Card** admin page (§8b). So: future paradoxical cards get a `Paradoxical` checkbox in
   `AddCardForm`; existing prod paradoxical cards are marked once by a targeted JSON-driven
   type-attach pass (§8c), skipping not-yet-added cards; legacy modal pairs are linked by the
   one-off `migrate_modal_cards` command (§4) and future modal cards via new add-card fields (§8b).
2. **Banlist & rulings — RESOLVED.** Paradoxical cards are **not** affected by the banlist of the
   non-paradoxical card, and the two must **not** share rulings either. `bans`/`combination_bans`
   **and `rulings`** switch from `name` to `grouping_key` (§3).
3. **Copy-limit counting — RESOLVED (mostly moot today).** Paradoxical and non-paradoxical are
   *separate cards* but **share a single 4-copy allowance** (e.g. any mix of non-paradoxical +
   paradoxical "X" up to 4 total). Crucially this is a different axis from deck stacking:
   - **Stacking / display** uses `grouping_key` → paradoxical and non-paradoxical are **separate
     stacks** you can add side by side. ✅ (the whole point)
   - **Copy-limit counting**, *if/when enforced*, must count by **base `name`** (shared
     allowance), **not** `grouping_key`.

   There is **no 4-of rule enforced anywhere in the codebase today** (verified: the deck editor
   JS and save path impose no per-card maximum). So no code is needed now — this is recorded so
   that a future validator counts by base name. (A `base_name` helper = `grouping_key` stripped
   of the paradoxical marker, or just `name`, would serve that validator.)
4. **Modal as one row vs two — RESOLVED.** Keep the **two legacy rows**; the top half is the
   deck representative (lowest-risk, preserves legacy data & images). No collapse to a single
   row. **`other_sides` is preserved** — genuine two-sided/transform cards share the `^`/`*` pool,
   so modal pairs are **extracted explicitly via a curated list** (§4), never by a type heuristic.
   *Open input:* supply the modal base `card_id`s (a short reviewed list / fixture), or add a
   `Modal`/`split` marker to the card JSON so future modal cards self-identify like Paradoxical.
5. **Labels — RESOLVED.** Paradoxical: `"X (Paradoxical)"`. Modal: simple
   `currentcard//otherHalf` concatenation. The **stored** `grouping_key`/`display_name` is the
   canonical top-half form `"top//bottom"` (so stacking is stable); an individual card's own
   detail page may render it relative to the viewed half (`currentcard//otherHalf`) for
   readability — see §3 note.
6. **`Paradoxical` accompanies the base type — RESOLVED.** A paradoxical Resonator keeps its
   `Resonator` type *and* gains `Paradoxical`. Consequences: card-type search by `Resonator`
   still returns it, deck-zone placement (which keys off the main-deck types) is unaffected, and
   the dedicated `Paradoxical` toggle simply narrows to cards that *also* carry that type.

---

## 11. Suggested Rollout Order

1. **Constants + Type row** — add `Paradoxical` to `CARD_TYPE_VALUES` **and**
   `DATABASE_CARD_TYPE_GROUPS`; add the modal/label constants; data migration to `get_or_create`
   the `Type(name="Paradoxical")` row (§8).
2. **Schema** — add `modal_face`/`modal_partner`/`grouping_key`/`display_name` fields + `pre_save`
   & `m2m_changed` signals + `compute_*` helpers (§3); migration.
3. **Add Card form** — `Paradoxical` checkbox appears for free; add modal fields + symmetric
   linking + template fields (§8b).
4. **Prod data** — mark existing prod paradoxical cards (§8c); run `migrate_modal_cards` for
   legacy modal pairs; then `--backfill-all` to recompute every card's `grouping_key`/`display_name`
   (§4).
5. **Reprints/bans/rulings** property updates (§3) + card-detail display (§7).
6. **Search filters** — form, query, template (§5).
7. **Deck editor** — template data attrs + JS keying + modal exclusion + saved-deck
   normalisation (§6).
8. **Tests** (§9) throughout.
9. Manual QA: add an original + paradoxical + standalone-named + modal card to one deck and
   confirm independent stacks behave correctly on save/reload/export; add a paradoxical and a
   modal card via **Add Card** and confirm the type/markers persist.
