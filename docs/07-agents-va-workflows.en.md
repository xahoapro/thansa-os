# Agents & Workflows

*[Tiếng Việt](07-agents-va-workflows.md) · **English***

This is where you create specialized AI assistants (Agents) and combine them into automated workflows. Example: a research agent, a writer agent, a verification agent, chained together as "research > write > verify" running once to produce a result.

## What is this feature

- **Agent** is an "AI employee" with a fixed role. Each agent consists of: a name, a role description, detailed work instructions (system prompt), a list of skills (skill) allowed to use, a **running model**, and a **personal memory** accumulated over time. You can choose models from both **Claude** (Sonnet/Opus/Haiku/Fable - running via Thansa) and **ChatGPT/Codex** (GPT-5.x - running via Codex CLI, requires ChatGPT logged in on machine/VPS). Both can read/write files in vault and use MCP. The agent's model is applied REALLY when the workflow runs.
  - Safety note: when the workflow runs **automatically in the background** (Kanban dispatcher, restricted tool mode), the agent always uses Thansa to maintain safe tool limits - even if you choose Codex model. Codex model only applies when you press **▶ Run** directly on the Workflows page.
- **Workflow** is a chain of multiple steps, each step assigned to an agent to complete one task. The result of the previous step can flow to the next step. You can add an additional **verification step**: another agent plays the role of error checker, by default assumes the result is wrong and must prove otherwise; if not passed, the workflow automatically fixes it a few times.
- All agents and workflows are saved as **files .md in vault** (the brain you've chosen), so you can view them, edit by hand, and Thansa can also create them by voice through chat.

Related: to choose a model for an agent see [Models & engine](10-models-va-engine.md); to create and enable/disable skills to assign to agents see [Skills](06-skills.md).

## Where to open in Thansa

On the left navigation bar of the dashboard (default at port 7777), open the **Capabilities** group. This group has 4 items, two of which are used on this page:

- **Agents**: manage AI assistants.
- **Workflows**: manage chains.

(The other two items in the group are Skills and Plugins.) Click to open the corresponding page. All content on both pages belongs to one brain (brain) currently selected: if you change brains, the list of agents and workflows also changes accordingly.

## First: click "Create template" to have a working example

If you're just starting out and have nothing, the fastest way is to use the built-in template set.

1. Open the **Workflows** page.
2. In the top right corner, click **Create template** button.
3. Thansa will create 3 sample agents and 1 sample workflow in advance (all 3 agents are pre-set with **Sonnet** model):
   - Agent **Researcher**: specializes in research, finding materials, synthesizing sources (pre-assigned deep-research skill).
   - Agent **Writer**: specializes in writing articles from research materials (pre-assigned salepage-16-buoc skill).
   - Agent **Verifier**: provides independent evaluation, always assumes the result is wrong and must prove otherwise; does not create content, only grades.
   - Workflow **Research → Write (with verification)**: step 1 research, step 2 write then verify independently, auto-fixes up to 2 times if not passed.

After having the template, you can run it immediately (see "Run a workflow" section below), or open it to edit according to your needs to understand how it works.

Note: the two skills that the template agent references (deep-research, salepage-16-buoc) are just pre-assigned names. If your brain doesn't have those two skills yet, the agent will still run normally, just without the detailed guidance that comes with them.

## Create an Agent (step by step, via form)

1. Open the **Agents** page.
2. Click **+ Agent** button in the top right corner. An editing frame opens on the right side of the screen.
3. Fill in the following fields:

| Field | Meaning | Fill suggestion |
|---|---|---|
| **Name** | Agent name, shown on the card. Required. | Ex: "Email specialist" |
| **Role (short description)** | A sentence describing what the agent does. | Ex: "Write sales emails, friendly tone" |
| **System prompt (detailed work method)** | Detailed instructions on how the agent works, principles, desired output. | Ex: writing rules, forbidden words, output format |
| **Skills** | List of skills available in vault, check to allow agent to use. | Choose skills that match the role |
| **Model** | Selection field with 8 options, see table below. | Sonnet for balance, Opus for deep reasoning, Haiku for fast and cheap |

4. Click **Save**. If you forget to enter Name, Thansa will prompt "Enter name".
5. The new agent card appears in the list with a 🤖 icon, accompanied by the model name and skill labels assigned. If no skills are assigned, the card shows "no skills assigned".

Note about Skills field: the skills list is taken from the skill folder of vault. If vault has no skills yet, the frame will say "Vault has no skills in skills/ - can still create agent, assign skills later." You can still create the agent normally and go back to assign later. To create skills see [Skills](06-skills.md).

### What's in the Model field

| Choice | Group | Run by |
|---|---|---|
| **Default (per CLI)** | (no group) | See explanation right below table |
| **Sonnet** | Claude (Thansa) | Thansa |
| **Opus** | Claude (Thansa) | Thansa |
| **Haiku** | Claude (Thansa) | Thansa |
| **Fable** | Claude (Thansa) | Thansa |
| **GPT-5.5** | ChatGPT (Codex - requires ChatGPT login) | Codex CLI |
| **GPT-5.4** | ChatGPT (Codex - requires ChatGPT login) | Codex CLI |
| **GPT-5.3 Codex** | ChatGPT (Codex - requires ChatGPT login) | Codex CLI |

Below the Model field is a note: "Agent runs via the provider's CLI: choose Claude → Thansa; choose ChatGPT → Codex (requires ChatGPT logged in on machine/VPS). Both can read/write vault files + use MCP."

**"Default (per CLI)" actually does what:** if left empty, Thansa takes the **secondary model** you set on the **Models** page before (only when secondary model is a Claude model); if there's no Claude secondary model, it falls back to the CLI's default model. If you want an agent to always run on exactly one model regardless of general configuration, choose that model directly for it instead of leaving it empty.

### Agent's personal memory and run log

Besides the `.md` file, each agent also has two things in the `memory/agents/<slug>/` folder of the brain:

- **`MEMORY.md` - personal memory.** Each time the agent runs, Thansa reads this file and inserts it directly into the agent's system prompt under the title `# Your memory:`. This is a place to accumulate what the agent needs to remember long-term: custom conventions, customer lists, noted mistakes. This file has **two write sources**: you write by hand, and the agent **self-enriches when running** - at the end of a task, if a lesson can be reused, the agent proposes and Thansa records it in the `## Lessons (self-taught)` section. Thansa (not the model) holds the pen so there are hard fences: auto-removes duplicate lessons, keeps only the 15 newest lines so memory becomes dense rather than long, and anything you write by hand outside that section is never touched. Meaning the agent gets smarter with each use, no background job sweeps everything.
- **`runs/` - run log.** Each time a workflow step finishes running (including the verification step), Thansa adds an entry to `runs/<YYYY-MM-DD>.md` consisting of run time, assigned task, and result (condensed). This is a place to look back "what did this agent do yesterday" without having to reopen the tracking panel. This raw log doesn't go into the brain's git.

Both are regular text files: open, read and edit by hand via [File management](05-quan-ly-tep-tin.md). To teach an agent to remember something, just write directly to `memory/agents/<slug>/MEMORY.md` and the next run it will know. This is why the Agents page when empty says "No agents. Click + Agent to create (role + skills + personal memory)."

Distinction: this memory is of **just one agent**; Thansa's shared memory about you and the business is in `memory/MEMORY.md` and `memory/facts/`, see [Second Brain: memory, Wiki, INGEST](13-second-brain-bo-nho-wiki.md).

### Edit or delete agent

- **Edit**: on the agent card, click **Edit**, make changes then click **Save**.
- **⤓ Export**: package the agent (with its skills) into a `.zip` file to share, see "Sharing" section at the end of the page.
- **Delete**: click **Delete**, confirm in the "Delete agent ...?" dialog. Note: if a workflow is using this agent, that step will point to a non-existent agent, so after deleting check related workflows. Deleting an agent does **not** delete the `memory/agents/<slug>/` folder, so old memory and logs remain on disk.

## Create a Workflow (step by step, via form)

You need at least one agent before creating a workflow. If you don't have any agents, when you click create workflow Thansa will say "No agents yet. Create Agent first (Agents tab) or click Create template."

1. Open the **Workflows** page.
2. Click **+ Workflow** in the top right corner.
3. Fill in:
   - **Name**: workflow name. Required.
   - **Description**: a line saying what this workflow does (not required but recommended; this line appears on the workflow card).
4. In the **Steps** section (each step = 1 agent · use {{input}} and {{prev}}), each step is a block consisting of:
   - **Task** field: describe what this step should do. In the task, you can use two special variables:
     - `{{input}}` = input you type when clicking run workflow.
     - `{{prev}}` = result of the immediately preceding step.
   - **Verification** part (optional): choose an agent to play error checker for this step, and number of correction attempts allowed. Leave as default "- no verification -" if not needed. Number of corrections defaults to 1, allows 0 to 5.
5. Click **+ Step** to add a new step.
6. Click **Save**. If you forget to enter Name, Thansa prompts "Enter name". New workflow saves in ready state (active).

### Header line of a step

Each step has a header line, read from left to right:

| Element | Meaning |
|---|---|
| Serial number | 1, 2, 3... in exact run order |
| Summary line | "agent name · task" condensed on one line |
| Agent selection field | Change the agent responsible for this step |
| **↑** | Push step up one level (grayed at first step) |
| **↓** | Push step down one level (grayed at last step) |
| **✕** | Delete this step (at END of header line) |

**Collapse and expand step:** click on the header line (blank space, not button or field) to collapse or expand the body of that step. When you open an existing workflow to **edit**, all steps default to collapsed so you see the full chain; click on a step to expand it for editing. **Newly created** workflow has only one step so it's open.

Unfinished text won't be lost when you collapse/expand, change order or delete other steps - Thansa temporarily saves each step's contents before each redraw.

### Example: a 2-step workflow

- Step 1: agent **Researcher**, task: `Research thoroughly the topic: {{input}}. Find sources, synthesize key insights.`
- Step 2: agent **Writer**, task: `Write a complete article about '{{input}}' based on the following research:` then new line and add `{{prev}}`. In the Verification section, choose agent **Verifier**, number of corrections 2.

This is exactly the "Research → Write (with verification)" template workflow that the Create template button creates.

### Read a workflow card

Each workflow displays as a card, consisting of:

- Header line: workflow name, a status badge (**● Ready** when active or **Archived** when inactive), and step count like "N steps".
- Workflow description line (if you filled in the Description field).
- Chain diagram: steps numbered 01, 02, ... Each box shows **task** as main text, agent name as sub-text below. In the task, variables are translated to words for readability: `{{input}}` appears as "input", `{{prev}}` appears as "previous step result"; any other variable shows its name literally.
- Button line: **▶ Run**, **Edit**, **Archive** or **Activate**, **⤓ Export**, **Delete**.

### Enable, disable, edit, delete workflow

- **Enable/disable**: click **Archive** to disable workflow (button changes to **Activate**). Archived workflow won't run: **▶ Run** button is grayed out. Click **Activate** to re-enable.
- **Edit**: click **Edit**, modify steps then **Save**.
- **Delete**: click **Delete**, confirm in "Delete workflow ...?" dialog.

## Run a workflow (step by step)

1. On the workflow card in **● Ready** state, click **▶ Run**.
2. An input field appears asking for input, like "Input for ... (ex: article topic)". Type the content you want to input (the value of `{{input}}`), then confirm. If you click cancel, the workflow won't run.
3. A tracking panel slides out on the right side of the screen, displaying real-time progress:
   - Top shows "▶ workflow name", next line shows total step count.
   - Status badge on the card changes to **⏳ Running...**, then **⏳ Step 1/N**, **⏳ Step 2/N**, ...
   - In the chain diagram, the running step lights up; completed step gets a checkmark.
   - For each step, you see the agent name, task, and result text appearing gradually as the agent works. If the agent calls a tool, there's a note ⚙ with the tool name.
4. If a step has verification, after the agent finishes you'll see "🔍 ... verifying..." (with retry count if repeating). Verification result is one of two:
   - **✓ Passed**: step completes, flows to next step.
   - **✗ Not passed**: with brief reason. Workflow automatically reruns that step (line "↻ Fix attempt ...") per feedback, up to the limit you set. Fix attempt SEES old result plus feedback to improve further, doesn't restart from scratch.
   - If fix attempts run out but still not passed, the step still ends but gets a warning "⚠ Not passed verification after number of attempts - review the result". At this point you should read the output yourself.
5. When all complete, the end of the panel shows "✓ Workflow complete".
6. Click the close button of the panel to close it. Closing the panel also stops any running part.

After each step completes, Thansa records the result in the run log of the agent responsible for that step (`memory/agents/<slug>/runs/`), so you can review it even after closing the panel.

## Create agent and workflow by voice (via chat)

You don't have to use the form. In the chat frame with Thansa (see [Chat & voice](02-tro-chuyen-va-giong-noi.md)), you can give voice commands, for example:

- "Create agent specialized in writing sales emails."
- "Create workflow research then write article."
- "Add editing step to workflow X."

When you do, Thansa automatically writes the corresponding .md file to vault, automatically sets slug in lowercase no-diacritics, auto-assigns fitting skills from available skills, and if a workflow mentions an agent that doesn't exist it creates that agent first. After finishing, Thansa briefly reports which files were created/modified. Go back to the Agents or Workflows page and you'll see it right away, no extra action needed.

This way is convenient when you can describe your intention by voice but don't want to fill out a form, or want to modify multiple steps at once.

## Where agents and workflows are saved

In the new brain structure, each agent is a `agents/<slug>.md` file and each workflow is a `workflows/<slug>.md` file. `slug` is the name in lowercase with hyphens, no diacritics (example "write email" becomes `write-email`).

**Old brain structure not yet converted** keeps these two folders in `Javis/agents/` and `Javis/workflows/`. Thansa auto-detects: if the new folders exist it uses them, otherwise it uses the old path. So if you open the File management page and don't see `agents/` at the brain root, look inside `Javis/`.

Since these are text files, you can open them via [File management](05-quan-ly-tep-tin.md) to view or edit by hand. File structure:

- Agent: frontmatter section contains name, role, list of skills, model; body is detailed system prompt. Personal memory and run logs lie outside this file, in `memory/agents/<slug>/`.
- Workflow: frontmatter contains name, state (active or off), description and list of steps (each step has agent, task, and optional verification agent plus number of corrections).

Edit the file and save, then the Agents / Workflows page automatically recognizes new content on next load.

## Tips

- **Always separate a verification step for important stages.** Set the verification agent to be a different agent from the one doing the work, since it's forced into the role of "assume result is wrong". This is how to reduce AI rushing or making things up.
- **Each step does exactly one thing.** Don't stuff "research and write and post" into one step. Break down to be easy to control and fix each phase.
- **Use `{{prev}}` to connect.** If a later step wants to use the previous step's output, you must mention `{{prev}}` in the task, otherwise the agent won't see the prior output.
- **Rearrange order using ↑/↓ instead of delete and redo.** If you mix up the order, just push steps up or down, content follows intact.
- **Set correction count reasonably.** 1 to 2 times usually enough. Set too high and the workflow runs long and wastes credit when the result is hard to meet.
- **Choose model by task.** Heavy reasoning step (analyze, verify) uses Opus; simple, many-quantity step uses Haiku for speed and savings. Details in [Models & engine](10-models-va-engine.md).
- **Assign skills in the right place.** Agent is only strong with fitting skills. For example a sales page writer agent should get the sales page writing skill. Manage skills at [Skills](06-skills.md).
- **Use personal memory for repeated instructions.** Same reminder has to be repeated each run, write straight to `memory/agents/<slug>/MEMORY.md`, no need to stuff it in system prompt.

## Sharing: Export / Import (agent, skill, workflow)

You can package an agent, skill or workflow into **one `.zip` file** to send to others, and receive files from others into your brain.

- **Export:** each agent / skill / workflow card has **⤓ Export** button. Click to download a `.zip` package. This package **self-includes dependencies** so the receiver can run immediately: exporting a workflow includes all agents the workflow uses and those agents' skills; exporting an agent includes that agent's skills. **System** skills are not packaged since every brain already has them.
- **Import:** each **Agents / Skills / Workflows** page has **⤒ Import** button. Choose a `.zip` file (Thansa package), individual `.md` file (agent/workflow), or **Thansa skill `.skill` package** (Thansa auto-recognizes `SKILL.md` in package and puts it in the right skill folder) to bring into the currently selected brain. Thansa asks whether to **overwrite** when there's a name collision: click Cancel to keep the old one (import only new items), click OK to overwrite with the version in the package. After importing, Thansa reports what was imported, what was skipped.
- **Safety:** when importing, Thansa blocks unusual paths in the package (no writing outside agent/skill/workflow folders) and limits file size to prevent malicious files. Still, only import packages from sources you trust, since skill content is instructions for AI to follow.

Note: exported package contains only definition files. **Agent's personal memory and run logs don't go with the package** - recipient gets role and skills, not memories.

## Quick reference: buttons and status

| You see | Meaning / action |
|---|---|
| **+ Agent** / **+ Workflow** | Open editing frame to create new |
| **Create template** (Workflows page) | Create 3 sample agents + 1 sample workflow run right away |
| **⤒ Import** | Bring `.zip` / `.md` / `.skill` package into currently selected brain |
| **⤓ Export** | Download `.zip` package with dependencies to share |
| **● Ready** | Workflow is enabled, can run |
| **Archived** (badge) | Workflow is disabled, ▶ Run button grayed out |
| **Archive** / **Activate** (button) | Disable / enable workflow |
| **N steps** | Number of steps in the chain |
| **▶ Run** | Run workflow, ask for input then open tracking panel |
| **↑** / **↓** (in step) | Change step order |
| **✕** (end of step header line) | Delete that step |
| **⏳ Step i/N** | Running up to step i |
| **✓ Passed** / **✗ Not passed** | Result of one verification round |
| **↻ Fix attempt k** | Re-running step per verification feedback |
| **⚠ Not passed verification after number of attempts** | Out of correction attempts but still not passed, need to review result yourself |
| **✓ Workflow complete** | All done |

## Common trouble

- **Click + Workflow says "No agents yet".** You haven't created an agent. Go to Agents page to create at least one, or click Create template on Workflows page to get example set.
- **▶ Run button grayed out, can't click.** Workflow is in Archived state. Click **Activate** to change back to ● Ready then run again.
- **List empty, says "No workflows" or "No agents".** This is initial state. Click **Create template** (on Workflows) or **+ Agent** / **+ Workflow** to start. If you just changed brains and see empty, confirm you're in the right brain.
- **Open Edit workflow and see all steps collapsed, think content is lost.** It's not lost. Editing workflow defaults to collapse for full view; click on step header line to expand it.
- **Skills field empty when creating agent.** Vault has no skills yet in the skill folder. Create agent first, create skills later on [Skills](06-skills.md) page then come back to assign.
- **Choose GPT-5.x model but agent still runs with Claude.** By design when workflow runs automatically in background: that mode forces Claude to maintain tool limits. To use Codex click **▶ Run** directly on workflow card, and machine must already have ChatGPT logged in.
- **Leave Model field empty but agent runs with strange model.** Empty field means take secondary model from Models page before. To force specific model, choose it directly for the agent.
- **Can't find `agents/` folder in brain.** Old brain keeps them in `Javis/agents/` and `Javis/workflows/`. Open File management page and look in the `Javis` folder.
- **Step shows warning "⚠ Not passed verification after number of attempts".** The working agent has fixed to limit but verifier still grades not passed. Read the step output yourself; consider clarifying task description, switching to stronger model, or increasing correction attempts then re-run.
- **Tracking panel stops mid-run.** Closing tracking panel cuts off running part. If network hiccups, panel may also freeze; open the workflow again and click ▶ Run to restart.
- **Page keeps showing "Loading...".** Server slow or not running. Check Thansa is up on port 7777, then reload page. If still error, see [Troubleshooting & FAQ](17-khac-phuc-su-co.md).

## Related

- [Skills](06-skills.md) - create, enable/disable and assign skills to agents.
- [Plugins](20-plugins.md) - fourth item in Capabilities group, for tools that run real code.
- [Models & engine](10-models-va-engine.md) - choose primary model, secondary model and providers.
- [Tasks / Kanban](21-viec-kanban.md) - where workflows run automatically per task.
- [Second Brain: memory, Wiki, INGEST](13-second-brain-bo-nho-wiki.md) - distinguish agent's personal memory from Thansa's shared memory.
- [File management](05-quan-ly-tep-tin.md) - open and edit agent, workflow, memory files by hand.
