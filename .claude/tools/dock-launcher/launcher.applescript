-- The project's app, in my Dock. One click opens my workspace: its editor, and iTerm2.
--
-- open.py, beside the app, does the work. Homebrew's python3 runs it,
-- because 1100 needs a newer one than macOS ships.
--
-- Bringing iTerm2 forward is asked here, last. macOS lets the app I just
-- clicked hand the front to another. iTerm2 asking for itself is refused
-- while another app is in front.
--
-- build.py compiles this into the app, named for the project in .claude/project.json.

on run
	set here to do shell script "dirname " & quoted form of (POSIX path of (path to me))
	do shell script "/opt/homebrew/bin/python3 " & quoted form of (here & "/open.py")
	tell application id "com.googlecode.iterm2" to activate
end run
