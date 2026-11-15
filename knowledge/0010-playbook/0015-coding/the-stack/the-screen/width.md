# Width

Up: [[the-screen-MOC|The Screen]]

Where a screen's content stands, and how wide, at every width.

A screen's content spans `Page`'s column, or centres in it. The white left
of it always equals the white right.

A list and a home span. A form with notes centres. From
`wide` it takes at most `--column-centred`. Below, at most `--column-content`.

Only fields and prose stop at `--column-content`. A Settings page may stop at
a document's width. On a record's page, prose
spans like every other part.

Nothing moves when a view changes, even when it grows past the window:
every screen keeps its scrollbar's room, on both sides, whether it scrolls
or not.
