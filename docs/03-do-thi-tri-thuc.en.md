# Knowledge Graph

*[Tiếng Việt](03-do-thi-tri-thuc.md) · **English***

The knowledge graph transforms notes in your brain into a visual network. Each dot is a Markdown file; each thread is a wikilink `[[...]]` between two notes.

The graph uses 2D canvas, not WebGL, and doesn't need to load libraries from the internet. It displays all notes even without connections, supports timelapse, and can be completely turned off in Settings.

See also where this data is created: [Second Brain: Memory, Wiki, INGEST](13-second-brain-bo-nho-wiki.md).

## What the graph shows

- **Each node = one note** in the selected brain. Nodes with more connections appear larger.
- **Each thread = one wikilink `[[...]]`** between two notes.
- **Node color = immediate parent folder** of the file.
- **Category labels** around the graph show the largest folders, their note count and percentage of your vault.
- **AGENTS · SKILLS · WORKFLOWS bar** at the bottom shows how many capabilities you have. Click a section to jump to its management page.

## Opening the graph

1. Open the dashboard, default at `http://<your-machine>:7777`.
2. On the left navigation bar, open **Assistants** group then select **Thansa**.
3. The graph is in the center area of the screen.

When you navigate to another page or open the note editor, the graph pauses. Come back to the **Thansa** page or close the editor to resume.

On screens under 860px wide, Thansa prioritizes a lightweight interface and goes straight to the **Chat** page.

## Turn graph on or off

1. Open **System → Settings**.
2. Open **Interface & Brain**.
3. Find the **Brain Graph** card.
4. Click **Turn graph off** or **Turn graph on**.

When off, Thansa doesn't build the graph and goes straight to the **Chat** page. The setting is saved on the server.

## Select brain

The brain selector is on the top bar, next to THANSA OS. Switching brains updates the graph, memory, agent/skill/workflow counts, file tree, and chat.

Three small buttons beside the selector:

| Button | Function |
|---|---|
| ➕ | Create new brain in the `brains` folder |
| 🗑 | Delete the selected brain after confirming the exact name. Cannot delete **Brain Default** |
| 📁 | Choose any folder on your computer as the source |

External folders are saved in the selector list for later. When you click 🗑 on an external source, Thansa removes it from the menu but doesn't delete the data on disk.

## Navigate and read the graph

- **Drag the background** to move the network.
- **Scroll wheel** to zoom in or out.
- **Drag a node** to reposition temporarily; when released, it returns to equilibrium.
- **Hover over a node** to show the note name, highlight that node and its neighbors, dim the rest.
- **Click a node** to open the note in the editor.
- **Click a category label** to spotlight only that folder's cluster. Click the label again or click the background to remove the filter.

After the physics stabilize, Thansa automatically centers the entire network in the view.

## Open and edit notes from nodes

1. Click a node.
2. The note editor opens right over the graph area.
3. Read, edit, or upload the file normally.
4. Click ✕ or press Esc to close and restart the graph.

With `.md` files, the editor has two modes **Edit** and **Source**. Toolbar has:

| Button | What it does |
|---|---|
| 💾 Save | Write content to file; supports `Ctrl+S` |
| ✎ | Rename the file |
| 🗑 | Delete the note after confirming |
| ↗ | Open raw file in new tab |
| ⤓ Download | Download file to your computer |
| ⛶ | Expand or collapse the editor |
| ✕ | Close the editor |

Clicking a node only opens the file, doesn't send a question to chat. To ask Thansa to summarize or analyze, make a request in the chat.

## Hide overlay information layer

The eye icon button in the top right of the graph area toggles:

- category labels;
- AGENTS · SKILLS · WORKFLOWS bar.

This setting is remembered in your browser and syncs across tabs.

## Timelapse "brain's life"

The clock button below the eye button plays back how your brain grew:

1. Graph starts empty.
2. Notes appear in the order files were created, spaced 0.16 seconds apart.
3. A thread only appears once both endpoints exist.
4. Click the button again to stop; the complete graph restores.

## Node color by folder

Thansa uses a contrast palette and assigns colors in order to each immediate parent folder. Number prefixes like `07 - ` are ignored when comparing names, so `07 - Wiki` and `Wiki` are treated as the same folder.

When you switch light/dark theme, the graph switches palettes but keeps the same color group for each folder.

## Statistics line

On the top bar there's a line like:

```text
42 notes · 87 connections
```

- **notes**: number of notes currently displayed, including notes without wikilinks.
- **connections**: total number of valid wikilinks between notes.

Other states are **Loading...**, **Error: ...**, or warning that the graph library didn't load.

## Real-time updates

The graph monitors your brain and auto-updates when notes or links are added:

1. New nodes pop up and shrink to normal size.
2. Statistics line updates and flashes slightly.

If the monitoring connection drops, Thansa reconnects automatically. A periodic scan also catches any missed changes.

## Reacts to voice and status

- When you speak or Thansa reads, nodes swell slightly with volume level.
- When Thansa switches to **THINKING**, the network changes rhythm.
- At rest, nodes breathe gently with offset phases.

## How the graph is built

1. Thansa scans up to 2,000 `.md` files from the selected source.
2. Each file becomes a node; node name is the filename without extension.
3. Thansa finds wikilinks `[[...]]`; each link to another file becomes an edge.
4. Format `[[folder/Name|alias]]` is supported; Thansa takes the filename part to connect.
5. Thansa counts notes per folder and picks up to 8 largest folders for labels.

## Common issues

- **Graph empty or few nodes**: check the selected brain and verify the source has `.md` files.
- **Can't load graph library**: reload the page. The library is on Thansa's server itself, so errors usually mean the page loaded partially or static files aren't being served.
- **Statistics show "Error"**: external source may have changed path or you no longer have read permission.
- **Graph frozen**: check if you're on another page, the editor is open, screen is narrow, or you turned the graph off in Settings.
- **Entering Thansa but goes straight to Chat**: screen is narrow or graph is turned off.
- **New node not appearing**: wait for monitoring to reconnect, or switch brains then back to reload.

## Related

- [Chat & Voice](02-tro-chuyen-va-giong-noi.md)
- [Second Brain: Memory, Wiki, INGEST](13-second-brain-bo-nho-wiki.md)
- [File Management](05-quan-ly-tep-tin.md)
- [Agents & Workflows](07-agents-va-workflows.md)
- [Skills](06-skills.md)
- [Back up brain to GitHub](18-sao-luu-github.md)
- [Troubleshooting & FAQ](17-khac-phuc-su-co.md)
