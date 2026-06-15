# Gro Wai GoGo

Gro Wai GoGo is a tiny arcade-style playground for checking simple game
validation files. "Gro Wai" is used here as a playful phrase for lively fun:
collect coins, dodge rivals, and unlock hidden bonus characters.

## Allowed

- generic syntax checks;
- small game examples;
- dependency and packaging checks;
- temporary validation files with playful names.

## Not Allowed

- credentials, endpoints, or local paths;
- unrelated project names or internal labels;
- logs, artifacts, or local notes;
- files that are not safe to show in public CI output.

## Temporary Files

- Use playful file, function, class, and test names.
- Keep any local mapping outside this repository.
- Keep Actions logs safe to read publicly.
- Remove temporary files after the validation run is complete.

## Scaffold

| Path | Role |
| --- | --- |
| [workflows/](workflows/) | Workflow notes. |
| [tests/](tests/) | Test notes. |
| [fixtures/](fixtures/) | Small game examples. |
| [scripts/](scripts/) | Helper scripts. |
