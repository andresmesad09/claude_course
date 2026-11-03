# Diagrams

Three views of `second_brain`: how the code is organized, how you call it, and what using it looks like day to day.

## 1. Package Overview

Every file and function in `src/second_brain/`, grouped into components.

- **Solid arrows** are function calls.
- **Dashed arrows** are imports between files, or files being read and written.
- **Double-bordered boxes** list what each file imports.

```mermaid
---
title: Package overview — files, functions and imports
config:
  flowchart:
    nodeSpacing: 25
    rankSpacing: 45
---
flowchart LR
    subgraph entry["Entry points"]
        script["pyproject.toml<br/>script: second_brain"]
        dunder_main["__main__.py<br/>python -m second_brain"]
        dunder_init["__init__.py<br/>empty package marker"]
    end

    subgraph app["app.py — CLI and logging"]
        app_imports[["imports: click · loguru<br/>python-dotenv · sys · datetime"]]
        fn_main["main()<br/>logger.catch → exit 1"]
        fn_cli["cli()<br/>click group"]
        subgraph commands["Commands"]
            fn_new["new(text)"]
            fn_list["list_command()"]
            fn_show["show(number)"]
        end
        subgraph logsetup["Logging setup"]
            fn_conf["configure_logging()<br/>LOG_FORMAT"]
            fn_patch["_add_short_level()"]
            fn_short["short_level()<br/>LEVEL_ABBREVIATIONS"]
        end
    end

    subgraph notes["notes.py — note storage"]
        notes_imports[["imports: os · re · pathlib"]]
        fn_dir["notes_dir()<br/>DEFAULT_DIR_NAME"]
        fn_save["save_note()"]
        fn_render["render_note()"]
        fn_fname["note_filename()"]
        fn_slug["slugify()<br/>MAX_SLUG_LENGTH"]
        fn_bynum["note_by_number()"]
        fn_listnotes["list_notes()"]
    end

    subgraph disk["Files read and written"]
        file_env[(".env")]
        file_log[("app.log")]
        file_notes[("notes folder<br/>*.md files")]
    end

    %% Imports between files
    dunder_main -. "imports main" .-> fn_main
    app_imports -. "from second_brain.notes import<br/>notes_dir · save_note<br/>list_notes · note_by_number" .-> notes_imports

    %% Entry points and the CLI group
    script --> fn_main
    fn_main --> fn_cli
    fn_cli --> fn_conf
    fn_cli --> fn_new
    fn_cli --> fn_list
    fn_cli --> fn_show
    fn_conf --> fn_patch --> fn_short

    %% Calls from app.py into notes.py
    fn_new --> fn_dir
    fn_new --> fn_save
    fn_list --> fn_listnotes
    fn_show --> fn_bynum
    fn_save --> fn_render
    fn_save --> fn_fname --> fn_slug
    fn_bynum --> fn_listnotes

    %% Filesystem
    fn_cli -. "load_dotenv()" .-> file_env
    fn_conf -. "writes" .-> file_log
    fn_save -. "writes" .-> file_notes
    fn_listnotes -. "reads" .-> file_notes
```

A few connections are left out to keep the chart readable:

- `list_command()` and `show()` also call `notes_dir()`, and `show()` also calls `list_notes()` to count the notes in its error message.

## 2. Entry Points and Arguments

The two ways to start the CLI, every command and argument, and what each one does, with its exit code.

```mermaid
---
title: Entry points, arguments and outcomes
config:
  flowchart:
    nodeSpacing: 25
    rankSpacing: 45
---
flowchart LR
    subgraph start["How you start it"]
        run_script["second_brain …"]
        run_module["python -m second_brain …"]
        env_vars[/".env or shell:<br/>SECOND_BRAIN_DIR<br/>LOG_LEVEL · LOG_FILE"/]
    end

    subgraph wrapper["main() and the cli() group"]
        main_catch["main()<br/>crash → log + exit 1"]
        group_cb["cli() callback<br/>load .env, set up logging"]
    end

    subgraph args["Commands and arguments"]
        a_new["new TEXT<br/>string, required"]
        a_list["list<br/>no arguments"]
        a_show["show NUMBER<br/>integer ≥ 1"]
        a_help["--help<br/>or no command"]
    end

    subgraph behind["What happens"]
        b_new{"TEXT empty?"}
        b_list["list_notes()<br/>newest first"]
        b_show{"note #NUMBER<br/>exists?"}
        b_help["Click prints help<br/>no callback runs"]
    end

    subgraph outcome["Output and exit code"]
        o_saved["Saved path<br/>exit 0"]
        o_new_err["can't be empty<br/>exit 2"]
        o_listed["numbered list<br/>or No notes yet.<br/>exit 0"]
        o_shown["note content<br/>exit 0"]
        o_show_err["No note #N<br/>exit 2"]
        o_help["help text<br/>exit 0 for --help<br/>exit 2 for no command"]
    end

    run_script --> main_catch
    run_module --> main_catch
    env_vars -.-> group_cb

    main_catch --> group_cb
    group_cb --> a_new
    group_cb --> a_list
    group_cb --> a_show
    main_catch --> a_help

    a_new --> b_new
    b_new -- "no" --> o_saved
    b_new -- "yes" --> o_new_err
    a_list --> b_list --> o_listed
    a_show --> b_show
    b_show -- "yes" --> o_shown
    b_show -- "no" --> o_show_err
    a_help --> b_help --> o_help

    %% Keep --help in the arguments column
    group_cb ~~~ a_help
```

`cli()` is a Click group, and its callback runs whenever a command is given, before that command's arguments are checked. `--help`, plain `second_brain` and unknown commands print help or an error without loading `.env` or setting up logging. A command's own `--help`, such as `new --help`, still runs the callback first. `show 0`, `show abc` and `show -1` are rejected by Click before `show()` runs, also with exit code 2.

## 3. Example User Flow

A typical session: capture an idea, find it again later, and read or copy it.

```mermaid
---
title: Example user flow — capture, find, read
config:
  flowchart:
    nodeSpacing: 25
    rankSpacing: 40
---
flowchart LR
    subgraph capture["1. Capture"]
        cmd_new(["second_brain new<br/>'Cache API responses'"])
        saved["Saved …/2026-11-02-<br/>163019-cache-api-responses.md"]
    end

    subgraph find["2. Find (later)"]
        cmd_list["second_brain list"]
        numbered["1. …-cache-api-responses.md<br/>2. …-buy-a-keyboard.md"]
    end

    subgraph read["3. Read"]
        cmd_show["second_brain show 1"]
        valid{"Number in<br/>the list?"}
        content["# Cache API responses<br/><br/>Cache API responses"]
        error["No note #9.<br/>You have 2 notes."]
    end

    subgraph reuse["4. Reuse"]
        copy["show 1 | pbcopy<br/>or open the .md file"]
    end

    cmd_new --> saved --> cmd_list --> numbered --> cmd_show --> valid
    valid -- "yes" --> content --> copy
    valid -- "no" --> error
    error -. "run list again" .-> cmd_list
```

Numbers in `list` are newest first, so they shift by one every time you save a new note. If in doubt, run `list` again before `show`. With no notes yet, `list` prints `No notes yet.`, and `show` reports `You have 0 notes`.
