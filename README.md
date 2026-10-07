# Diffdunlin

Bounded read-only UTF-8 text comparison: insert/delete/replace groups, exact line-ending awareness, optional ignore-trailing-spaces/tabs mode, and JSON reports. Never edits a source file or applies a patch.

Python 3.9+, standard library only. No network or dependencies.

## Run locally

This app is published in a private GitHub repository. Download its ZIP while signed into the owner account, extract it and open a terminal inside the source folder.

```text
python3 diffdunlin.py
python3 diffdunlin.py before.txt after.txt
python3 diffdunlin.py before.txt after.txt --ignore-trailing
python3 diffdunlin.py before.txt after.txt --output changes.json
python3 -m unittest -v
bash app-store.sh install
bash app-store.sh run
```

Outputs refuse to overwrite any existing path, including source files. JSON reports include changed source lines, so they carry the source's privacy and audience restrictions. Keep them private. No repository, automatic syncing, background checks or persistent history is created by running this app.

## Exactness and limits

UTF-8 only, maximum 1 MiB and 5000 lines per input. Regular files, not devices/FIFOs. Symlinks may resolve to a regular file; this is not an adversarial-path sandbox. NUL bytes and invalid UTF-8 are rejected. Use stable copies; reads are sequential, not an atomic pair snapshot.

Line terminators are preserved. CRLF differs from LF, and a missing final newline differs from a final newline. Trailing mode ignores only spaces/tabs before the preserved terminator or end-of-line. It does not ignore leading/internal whitespace, newline style or final-newline presence. `raw_equal` remains false when bytes-as-text differ even if ignored trailing whitespace makes `comparison_equal` true.

JSON change ranges are zero-based, half-open `[start,end]`; an insertion has an empty old range and deletion an empty new range. These are text sequence ranges, not offsets in bytes or a patch-file format. Matching uses Python SequenceMatcher, not a guarantee of globally minimal edit distance. Repeated content can produce valid but unexpected alignments. Worst-case repetitive comparisons may take time despite the input cap. No code-aware syntax or semantic equivalence claims.

Terminal output escapes line endings/control characters and truncates individual lines at 500 characters. Display caps changed lines at 100. JSON keeps full changed lines and all groups. Reported line counts use Python splitlines, which recognizes some Unicode line separators. Input BOM is treated as a character, not silently removed.

CLI exits 0 for comparison-equal, 1 for differences, 2 for errors. Interactive mode returns to the menu after a result. Root marker/version files opt in to store integration. The current public-only Pi App Store cannot discover private repositories; authenticated store support is not verified.

18 tests cover line-ending differences, final newline, exact ranges, optional whitespace handling, Unicode, FIFO/binary rejection, source preservation, overwrite refusal and CLI status. Linux tested; real Pi/non-Linux platforms untested.
