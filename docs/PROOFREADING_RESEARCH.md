# Proofreading research

Status: research note for a later build slice. Not an active implementation contract.

## Goal

Add fast local proofreading without putting spellcheck or grammar work on EZmd's launch, Open,
typing, cursor, Save, or Markdown-persistence hot paths.

The intended user experience is:

- spelling feedback appears quickly while writing;
- grammar/style feedback appears after a short pause;
- the editor stays responsive even when proofreading is slow;
- normal writing does not require a network service;
- proofreading underlines are presentation only and never become document formatting.

## Disposable LanguageTool measurements

These numbers came from local disposable spikes on October 5, 2026. They were not production
benchmarks and are not CI performance requirements.

Environment:

- language_tool_python 3.4.0
- LanguageTool 6.8
- Temurin Java 21.0.12.1+1

First-run setup:

- the test machine did not already have Java;
- a temporary JRE was installed outside the repository;
- the first LanguageTool launch downloaded about 259 MB;
- first startup including that download took about 158 seconds;
- cached startup took about 1.09 seconds.

Initial paragraph/document latency probe:

- 793-character paragraph: about 59 ms median over five checks;
- about 1 KB: 67 ms median;
- about 10 KB: 256 ms median;
- about 100 KB: 1.93 s median.

Memory observed in that probe:

- about 378 MiB Python + Java RSS after startup;
- about 1.74 GiB after the larger checks while LanguageTool remained alive.

A second stability probe kept one LanguageTool instance alive and performed 500 sequential
checks on 784-character paragraphs:

- startup RSS: 368.7 MiB;
- after 10 checks: 1,110.6 MiB;
- after 100 checks: 880.7 MiB;
- after 250 checks: 885.4 MiB;
- after 500 checks: 884.2 MiB;
- after 60 seconds idle: 884.3 MiB;
- median check latency: 23.9 ms;
- maximum individual latency: 2.09 s;
- shutdown was clean and left no Java child process.

The useful conclusion is narrow: local LanguageTool is fast enough for paragraph-sized background
checks, but too memory-heavy for routine whole-document checking or permanent eager startup.

## Proposed later architecture

Use two separate proofreading layers with different jobs.

### Fast spelling

Use a lightweight spelling library such as pyspellchecker for word-level spelling feedback.

Candidate behavior:

- do not initialize proofreading during application launch;
- check a finished word on space, punctuation, or Enter, or after a very small debounce;
- keep work limited to the word or small local text range that changed;
- show spelling diagnostics without modifying QTextDocument semantics.

The exact library still needs a production dependency/license review before adoption.

### Delayed grammar and style

Use local LanguageTool only for deeper grammar/style checks.

Candidate behavior:

1. Normal editing stays entirely on the native Qt document.
2. Restart a short idle timer while the user types.
3. After roughly 700-1000 ms without typing, copy only the changed paragraph text.
4. Send that plain string to a background worker.
5. Lazy-start LanguageTool in that worker when the first grammar check is actually needed.
6. Return ranges, messages, and suggestions to the UI thread.
7. Apply results only if they still belong to the current document revision.
8. Never let the worker mutate QTextDocument directly.

The exact delay is a UX tuning value, not a fixed contract.

## Resource policy

Do not keep the grammar engine alive merely because EZmd is open.

A later slice should evaluate an idle shutdown policy, likely on the order of a few minutes:

- grammar activity keeps LanguageTool warm;
- extended grammar inactivity shuts down the LanguageTool/Java process;
- the next grammar request restarts it in the background;
- disabling grammar checking shuts the process down rather than only hiding diagnostics.

This trades a roughly one-second cached restart for reclaiming hundreds of MiB when grammar is
not in use.

## Scope boundaries

A proofreading slice should initially avoid:

- checking the whole document on Open;
- checking the whole document after every pause;
- running LanguageTool on the UI thread;
- loading Java/LanguageTool before the editor is usable;
- storing spelling/grammar diagnostics in Markdown;
- changing document formatting to represent diagnostics;
- network grammar services as a normal requirement;
- proofreading work during Save or Markdown preflight.

For a large document, checking the changed/current paragraph is enough for the first slice.
Progressive idle checking of untouched paragraphs can be considered later only if real use shows
it is valuable.

## Presentation and stale results

Proofreading marks should behave like presentation overlays, not saved document state.

Background results should carry enough identity to detect stale work, for example a document
revision/generation plus the checked text range. If the user edits that paragraph before a slow
result returns, discard the stale result rather than underlining the wrong text.

Likely user controls:

- Check spelling
- Check grammar

Turning grammar off should stop the grammar worker/process when practical.

## Acceptance direction for a future build

When this becomes an approved build, define measurable behavior before implementation. At minimum:

- application launch remains fast with proofreading enabled;
- opening a document does not wait for LanguageTool;
- typing/cursor movement never wait for spellcheck or grammar;
- word-level spelling feedback feels immediate;
- grammar checks run only after a pause and off the UI thread;
- stale grammar results are discarded safely;
- diagnostics never alter saved Markdown;
- grammar can be disabled and its Java process released;
- no routine whole-document LanguageTool checks are performed.

Do not implement proofreading from this research note alone. Create a precise build contract when
the feature becomes the next approved slice.
