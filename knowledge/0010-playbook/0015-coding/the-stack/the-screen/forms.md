# Forms

Up: [[the-screen-MOC|The Screen]]

How a form sits on a screen: its fields, its notes, its hints and its marks.

A card never wraps fields. Fields sit on the page. A card's press may open
one reason box.

A note explains one part of the form. From `wide`, notes stand right of the
fields, in `--column-note`, each beside its part, in view while that part
scrolls. The fields take the rest, up to `--column-content`.

Below `wide`, each note sits above its part.

A form inside a screen's own list takes no note column, at any width.

A note sits on the surface, in a panel.
It holds a short label, then one or two sentences. Both are small type.
The label is bold, in the text colour. The sentences are in the second
text colour.

A field whose label is not enough carries a hint. The hint sits under the
field, always visible. An error takes its place while the error stands.

A needed field wears a red star after its label. A pair where one is
needed wears it once, on one label above both. Each field of the pair keeps
its own label, unstarred.

No field ever carries a placeholder.

A select wears the chevron, inside its right edge. Never the browser's arrow.

Every field, whatever its type, rests on the same border colour: text boxes,
selects, text areas, dates, passwords, radios and ticks.

A form never asks for a total its parts already make. It asks each part,
then shows their total.

A choice in a form that can't take input reads greyed out. Why shows under
its name.

A form that makes a record, on a screen of its own with no rail row, sits
under its list's address. A form started from a record sits under it.
