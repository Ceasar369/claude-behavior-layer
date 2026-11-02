#!/usr/bin/env python3
"""skills-page.py — every skill, as a cheat sheet, on 1100/skills.

Each skill's name, description and arguments already sit in the head of
its SKILL.md. The page reads every head each time it draws, so it is
always current, stores nothing, and never spends a token.

Skills group by family. A family is its router, D-name, then its
children, name-*, in the order of their digits. Every other skill sits
first, under No family, laid left to right across the page. The numbered
families follow in as many columns as the width holds.

A row leads with its command, copied on a click. Under it, its
arguments, one choice a line. Under them, its intent, the description's
first sentence, across the column. A small filter narrows every family
to the rows holding each word typed; Enter copies the first.

The dashboard's server serves it. Imported, never run.
"""

import hashlib
import os
import re
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import page  # noqa: E402
import registry  # noqa: E402

SKILLS = os.path.join(registry.ROOT, ".claude", "skills")
ROUTER = re.compile(r"(\d+)-(.+)")
# The families whose pages wear an icon, beside their digit.
ICONED = ("assistant", "clarify", "prototype", "agenda")


def value(raw: str) -> str:
    """A head's value as it reads: a double-quoted one drops its quotes, and
    its \\" and \\\\ read as a quote and a backslash."""
    raw = raw.strip()
    if len(raw) > 1 and raw[0] == raw[-1] == '"':
        return re.sub(r'\\(["\\])', r"\1", raw[1:-1])
    return raw.strip('"')


def heads() -> list:
    """Every SKILL.md's head, as (name, description, arguments), by name."""
    out = []
    for name in sorted(registry.listing(SKILLS)):
        try:
            with open(os.path.join(SKILLS, name, "SKILL.md")) as f:
                text = f.read(4000)
        except OSError:
            continue
        head = text.split("---", 2)[1] if text.startswith("---") else ""
        field = lambda k: next((value(line.split(":", 1)[1]) for line in head.splitlines()
                                if line.startswith(f"{k}:")), "")
        out.append((field("name") or name, field("description"), field("argument-hint")))
    return out


def families(found: list) -> list:
    """(digit, family, [skills]) for every router, by digit, then No family."""
    routers = sorted(((m.group(1), m.group(2), s) for s in found if (m := ROUTER.fullmatch(s[0]))),
                     key=lambda r: (int(r[0]), len(r[0])))
    taken = {r[2][0] for r in routers}
    groups = []
    for digit, fam, router in routers:
        kids = [s for s in found if s[0] not in taken and s[0].startswith(f"{fam}-")]
        taken |= {s[0] for s in kids}
        groups.append((digit, fam, [router] + kids))
    return groups + [("", "no family", [s for s in found if s[0] not in taken])]


def args(hint: str) -> str:
    """A skill's arguments, one choice a line. What each means dims."""
    return '<div class="args">' + "".join(
        f'<div>{page.esc(form)}' + (f' <span class="mn">— {page.esc(means)}</span>' if means else "") + '</div>'
        for form, _, means in (choice.partition(" — ") for choice in hint.split(" · "))) + '</div>'


def line(skill: tuple) -> str:
    name, description, arguments = skill
    intent = (re.match(r".*?[.!?](?=\s|$)", description) or [description])[0]
    return (f'<div class="sr"><button class="cmd" title="Copy /{page.esc(name)}" data-c="/{page.esc(name)}">'
            f'<span class="t">/{page.esc(name)}</span>{page.icon("copy", 13)}</button>'
            + (args(arguments) if arguments else "")
            + f'<p class="int">{page.esc(intent)}</p></div>')


STYLE = """<style>
  body > main { padding:0; }
  header.top.skills .mid { justify-self:stretch; color:var(--dim); font-weight:400; font-size:13px; }
  .find { max-width:560px; }
  .hm { display:inline-flex; align-items:center; gap:6px; font-size:11px; color:var(--dim); white-space:nowrap; }
  .hm b { color:var(--text); }
  .first { padding:12px 12px 0; }
  .first .skf { margin:0; }
  .across { display:grid; grid-template-columns:repeat(auto-fit, minmax(max(220px, calc((100% - 72px) / 5)), 1fr)); column-gap:18px; }
  .across .sr { border-top:1px solid var(--line); }
  .sk { columns:360px; column-gap:12px; padding:12px; }
  .skf { break-inside:avoid; margin:0 0 12px; padding:6px 12px; background:var(--panel);
    border:1px solid var(--line); border-radius:6px; }
  .skf.none { display:none; }
  .skh { display:flex; align-items:center; gap:8px; margin:0 0 4px; padding:2px 0 6px; border-bottom:1px solid var(--line); }
  .skh b { font-size:13px; }
  .dg { flex:none; min-width:20px; padding:0 4px; border-radius:4px; text-align:center; font-size:11px;
    font-weight:700; background:var(--raised); color:var(--text); }
  .sr { padding:6px 0; }
  .sr.none { display:none; }
  .sr + .sr { border-top:1px solid var(--line); }
  .cmd { max-width:100%; display:inline-flex; align-items:center; gap:7px; padding:0; font:inherit;
    font-size:13px; font-weight:700; line-height:20px; color:var(--text); background:none; border:0; cursor:pointer; }
  .cmd .t { min-width:0; overflow-wrap:anywhere; text-align:left; }
  .cmd svg { color:var(--blue); }
  .cmd:hover .t { color:var(--blue); }
  .cmd.ok .t, .cmd.ok svg { color:var(--green); }
  .args { margin:2px 0 0; padding-left:8px; border-left:2px solid var(--blue); font-size:12px; line-height:17px;
    color:var(--text); overflow-wrap:anywhere; }
  .args .mn { color:var(--dim); }
  .int { margin:3px 0 0; font-size:12px; line-height:18px; }
  mark { background:var(--hover); color:var(--text); border-radius:2px; box-shadow:0 0 0 1px var(--grey); }
  .nomatch { padding:12px; color:var(--dim); display:none; }
  @media (max-width:520px) { .first { padding:8px 8px 0; } .sk { padding:8px; } }
  /* A touch screen, as my phone, and never a Mac, however narrow its pane.
     Every control takes a fingertip: 44 by 44 points, Apple's minimum. */
  @media (hover:none) and (pointer:coarse) {
    .cmd { min-height:44px; }
  }
</style>
"""

# The filter waits to be clicked: nothing takes my keys when the sheet
# opens. Each word marks where it shows.
SCRIPT = """<script>
(() => {
  const q = document.getElementById('q'), hm = document.getElementById('hm'), all = hm.innerHTML;
  const rows = [...document.querySelectorAll('.sr')];
  rows.forEach(r => r.querySelectorAll('.int, .cmd .t').forEach(e => e.dataset.t = e.textContent));
  const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
  const safe = s => s.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&');
  let first = null, timer = 0;
  // It flashes only once the copy landed.
  function copy(b) {
    navigator.clipboard.writeText(b.dataset.c).then(() => {
      document.querySelectorAll('.cmd.ok').forEach(x => x.classList.remove('ok'));
      b.classList.add('ok');
      clearTimeout(timer);
      timer = setTimeout(() => b.classList.remove('ok'), 1600);
    }).catch(() => {});
  }
  document.querySelectorAll('.cmd').forEach(b => b.onclick = () => copy(b));
  function filter() {
    const words = q.value.trim().toLowerCase().split(/\\s+/).filter(Boolean);
    const re = words.length ? new RegExp('(' + words.map(safe).join('|') + ')', 'gi') : null;
    first = null;
    rows.forEach(r => {
      const said = [...r.querySelectorAll('[data-t]')].map(e => e.dataset.t).join(' ').toLowerCase();
      const hit = words.every(w => said.includes(w));
      r.classList.toggle('none', !hit);
      r.querySelectorAll('[data-t]').forEach(e => e.innerHTML = re
        ? esc(e.dataset.t).replace(re, '<mark>$1</mark>') : esc(e.dataset.t));
      if (hit && !first) first = r.querySelector('.cmd');
    });
    document.querySelectorAll('.skf').forEach(f => f.classList.toggle('none', !f.querySelector('.sr:not(.none)')));
    document.querySelector('.nomatch').style.display = first ? 'none' : 'block';
    hm.innerHTML = !words.length ? all : first ? '↵ copies <b>' + esc(first.dataset.c) + '</b>' : 'No match';
  }
  // What I filtered by outlives a reload, as a skill's head changing brings.
  const kept = () => sessionStorage.setItem('skills-filter', q.value);
  q.addEventListener('input', () => { kept(); filter(); });
  q.addEventListener('keydown', e => {
    if (e.key === 'Enter' && first && q.value.trim()) copy(first);
    if (e.key === 'Escape') { q.value = ''; kept(); filter(); }
  });
  q.value = sessionStorage.getItem('skills-filter') || '';
  if (q.value) filter();
})();
</script>
"""


def render() -> str:
    found = heads()
    primary, groups = "", []
    for digit, fam, skills in families(found):
        if not skills:
            continue
        mark = ((f'<span class="dg">{digit}</span>' if digit else "")
                + (page.icon(fam, 14) if fam in ICONED else ""))
        title = fam.replace("-", " ").capitalize() if digit else "No family"
        rows = "".join(line(s) for s in skills)
        section = (f'<section class="skf"><div class="skh">{mark}<b>{page.esc(title)}</b></div>'
                   + (f'<div class="across">{rows}</div>' if not digit else rows) + '</section>')
        if digit:
            groups.append(section)
        else:
            primary = section
    key = hashlib.sha1(repr(found).encode()).hexdigest()[:12]
    find = (f'<label class="find">{page.icon("filter", 14)}<input id="q" spellcheck="false" '
            'aria-label="Filter the skills" placeholder="Filter: a command, what it does"></label>')
    body = (STYLE + f'<div class="first">{primary}</div><div class="sk">{"".join(groups)}</div>'
            '<p class="nomatch">No skill\'s command or intent holds that.</p>' + SCRIPT + page.watch(key))
    return page.render("00-skills", [("", body)],
                       page.head("skills", "", find, f'<span class="hm" id="hm">{len(found)} skills</span>'),
                       refresh=0)
