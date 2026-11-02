#!/usr/bin/env python3
"""shell.py — what a typed shell command runs, read without running it.

hooks/guard.py judges a command before it runs, for every session. It
reads it here, the one way.

It reads what is typed, down into $(...), backticks, bash -c, eval and a
heredoc a shell reads. Each simple command comes out flat, with its
assignments and the folder it runs in, as far as the text says. A value
held in a variable is unknown unless the text sets it, so a reader of
the result treats an unknown folder as unknown, never as safe.

Imported, never run.
"""

import os
import re

SHELLS = {"bash", "sh", "zsh", "dash", "ksh"}
# The words that only launch the command after them.
LAUNCHED = {"nohup", "time", "exec", "command", "builtin", "caffeinate", "then",
            "do", "else", "elif", "if", "while", "until", "!", "{", "}"}

# A substitution's text stands in its word as \0N\0, N its place in the list.
SUB = re.compile(r"\x00(\d+)\x00")
OPS = ("&&", "||", ";;", "|&", ";", "&", "|", "(", ")")
REDIRECT = ("<<<", "<<-", "<<", "&>>", "&>", ">>", ">&", "<&", "<>", ">|", "<", ">")


def closing(text: str, i: int) -> int:
    """Where the $( opened just before i closes, quotes and nesting kept."""
    depth, quote = 1, ""
    while i < len(text):
        c = text[i]
        if quote:
            if c == "\\" and quote == '"':
                i += 2
                continue
            if c == quote:
                quote = ""
        elif c in "'\"":
            quote = c
        elif c == "\\":
            i += 2
            continue
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return len(text)


def scan(text: str) -> tuple:
    """Words and operators, quotes taken off, in order.

    Returns the tokens and the inner texts. A token is ("w", word),
    ("op", op), ("redir", op) or ("in", n): inner text n starts there. An
    inner text is a substitution, or a heredoc's body, kept with the words
    of the command it feeds.
    """
    tokens, inner, heredocs = [], [], []
    word, i, n = None, 0, len(text)

    def end():
        nonlocal word
        if word is not None:
            tokens.append(("w", word))
            word = None

    def add(s: str):
        nonlocal word
        word = (word or "") + s

    def substitution(start: int, stop: int) -> str:
        inner.append(("sub", text[start:stop], None))
        tokens.append(("in", len(inner) - 1))
        return f"\x00{len(inner) - 1}\x00"

    while i < n:
        c = text[i]
        if c == "\\":
            if i + 1 < n and text[i + 1] == "\n":
                i += 2
                continue
            add(text[i + 1:i + 2])
            i += 2
        elif c in " \t\r":
            end()
            i += 1
        elif c == "#" and word is None:
            while i < n and text[i] != "\n":
                i += 1
        elif c == "\n":
            end()
            i += 1
            for delim, feeds in heredocs:
                body = []
                while i < n:
                    j = text.find("\n", i)
                    line = text[i:] if j < 0 else text[i:j]
                    i = n if j < 0 else j + 1
                    if line.strip() == delim:
                        break
                    body.append(line)
                inner.append(("heredoc", "\n".join(body), feeds))
                tokens.append(("in", len(inner) - 1))
            heredocs = []
            tokens.append(("op", ";"))
        elif c == "'":
            j = text.find("'", i + 1)
            j = n if j < 0 else j
            add(text[i + 1:j])
            i = j + 1
        elif c == "$" and text.startswith("$'", i):
            j = i + 2
            while j < n and text[j] != "'":
                j += 2 if text[j] == "\\" else 1
            add(text[i + 2:j])
            i = j + 1
        elif c == '"':
            i += 1
            add("")
            while i < n and text[i] != '"':
                if text[i] == "\\" and i + 1 < n:
                    add(text[i + 1])
                    i += 2
                elif text.startswith("$(", i):
                    j = closing(text, i + 2)
                    add(substitution(i + 2, j))
                    i = j + 1
                elif text[i] == "`":
                    j = text.find("`", i + 1)
                    j = n if j < 0 else j
                    add(substitution(i + 1, j))
                    i = j + 1
                else:
                    add(text[i])
                    i += 1
            i += 1
        elif text.startswith("$(", i):
            j = closing(text, i + 2)
            add(substitution(i + 2, j))
            i = j + 1
        elif c == "`":
            j = text.find("`", i + 1)
            j = n if j < 0 else j
            add(substitution(i + 1, j))
            i = j + 1
        elif c in "<>" or (c == "&" and text.startswith("&>", i)):
            # A number right before is the descriptor, never a word.
            if word is not None and word.isdigit():
                word = None
            end()
            op = next(o for o in REDIRECT if text.startswith(o, i))
            i += len(op)
            tokens.append(("redir", op))
            if op in ("<<", "<<-"):
                while i < n and text[i] in " \t":
                    i += 1
                j = i
                while j < n and text[j] not in " \t\n;&|<>()":
                    j += 1
                delim = text[i:j].strip("'\"")
                i = j
                tokens.append(("w", delim))
                heredocs.append((delim, current(tokens)))
        elif any(text.startswith(o, i) for o in OPS):
            end()
            op = next(o for o in OPS if text.startswith(o, i))
            tokens.append(("op", op))
            i += len(op)
        else:
            add(c)
            i += 1
    end()
    return tokens, inner


def current(tokens: list) -> list:
    """The words of the command the tokens are in the middle of."""
    words = []
    for kind, value in reversed(tokens):
        if kind == "op":
            break
        if kind == "w":
            words.append(value)
    return list(reversed(words))


def commands(tokens: list) -> list:
    """Simple commands, in order, each ("cmd", words, inner ids), with a
    subshell's edges as ("(",) and (")",). A redirection's target is no
    word of its command."""
    out, words, ins, skip = [], [], [], False
    for kind, value in tokens:
        if kind == "redir":
            skip = True
        elif kind == "w":
            if skip:
                skip = False
            else:
                words.append(value)
        elif kind == "in":
            ins.append(value)
        else:
            skip = False
            if words or ins:
                out.append(("cmd", words, ins))
            words, ins = [], []
            if value in ("(", ")"):
                out.append((value,))
    if words or ins:
        out.append(("cmd", words, ins))
    return out


def core(words: list) -> tuple:
    """A command's own words, past its assignments and the words that only
    launch it: sudo, env, nohup, timeout, xargs and the like. Returns the
    words and the assignments."""
    assigns, i = {}, 0
    while i < len(words):
        w = words[i]
        name = os.path.basename(w)
        if re.match(r"[A-Za-z_][A-Za-z0-9_]*=", w):
            k, _, v = w.partition("=")
            assigns[k] = v
            i += 1
        elif name in LAUNCHED:
            i += 1
        elif name in ("sudo", "env", "nice"):
            i += 1
            while i < len(words) and words[i].startswith("-"):
                i += 2 if words[i] in ("-u", "-n", "-g") else 1
        elif name == "timeout":
            i += 1
            while i < len(words) and words[i].startswith("-"):
                i += 2 if words[i] in ("-s", "-k") else 1
            i += 1
        elif name == "xargs":
            i += 1
            while i < len(words) and words[i].startswith("-"):
                i += 2 if words[i] in ("-I", "-n", "-P", "-L", "-s", "-E", "-d", "-J", "-R") else 1
        else:
            break
    return words[i:], assigns


class Reader:
    """Every simple command a typed text runs, flat, each with the folder
    it runs in, as far as the text says."""

    def __init__(self):
        self.found = []
        self.vars = {}

    def read(self, text: str, cwd, depth: int = 0) -> None:
        if depth > 6:
            return
        tokens, inner = scan(text)
        stack = []
        for item in commands(tokens):
            if item[0] == "(":
                stack.append(cwd)
                continue
            if item[0] == ")":
                cwd = stack.pop() if stack else cwd
                continue
            _, words, ins = item
            for n in ins:
                kind, body, feeds = inner[n]
                fed = core(feeds)[0] if feeds else []
                if kind == "sub" or (fed and os.path.basename(fed[0]) in SHELLS):
                    self.read(body, cwd, depth + 1)
            words, assigns = core(words)
            for k, v in assigns.items():
                self.vars[k] = self.value(v, inner)
            if not words:
                continue
            name = os.path.basename(words[0])
            if name in SHELLS:
                flag = next((k for k, w in enumerate(words[1:], 1)
                             if re.fullmatch(r"-[a-z]*c[a-z]*", w)), None)
                if flag is not None and flag + 1 < len(words):
                    self.read(self.text(words[flag + 1], inner), cwd, depth + 1)
            elif name == "eval":
                self.read(" ".join(self.text(w, inner) for w in words[1:]), cwd, depth + 1)
            elif name in ("cd", "pushd"):
                cwd = self.path(words[1] if len(words) > 1 else "~", cwd, inner)
            elif name == "popd":
                cwd = None
            self.found.append((words, assigns, cwd, inner))

    def text(self, word: str, inner: list) -> str:
        """A word as the shell would run it, each substitution back as $(...)."""
        return SUB.sub(lambda m: f"$({inner[int(m.group(1))][1]})", word)

    def value(self, word: str, inner: list) -> str | None:
        """What an assignment holds, when the text says. A mktemp holds a
        folder outside this project. Anything else computed is unknown."""
        m = SUB.fullmatch(word)
        if m:
            body = inner[int(m.group(1))][1].strip()
            return "/tmp/mktemp" if re.match(r"mktemp\b", body) else None
        return None if "\x00" in word else word

    def path(self, word: str, cwd, inner: list):
        """A folder a command names, or None when the text cannot say."""
        if re.fullmatch(r"\$\{?\w+\}?", word) and word.strip("${}") in self.vars:
            word = self.vars[word.strip("${}")]
            if word is None:
                return None
        word = re.sub(r"\$\{?(\w+)\}?", lambda m: self.vars.get(m.group(1))
                      or os.environ.get(m.group(1)) or "\x01", word)
        if "\x00" in word or "\x01" in word:
            return None
        word = os.path.expanduser(word)
        if not os.path.isabs(word):
            if cwd is None:
                return None
            word = os.path.join(cwd, word)
        return os.path.normpath(word)
