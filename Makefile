# Second Brain automation (macOS / Linux).
# Thin wrappers around the Claude Code CLI in headless mode, so ingestion can be
# scripted / scheduled without opening an interactive session.
# Windows users: use ./sb.ps1 instead (same verbs).
#
# Requires: the `claude` CLI on PATH (https://docs.claude.com/claude-code).
# --permission-mode acceptEdits lets Claude write wiki files without prompting.

CLAUDE ?= claude
PERM   ?= --permission-mode acceptEdits

.PHONY: help ingest process-inbox query lint ui capture study gaps explain

help:
	@echo "Second Brain commands:"
	@echo "  make ingest SRC=\"path-or-URL\"   Ingest one source into the wiki"
	@echo "  make process-inbox               Triage raw/inbox.md into the wiki"
	@echo "  make query Q=\"your question\"     Ask the wiki; answer saved to output/"
	@echo "  make lint                        Health-check the wiki"
	@echo "  make capture TEXT=\"a thought\"    Append a line to raw/inbox.md (no LLM)"
	@echo "  -- learning --"
	@echo "  make study [N=10]                Spaced-repetition session (interactive)"
	@echo "  make explain C=\"a concept\"       Feynman mode (interactive)"
	@echo "  make gaps                        Learning health check -> output/study-plan.md"
	@echo "  make ui                          Launch the Streamlit interface"

ingest:
	@test -n "$(SRC)" || (echo "Usage: make ingest SRC=\"path-or-URL\"" && exit 1)
	$(CLAUDE) -p "/ingest $(SRC)" $(PERM)

process-inbox:
	$(CLAUDE) -p "/process-inbox" $(PERM)

query:
	@test -n "$(Q)" || (echo "Usage: make query Q=\"your question\"" && exit 1)
	$(CLAUDE) -p "/query $(Q)" $(PERM)

lint:
	$(CLAUDE) -p "/lint" $(PERM)

# Pure-text capture: no LLM, just prepend to the inbox under the header line.
capture:
	@test -n "$(TEXT)" || (echo "Usage: make capture TEXT=\"a thought\"" && exit 1)
	@printf '%s\n' "$(TEXT)" | cat - raw/inbox.md > raw/.inbox.tmp && mv raw/.inbox.tmp raw/inbox.md
	@echo "Captured to raw/inbox.md"

# Interactive (open a live Claude session so it can ask you questions).
study:
	$(CLAUDE) "/study $(N)" $(PERM)

explain:
	@test -n "$(C)" || (echo "Usage: make explain C=\"a concept\"" && exit 1)
	$(CLAUDE) "/explain $(C)" $(PERM)

gaps:
	$(CLAUDE) -p "/gaps" $(PERM)

ui:
	streamlit run app/app.py
