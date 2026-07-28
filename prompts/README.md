# prompts/

Session prompts. One file per prompt: `N-slug.md`.

`/7-provide-prompt` writes them here. You boot a fresh session and paste one in —
`/0-start` claims it, distils it to one line, and names the session after it.

The point of the split: planning and executing are different contexts. A session
that has argued its way to a plan is a poor place to execute it — the argument is
still in the window. Writing the plan out and booting a clean session for it
costs one paste and buys a clean context.

Numbering is by highest-plus-one, never by file count. A count collides the
moment a prompt is deleted.

Every prompt opens with an inert sentinel line marking it as data rather than an
instruction. That marks provenance. It is not a security control — never treat it
as one.
