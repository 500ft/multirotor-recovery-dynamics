# V995 fixture source review, 2026-09-27

Companion: [research note](../../docs/v995-fixture-research-2026-09-27.md).
Research used the user's Chrome browser through the ChatGPT extension.

- `adafruit-4541-drawing-browser.png`: screenshot of the product-linked
  [75 mm cell drawing](https://cdn-shop.adafruit.com/product-files/4541/C14641+C14642+C14643+datasheet.png).
  Its mechanical dimensions and Chinese specification table were visually read.
- `adafruit-80mm-candidate-drawing-browser.png`: screenshot of the
  [80 mm image](https://cdn-shop.adafruit.com/product-files/5231/Datasheet.png)
  identified in the indexed text of the 4540 PDF. The PDF viewer remained
  inaccessible. Because the image is hosted under PID 5231, its 4540 association
  and delivered-part applicability remain candidate evidence. No performance
  specification appears in this image.
- `screening-calculation.json`: arithmetic using the published 4541 error terms,
  standard gravity, an unverified 50 g aircraft-mass scenario, and explicitly
  assumed independent rectangular bounds with coverage factor 2. It is not an
  installed calibration or a manufacturer-certified combined uncertainty.

The [2021 Adafruit support response](https://forums.adafruit.com/viewtopic.php?t=181236)
about PID 4540 was read directly after the website's automatic verification
completed. No generic TAL220 or SparkFun error specification was assigned to
the purchased 1 kg cell. No physical record or accepted numeric register changed.

Validation: local links exist; `git diff --check` passes; the pending-request
and fixture-contract consistency checks both pass. The historical contract still
has 2 evaluable and 10 pending clauses, which does not describe V995 acceptance.
