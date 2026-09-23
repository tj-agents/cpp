# Base utility scripts

No scripts are defined. `templates/` holds the shared scaffold templates consumed by the
G++, MSVC and Win32 scaffolds; they ship inside each of those packages under
`resources/base/utility/scripts/`, so a package never depends on another installation.
A toolchain template at the same relative path replaces the shared one.
