# Exact visible Lexical prompt text

Live evidence: one paste into an empty editor produced one P per original newline. Root innerText inserts an extra newline between P blocks, causing false hash mismatch; all 11 paragraph strings match the immutable file exactly. No repaste allowed.

Contract: serialize the observed all-P DOM layout by joining each visible paragraph innerText with one newline, preserve internal whitespace/BR/blank paragraphs and fall back to root innerText for other structures. Do not collapse arbitrary whitespace or alter the source prompt. Use the same reader for paste verification and read-prompt. Add optional read-prompt --file for non-mutating exact normalized hash comparison against a bound project file. Preserve unique editor and no-append guards. Unit-test DOM serialization and live existing prompt without any second paste.

## Result
123 tests and source/live deployment parity PASS. Existing B01 prompt readback exactly matches immutable SHA without repaste. First provider card accepted In queue. Video QC remains separate.
