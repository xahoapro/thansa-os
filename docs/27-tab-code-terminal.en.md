# Code Group: Terminal Right in the Dashboard

*[Tiếng Việt](27-tab-code-terminal.md) · **English***

**Code** is a separate group on the navigation bar - a programmer's workspace for Thansa. The first item in the group is **Terminal**: a real command line, running on the exact machine running Thansa, open right in the browser. No need to open SSH in another window anymore.

## What This Feature Is

Terminal here is a **real pseudo-terminal from the OS**, not simulated. Meaning:

- Runs any command you'd type over SSH: `git pull`, `ls`, `tail -f`, `pip install`, `agy`, `claude auth login`...
- Runs full-screen programs: `htop`, `vim`, `nano`, `less`.
- Has colors, Tab completion, command history (arrow keys), `Ctrl+C` kills just the command, not the whole session.
- Resize the window and the shell knows right away - text doesn't break into jumbled lines.

The Code group is built to expand: right now it only has **Terminal**, other dev tools will become more items in the same group later.

## Where to Find It in Thansa

1. Open the Thansa dashboard (default port 7777).
2. Left navigation rail, open the **Code** group, click the **Terminal** item.
3. Terminal opens and connects automatically. Click the black area and type like a normal terminal.

Shell starts in the **HOME directory of the user running Thansa** - just like a normal machine terminal, great for the main job of this tab: installing and logging into CLIs (`agy`, `codex login`...). Need to go to a brain? Type `cd "$JAVIS_BRAIN"` - this variable always points to the current brain.

## Top Bar

| Thing | Meaning |
|---|---|
| Circle dot + status text | Green = running. Red = connection lost (Thansa re-connects). Gray = shell exited. |
| Path | The directory the shell is in when opened. Narrow screens hide it to make room for buttons. |
| **Clear** | Clear the screen, like the `clear` command. |
| **New Session** | Close the current session (kill the shell) and open a fresh one. Use when shell freezes or you want a clean start. |

## Session Keeps Running When You Leave the Tab

This is the most important point for daily use: **switching pages or reloading the page DOESN'T kill the shell.**

- Running `npm install` and click away to the Chat page? The command keeps running. Come back to the Code tab and you see the old screen showing where it got to.
- Lose network, shut down machine, F5? Thansa re-connects to the same session.
- Nobody comes back within **30 minutes** and Thansa closes the session so you don't forget a process running forever.
- Want to close right away? Click **New Session** or type `exit`.

Maximum **4 sessions** at once. Hit the limit and Thansa tells you clearly instead of silently opening more.

## Simplified Mode on Windows

Python on Windows doesn't have a pseudo-terminal, so the Code tab runs in **simplified mode** and shows a warning line right on the window:

- Type a whole line and hit Enter, command runs and output streams back. Backspace works, `Ctrl+C` kills the command.
- **No** Tab completion, **no** arrow key command history, **no** full-screen programs (`vim`, `htop`).

Linux, macOS, and every Docker setup run full mode.

## Who Can Get In

Terminal is the place to run any command on the server - the highest permission the dashboard can give. So:

- Only **a logged-in browser** gets in. API tokens (type `jvs_...` for scripts and CLIs) **cannot** open terminal, even with full permission.
- When Thansa runs public (VPS, Docker), login is required, so terminal sits behind that same gate. See [Security & Account](14-bao-mat-tai-khoan.md).
- The shell inherits the server's environment variables, including secrets from `.env`. Just like owning the machine, but worth knowing when you loan the screen.
- Want to turn it off entirely? Set `JAVIS_TERMINAL=0` and restart Thansa. The Code tab will show a message saying it's off instead of an empty frame.

## Environment Variables

| Variable | Meaning | Default |
|---|---|---|
| `JAVIS_TERMINAL` | `0`/`off`/`false`/`no` = turn it off entirely | On |
| `JAVIS_TERMINAL_SHELL` | Path to the shell to run | `$SHELL`, fall back to `bash`/`sh`. Windows: `powershell.exe` then `cmd.exe` |
| `JAVIS_TERMINAL_CWD` | Directory to open in | HOME of the user running Thansa |

See [.env Configuration](16-cau-hinh-env.md) for how to set variables.

## Common Problems

**Terminal tab shows "Terminal is off on this machine".** Server has `JAVIS_TERMINAL=0`. Remove that line from `.env` and restart Thansa.

**Says "Already have 4 terminal sessions".** An old session is still alive in another browser tab. Click **New Session** on that tab, or wait 30 minutes for Thansa to clean up.

**Text broken across lines, table borders shifted.** Click in the terminal frame and resize the browser window once - it'll re-measure. If still off, type `clear`.

**Typed Tab, no suggestions.** You're in simplified mode (Windows). That's a system limit, not a config issue.

**Shell quits right when it opens.** Check that `JAVIS_TERMINAL_SHELL` points to a real executable, and the directory at `JAVIS_TERMINAL_CWD` exists.

## Related

- [05 - File Management](05-quan-ly-tep-tin.md) - browse and edit in the same directory using the GUI.
- [24 - Thansa CLI (terminal)](24-cli-terminal.md) - the flip side: type `thansa "..."` from your machine's terminal.
- [14 - Security & Account](14-bao-mat-tai-khoan.md) - the login gate in front of the Code group.
- [16 - .env Configuration](16-cau-hinh-env.md) - every environment variable.
