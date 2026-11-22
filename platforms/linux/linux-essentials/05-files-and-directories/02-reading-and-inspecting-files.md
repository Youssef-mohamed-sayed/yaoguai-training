# Reading and Inspecting Files


## Learning objectives
- Read text files using suitable tools.
- Inspect the beginning or end of large files.
- Understand why binary files should not be dumped blindly.

## Commands
```bash
cat file.txt
less file.txt
head -n 10 file.txt
tail -n 20 file.txt
tail -f application.log
file unknown.bin
stat unknown.bin
```
`cat` concatenates files to standard output and is best for short files. `less` supports paging and searching (`/pattern`, `n`, `N`, `q`). `head` and `tail` show selected ends. `tail -f` follows a changing file; `Ctrl-C` stops following.

Use `file` before assuming a file is text. Printing arbitrary binary data with `cat` can produce terminal control characters and unreadable output.

## Hands-on practice
- Inspect `/etc/os-release` with `cat` and `less`.
- Show its first three lines with `head`.
- Create a log file and append two lines; follow it with `tail -f` in one terminal while appending from another.
- Hint: use `>>` to append rather than overwrite.

## Common mistakes
- Using `cat` on huge files.
- Treating binary output as meaningful text.
- Forgetting to stop `tail -f`.

## Key takeaways
Choose the reader based on file size and purpose. Identify unknown files before displaying them.

## Further practice
Use `less` to search a log for `error` and inspect context around matches.

## References
- [GNU Coreutils](https://www.gnu.org/software/coreutils/manual/)
- [less manual](https://greenwoodsoftware.com/less/)
