# Walks standard

Up: [[walks-MOC|Walks]]

The only standard for a walk file. `walks/` is not the vault: the vault's standard never reaches it.

## What walks/ holds

My walks of the app. One folder per area: a part of the app with its own address, like `app/`, or `admin/`.

Every folder carries a MOC: its front door, listing its direct children in walking order, each with a link and a short purpose.

## An area's folder

- Its MOC, `<area>-MOC.md`, listing its sections in the menu's order under "Sections", then those across sections under "Across sections".
- `before-you-start.md`, its facts, each a bold label read by name:
  - **Where** · the address I walk, and each server behind it.
  - **Code** · where its screens' routes sit, and the file every quote comes from.
  - **Logins** · each login a step names, by email, and how it gets in.
  - **The walker's login** · how a walker makes its own, and which seeded login it stands for.
  - **Data** · how the test data is filled and reset, and where a Prep's database change runs.
  - **Codes and links** · where an email's code or link comes from: a dev door, or a log.
  - **Marked** · every marked step, and every Not designed one.
- One folder per section.

A section is one menu entry, getting in, or the frame every screen shares. A journey across sections is a section of its own.

Folder names: the entry's name in kebab-case, like `settings/`, and the journey's, like `first-purchase/`.

## Two kinds of walk

A features walk checks what a screen does. A looks walk checks how it shows: each language, each width. Each walks on its own, at its own moment.

Each journey of a features walk passes whole before the next, as `knowledge/0010-playbook/0017-walking/the-walking-axioms.md` rules: its flow, its other roles' views, then its docs pages. A feature's walk goes stage by stage instead: there, another place's steps, docs pages included, walk at the stage they show.

The flow runs each step once: one language, 1500 wide, the main role.

A way that changes what happens stays a lettered detail. A way that changes only what shows joins a looks sweep.

## A section's folder

Its files, in this order. A file with nothing to hold stays out.

- `<section>-MOC.md`: its files.
- `0-checklist.md`: every features check, my mark and the tester's: each step, each lettered detail, and each cover file's rows. `.claude/tools/walk-checklists.py` builds it from the journey files, keeping every mark. Under each journey: its flow, then each cover step covering one of its steps. Its 0 sorts it first.
- One file per journey: its steps.
- Cover files, when the section needs them: `member.md`, another role's view of the section's screens, and `docs.md`, each docs page naming them, one step per page, each claim a lettered detail. A docs step's italic line opens with the page's address.
- `looks/`: the looks walk. `looks-checklist.md`, built the same way, then one sweep per file, like `english.md` or `widths.md`.
- `walked.md`: there only while the section is walked whole, every "Tester" mark ✅ and every "You" mark ✅ or —. Its body is one line: "Every step of <section> passed, by you and the tester, on <date>." It goes the moment a step goes back to ⬜. While it stands, the section's MOC lists it first.

A cover or looks step's italic line ends naming the journey steps it covers: `*<what it checks> · Sign up 1, Forgot 1*`. Its checklist lists it under the first journey holding one. A step naming none stays under its own file.

A name stays short: the folder names the section. A link carries its path from `walks/`, since two areas can hold the same names.

## Every file

Line one is the title. Line two is blank. Line three is `Up:`, linking its folder's MOC; a MOC links the MOC above it, and `walks-MOC.md`, at the top, has none. Line four is blank. Line five is one purpose line. The body follows.

## Marks

✅ passed. ⬜ not passed yet. — not mine: a page only developers see is the tester's alone.

The tester is the walker and the analyzer together. The walker walks; the analyzer's verdict is the "Tester" mark.

A check passes once the tester and I both pass it. On a docs row, my pass is my own read of its page. A failed check reads ⬜. A step that changes goes back to ⬜, each mark it held, its details' too.

Marks live in each checklist alone.

## A journey file

It opens with its Start, its Prep and its End. Then its steps.

The Start names the state the steps need, and the logins, by email. No password is written. A question for me stands in the Start, after "Ask". Once I answer, its steps take my answer, and the Ask goes.

Each journey names its own steps, as "Sign up 3".

A step is one thing I do, then what I see. Its head names the screen, its address, and who I am. "Do" holds the exact values to type. "See" quotes the exact words, word for word from the file `before-you-start.md`'s Code names.

Other ways and edge cases fold under the step, lettered, in "Details the tester checks". Each opens with its letter and a short title, which its checklist row shows.

A step the walker readies carries "Prep". A Prep names its exact change: the database and its SQL, the call and its body, the command, or the log line it reads. A walker on its own login never resets the test data: a Prep needs no reset. A Prep acts on the walker's own login and company, never on a seeded one's. A step on a page only developers see is the tester's alone.

```text
### Sign up 3 · Type the code from the email

*<screen> · <address> · <who I am>*

**Do** · Type the code sent to <email>. Press <the button>.

**See** · <what opens>.

> [!note]- Details the tester checks (2)
> - **a · A wrong code is refused** · A wrong code → "<the words it shows>"
> - **b · A new code stops the first** · Send a new code → "<the words it shows>" The first code stops working.
```

A mark follows a step's title.

- **Hidden**: ruled out of sight. "See" says where it must not show.
- **Not built**: ruled, not built yet. Its step stands where I would look, never walked.
- **Stand-in**: words nobody ruled yet. I give mine.
- **Server only**: runs only on a deployed server, never on this laptop. My walker walks it there. "See" quotes what the laptop shows instead.
- **Real**: tests the real channel itself, which nothing seeded proves: an email arriving from the mail company, the Mac's Touch ID, a phone's authenticator app. It is my hands: the walker hands it to me, and I do it in my own Chrome.

**Not designed** stands in `before-you-start.md` alone, never as a step. No mark exists for code still changing.

Where the vault and the screen disagree, the step quotes both, as "Vault:" and "Screen:", and my word says which is right.

A sweep step is a table: one row per state or width, its words quoted.

## Keeping it current

`walk-write` writes every line: one a file already rules at once, any other once I confirm it. The lead writes the marks. Nobody else writes a walk file.

Right before each journey, `walk-write` reads its code. It brings each step they make wrong in line, and names each change. A change no session of the walk explains stays a finding.

The lead writes each check's "Tester" mark from the analyzer's case, and my mark the moment I approve or refuse. A section walked whole gets its `walked.md`.

Once a fix ends, `walk-write` rewrites each line it made wrong: "See" takes the screen as it is now, and the step goes back to ⬜. A section no longer walked whole loses its `walked.md`. Whoever adds, removes or renames a step, a detail or a sweep row reruns `.claude/tools/walk-checklists.py`.

## A walk's end

Once I end a walk, a copy of each area's folder goes to the references, into `walks/`, one dated folder per walk. `walks/` stays as it is.
