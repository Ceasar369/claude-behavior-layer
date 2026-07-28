-- The boot button.
--
-- One click brings the session environment up:
--   1. the status engine, started only if the port is dead
--   2. your workspace, if you supplied open-workspace.sh
--   3. one window holding the status page
--
-- Every step ENSURES, never adds. Click it five times and you still have one
-- engine and one window. That is the whole design rule — the button is a state
-- the machine converges on, not a sequence it replays.
--
-- Step 3 has two paths. If iTerm2 is installed AND you have made a browser
-- profile named "Bus", you get a split window: a terminal on the left, the
-- status page on the right. Anything else — no iTerm2, no plugin, no profile —
-- falls back to opening the page in your default browser. The fallback needs no
-- setup at all, so this works on a machine that has never heard of iTerm2.
--
-- Settings live in launcher.conf beside this file. See launcher.conf.example.

on run
	set toolDir to do shell script "dirname " & quoted form of (POSIX path of (path to me))
	set cfgCmd to "PORT=8787; PROFILE=Bus; cfg=" & quoted form of (toolDir & "/launcher.conf") & "; [ -f \"$cfg\" ] && . \"$cfg\"; "

	set thePort to do shell script cfgCmd & "echo \"$PORT\""
	set theProfile to do shell script cfgCmd & "echo \"$PROFILE\""
	set theURL to "http://127.0.0.1:" & thePort & "/"

	-- 1. The engine. Only when the port is dead, so a second click is harmless.
	set httpCode to do shell script "/usr/bin/curl -s -o /dev/null -w '%{http_code}' " & quoted form of theURL & " 2>/dev/null || echo 000"
	if httpCode is not "200" then
		-- A login shell, so a Homebrew or pyenv python3 is on PATH.
		do shell script "/bin/zsh -lc " & quoted form of ("cd " & quoted form of toolDir & " && BUS_PORT=" & thePort & " nohup python3 server.py >/dev/null 2>&1 &")
		delay 1.2
	end if

	-- 2. Your workspace. Optional: supply open-workspace.sh and make it
	--    executable. Absent, this step does nothing at all.
	set opener to toolDir & "/open-workspace.sh"
	try
		do shell script "[ -x " & quoted form of opener & " ] && " & quoted form of opener & " || true"
	end try

	-- 3. The window. Try the iTerm2 split first; fall back to the browser.
	--
	--    ENSURE one, never add one — a second click must not open a second
	--    window. It is identified by its Bus-profile pane, unique to this window.
	--    iTerm is checked through System Events first, because naming it inside
	--    a `tell` block would launch it and defeat the test.
	set didSplit to false
	set itermInstalled to false
	try
		do shell script "[ -d /Applications/iTerm.app ]"
		set itermInstalled to true
	end try

	if itermInstalled then
		tell application "System Events"
			set itermUp to exists (processes whose bundle identifier is "com.googlecode.iterm2")
		end tell
		if not itermUp then
			do shell script "/usr/bin/open -a iTerm"
			delay 1.5
		end if
		-- Controlling iTerm needs macOS Automation permission. Without it every
		-- send throws -1743. That is not a failure worth surfacing — it just
		-- means we take the browser path instead.
		try
			tell application "iTerm"
				set busWindow to missing value
				repeat with w in windows
					repeat with t in tabs of w
						repeat with s in sessions of t
							try
								if (profile name of s) is theProfile then set busWindow to w
							end try
						end repeat
					end repeat
				end repeat
				if busWindow is missing value then
					-- Left pane: a terminal on the default profile.
					set busWindow to (create window with default profile)
					-- Right pane: the status page. Throws if the profile is absent.
					tell current session of busWindow
						split vertically with profile theProfile
					end tell
				end if
				try
					select busWindow
				end try
				activate
			end tell
			set didSplit to true
		on error
			set didSplit to false
		end try
	end if

	if not didSplit then
		do shell script "/usr/bin/open " & quoted form of theURL
	end if
end run
