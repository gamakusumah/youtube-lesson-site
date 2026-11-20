# Content guidelines for the lesson page

## Accuracy first
- Every factual claim, number and rule must come from the transcript. Before writing a number, grep the transcript for it.
- Auto-generated captions contain mistakes (names, numbers, homophones). If a figure looks odd, check it against the surrounding sentences and prefer the value the speaker derives or repeats. If still unsure, leave it out or flag it in the final message.
- Things you add (practice tasks, analogies, a clarifying sentence) are fine, but say so in the final message. Never present an added fact as the speaker's.
- If the video was only partly readable (captions missing for a stretch), say which part is thin.

## Choosing sections
- 8 to 12 numbered sections. One idea per section, in the order the speaker builds the argument.
- Opening section: the problem or question the video starts from. Last two: a summary table, then practice tasks.
- Skip filler: greetings, sponsor reads, "like and subscribe", off-topic chat. Keep Q&A only if it adds a durable point.

## Writing each section
- `sec-no` + `h2.sec` (a claim or question, not just a noun), then 1 to 3 short paragraphs.
- Add what helps understanding, not all of these every time:
  - a figure (`figure > .fig-frame > svg`) when something is spatial, sequential or comparative;
  - a table when comparing 3+ things on 2+ attributes;
  - an `.analogi` block with one plain-language analogy;
  - a `.note` ("why it mattered", "common mistake"); `.note.alert` for a limitation or warning;
  - an `.eq` block for a short calculation.
- Keep paragraphs to 4 sentences or fewer (the CSS already limits line width).

## SVG figures
- `viewBox` about `0 0 700 H`, `role="img"` with a real `aria-label`.
- Wrap text in `<g font-family="JetBrains Mono, monospace">`; sizes 11 to 14.
- Palette (same tokens as the CSS): accent `#0257BA`, lift `#5B9BE8`, green `#79D3A5`, orange `#EDA45C`, red `#E8807F`, muted text `#8D959E`, dim text `#5F6975`, panel fills `#101317` / `#161A1F`.
- Arrow markers need unique ids per figure (`a1`, `a2`, ...). Clip paths too.
- Keep figures simple and honest: illustrative shapes must be labeled as illustrations.

## Labs (optional)
- Only when the topic has something computable or comparable. Use `makeLab(btnsId, codeId, outId, headers, samples)` from the reference; compute rows in JS rather than hardcoding.
- A lab shows a small input set (buttons), a code/definition box and a 3-column trace; mark the "aha" row with a 4th array element `true`.
- If there is nothing to compute, delete the lab CSS rules that are unused, the `makeLab` function, and the "labs" chip.

## Language and formatting
- Write in the video's spoken language unless the user asks otherwise. For mixed-language videos use the dominant language and keep technical terms the speaker keeps in their original language.
- Localize UI strings: `lang` attribute, TOC heading, footer, `aria-label`s, lab headers, `<title>`.
- Use the target language's number format (for example `1.234,5` in Indonesian, `1,234.5` in English). The reference Indonesian page has an `fmt()` helper pattern for this.
- Credit the source in the footer: video title, channel; no URL tracking parameters.
