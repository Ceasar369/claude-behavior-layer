---
name: app-skill
description: Writes or changes a skill for my Claude app, and readies its ZIP for me to upload.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
argument-hint: "[what the app skill does, or which one changes and how — omit, and it asks me in one question]"
---

# App Skill

## Step 1 — Read where it lives, and Anthropic's rules

1. Read `knowledge/0010-playbook/0019-targeted/the-map/the-claude-app.md`. Its skills' folder is the home.
2. Read `claude-app-skills-2026-11-05/01-what-anthropic-says.md`, in this project's references folder, whole.
3. Where its pages disagree, meet the stricter one.

## Step 2 — Say it in one sentence

1. Write what the app skill does in my app, in one sentence.
2. Unclear → ask me one question, in prose.
3. A change → read its folder's `SKILL.md` whole first.
4. Change only the repo copy. Never send me to the app's editor.

## Step 3 — Name it

1. The name says what it does, in words I already say.
2. It meets the capture's rules for a name.
3. A name already in the home is refused, unless it is the one changing.

## Step 4 — Write its SKILL.md

1. Write `.claude/app-skills/<name>/SKILL.md`. The folder takes the name.
2. Its frontmatter holds `name` and `description`, nothing else.
3. The description says what it does, then when I ask for it, in my words.
4. Write it all as `.claude/rules/talking.md` rules, under "Writing for another reader".
5. The body: numbered steps, one instruction a line.
6. A connector's tool goes by the name its connector gives it.

## Step 5 — Check it

1. Run this. It prints the name's length, the description's, whether the name matches the folder, and the line count.

```
python3 -c 'import re,sys;d=sys.argv[1].rstrip("/");t=open(d+"/SKILL.md").read();m=dict(re.findall(r"^(name|description): *(.*)$",t,re.M));print(len(m.get("name","")),len(m.get("description","")),m.get("name")==d.split("/")[-1],len(t.splitlines()))' .claude/app-skills/<name>
```

2. Hold each number to the capture's rules.
3. A fault → fix it, and run it again. Three tries, then show me its lines.

## Step 6 — Zip it

1. Run `cd .claude/app-skills && rm -f <name>.zip && zip -rqX <name>.zip <name>`.
2. Run `unzip -l .claude/app-skills/<name>.zip`. Its top entry is `<name>/`.

## Step 7 — Hand me the upload

1. A changed skill → my first step deletes its old copy, as the capture's "Changing one" says.
2. Then the upload, as the capture's "Upload" names it, with the ZIP's whole path.
3. Then one line to say in a new chat, and what I should see.
4. Each step the capture leaves not found is marked unproven.
5. Your move: "Action: do steps 1 to N above."
