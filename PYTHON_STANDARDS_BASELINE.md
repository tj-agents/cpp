# Python standards baseline

Existing violations at `8d4641a9f7d1c48e788453977ab62060eb31222f` are baselined by exact authored file and rule. New files receive all enabled checks. Remove an exception when repairing its source. The tool configuration owns enforcement; this document records the rollout evidence and rationale.

## Ruff

Reason: preserve existing implementations during the standards rollout. Each row records the existing count and a representative required repair. No wildcard path or whole-rule ignores were added.

| File | Rule | Existing count | Required repair |
| --- | --- | ---: | --- |
| `.agents/gen_skill_routes.py` | `E501` | 21 | Line too long (102 > 88) |
| `.agents/gen_skill_routes.py` | `I001` | 1 | Import block is un-sorted or un-formatted |
| `.agents/hooks/session_context.py` | `E501` | 11 | Line too long (120 > 88) |
| `.agents/hooks/session_context.py` | `I001` | 1 | Import block is un-sorted or un-formatted |
| `.agents/hooks/session_context.py` | `PTH109` | 1 | `os.getcwd()` should be replaced by `Path.cwd()` |
| `.agents/hooks/tests/test_session_context.py` | `E501` | 11 | Line too long (97 > 88) |
| `.agents/hooks/tests/test_session_context.py` | `PLR6301` | 1 | Method `context` could be a function, class method, or static method |
| `.agents/hooks/tests/test_session_context.py` | `PT009` | 21 | Use a regular `assert` instead of unittest-style `assertEqual` |
| `.agents/hooks/tests/test_session_context.py` | `SIM117` | 1 | Use a single `with` statement with multiple contexts instead of nested `with` statements |
| `.agents/hooks/tests/test_session_context.py` | `TID251` | 2 | `importlib.util.spec_from_file_location` is banned: Import the installed public API; do not load another checkout by path. |
| `.agents/tests/test_attester_safety.py` | `E501` | 9 | Line too long (96 > 88) |
| `.agents/tests/test_attester_safety.py` | `I001` | 1 | Import block is un-sorted or un-formatted |
| `.agents/tests/test_attester_safety.py` | `PLR6301` | 1 | Method `test_attester_parses_as_powershell` could be a function, class method, or static method |
| `.agents/tests/test_attester_safety.py` | `PT009` | 14 | Use a regular `assert` instead of unittest-style `assertLess` |
| `.agents/tests/test_attester_safety.py` | `SIM112` | 2 | Use capitalized environment variable `SYSTEMROOT` instead of `SystemRoot` |
| `.agents/tests/test_attester_safety.py` | `TID251` | 1 | `unittest.TestCase` is banned: Use plain pytest functions and bare assertions. |
| `.agents/tests/test_canonical_names.py` | `E501` | 7 | Line too long (155 > 88) |
| `.agents/tests/test_canonical_names.py` | `I001` | 1 | Import block is un-sorted or un-formatted |
| `.agents/tests/test_canonical_names.py` | `PT009` | 19 | Use a regular `assert` instead of unittest-style `assertEqual` |
| `.agents/tests/test_canonical_names.py` | `TID251` | 1 | `unittest.TestCase` is banned: Use plain pytest functions and bare assertions. |
| `.agents/tests/test_capability_harness.py` | `B023` | 2 | Function definition does not bind loop variable `package` |
| `.agents/tests/test_capability_harness.py` | `E501` | 15 | Line too long (107 > 88) |
| `.agents/tests/test_capability_harness.py` | `I001` | 1 | Import block is un-sorted or un-formatted |
| `.agents/tests/test_capability_harness.py` | `PT009` | 18 | Use a regular `assert` instead of unittest-style `assertEqual` |
| `.agents/tests/test_capability_harness.py` | `SIM117` | 1 | Use a single `with` statement with multiple contexts instead of nested `with` statements |
| `.agents/tests/test_capability_harness.py` | `TID251` | 2 | `importlib.util.spec_from_file_location` is banned: Import the installed public API; do not load another checkout by path. |
| `.agents/tests/test_cpp_mixin_guidance.py` | `E501` | 10 | Line too long (98 > 88) |
| `.agents/tests/test_cpp_mixin_guidance.py` | `I001` | 1 | Import block is un-sorted or un-formatted |
| `.agents/tests/test_cpp_mixin_guidance.py` | `PT009` | 25 | Use a regular `assert` instead of unittest-style `assertIn` |
| `.agents/tests/test_cpp_mixin_guidance.py` | `TID251` | 1 | `unittest.TestCase` is banned: Use plain pytest functions and bare assertions. |
| `.agents/tests/test_cpp_structure.py` | `E501` | 2 | Line too long (104 > 88) |
| `.agents/tests/test_cpp_structure.py` | `I001` | 1 | Import block is un-sorted or un-formatted |
| `.agents/tests/test_cpp_structure.py` | `PT009` | 2 | Use a regular `assert` instead of unittest-style `assertIn` |
| `.agents/tests/test_cpp_structure.py` | `TID251` | 1 | `unittest.TestCase` is banned: Use plain pytest functions and bare assertions. |
| `.agents/tests/test_gpp_scaffold.py` | `E501` | 31 | Line too long (102 > 88) |
| `.agents/tests/test_gpp_scaffold.py` | `I001` | 1 | Import block is un-sorted or un-formatted |
| `.agents/tests/test_gpp_scaffold.py` | `PT009` | 37 | Use a regular `assert` instead of unittest-style `assertEqual` |
| `.agents/tests/test_gpp_scaffold.py` | `TID251` | 1 | `unittest.TestCase` is banned: Use plain pytest functions and bare assertions. |
| `.agents/tests/test_hook_contract.py` | `E501` | 10 | Line too long (99 > 88) |
| `.agents/tests/test_hook_contract.py` | `I001` | 1 | Import block is un-sorted or un-formatted |
| `.agents/tests/test_hook_contract.py` | `PT009` | 4 | Use a regular `assert` instead of unittest-style `assertEqual` |
| `.agents/tests/test_hook_contract.py` | `TID251` | 2 | `importlib.util.spec_from_file_location` is banned: Import the installed public API; do not load another checkout by path. |
| `.agents/tests/test_marketplace_contract.py` | `E501` | 26 | Line too long (90 > 88) |
| `.agents/tests/test_marketplace_contract.py` | `I001` | 1 | Import block is un-sorted or un-formatted |
| `.agents/tests/test_marketplace_contract.py` | `PT009` | 54 | Use a regular `assert` instead of unittest-style `assertEqual` |
| `.agents/tests/test_marketplace_contract.py` | `TID251` | 2 | `importlib.util.spec_from_file_location` is banned: Import the installed public API; do not load another checkout by path. |
| `.agents/tests/test_msvc_scaffold.py` | `E501` | 28 | Line too long (105 > 88) |
| `.agents/tests/test_msvc_scaffold.py` | `I001` | 1 | Import block is un-sorted or un-formatted |
| `.agents/tests/test_msvc_scaffold.py` | `PLR6301` | 1 | Method `run_scaffold` could be a function, class method, or static method |
| `.agents/tests/test_msvc_scaffold.py` | `PT009` | 32 | Use a regular `assert` instead of unittest-style `assertEqual` |
| `.agents/tests/test_msvc_scaffold.py` | `SIM112` | 1 | Use capitalized environment variable `PROGRAMFILES(X86)` instead of `ProgramFiles(x86)` |
| `.agents/tests/test_msvc_scaffold.py` | `TID251` | 1 | `unittest.TestCase` is banned: Use plain pytest functions and bare assertions. |
| `.agents/tests/test_provenance_pin_updates.py` | `E501` | 19 | Line too long (112 > 88) |
| `.agents/tests/test_provenance_pin_updates.py` | `I001` | 1 | Import block is un-sorted or un-formatted |
| `.agents/tests/test_provenance_pin_updates.py` | `PT009` | 42 | Use a regular `assert` instead of unittest-style `assertEqual` |
| `.agents/tests/test_provenance_pin_updates.py` | `SIM117` | 1 | Use a single `with` statement with multiple contexts instead of nested `with` statements |
| `.agents/tests/test_provenance_pin_updates.py` | `TID251` | 2 | `importlib.util.spec_from_file_location` is banned: Import the installed public API; do not load another checkout by path. |
| `.agents/tests/test_route_cli.py` | `E701` | 2 | Multiple statements on one line (colon) |
| `.agents/tests/test_route_cli.py` | `I001` | 1 | Import block is un-sorted or un-formatted |
| `.agents/tests/test_route_cli.py` | `PT009` | 3 | Use a regular `assert` instead of unittest-style `assertEqual` |
| `.agents/tests/test_route_cli.py` | `TID251` | 1 | `unittest.TestCase` is banned: Use plain pytest functions and bare assertions. |
| `.agents/tests/test_sync_generated_safety.py` | `E501` | 43 | Line too long (127 > 88) |
| `.agents/tests/test_sync_generated_safety.py` | `I001` | 1 | Import block is un-sorted or un-formatted |
| `.agents/tests/test_sync_generated_safety.py` | `PLR6301` | 1 | Method `config` could be a function, class method, or static method |
| `.agents/tests/test_sync_generated_safety.py` | `PT009` | 24 | Use a regular `assert` instead of unittest-style `assertEqual` |
| `.agents/tests/test_sync_generated_safety.py` | `SIM117` | 2 | Use a single `with` statement with multiple contexts instead of nested `with` statements |
| `.agents/tests/test_sync_generated_safety.py` | `TID251` | 3 | `importlib.util.spec_from_file_location` is banned: Import the installed public API; do not load another checkout by path. |
| `.agents/tests/test_validate_claude.py` | `E501` | 5 | Line too long (109 > 88) |
| `.agents/tests/test_validate_claude.py` | `I001` | 1 | Import block is un-sorted or un-formatted |
| `.agents/tests/test_validate_claude.py` | `PT009` | 6 | Use a regular `assert` instead of unittest-style `assertEqual` |
| `.agents/tests/test_validate_claude.py` | `TID251` | 2 | `importlib.util.spec_from_file_location` is banned: Import the installed public API; do not load another checkout by path. |
| `.agents/tests/test_versionless_packages.py` | `B023` | 1 | Function definition does not bind loop variable `target` |
| `.agents/tests/test_versionless_packages.py` | `E501` | 3 | Line too long (101 > 88) |
| `.agents/tests/test_versionless_packages.py` | `F401` | 1 | `json` imported but unused |
| `.agents/tests/test_versionless_packages.py` | `I001` | 1 | Import block is un-sorted or un-formatted |
| `.agents/tests/test_versionless_packages.py` | `PT009` | 3 | Use a regular `assert` instead of unittest-style `assertNotIn` |
| `.agents/tests/test_versionless_packages.py` | `SIM117` | 1 | Use a single `with` statement with multiple contexts instead of nested `with` statements |
| `.agents/tests/test_versionless_packages.py` | `TID251` | 2 | `importlib.util.spec_from_file_location` is banned: Import the installed public API; do not load another checkout by path. |
| `.agents/tests/test_win32_scaffold.py` | `E501` | 25 | Line too long (105 > 88) |
| `.agents/tests/test_win32_scaffold.py` | `I001` | 1 | Import block is un-sorted or un-formatted |
| `.agents/tests/test_win32_scaffold.py` | `PLR6301` | 1 | Method `convert` could be a function, class method, or static method |
| `.agents/tests/test_win32_scaffold.py` | `PT009` | 44 | Use a regular `assert` instead of unittest-style `assertEqual` |
| `.agents/tests/test_win32_scaffold.py` | `TID251` | 1 | `unittest.TestCase` is banned: Use plain pytest functions and bare assertions. |
| `.github/scripts/update_provenance_pins.py` | `C420` | 1 | Unnecessary dict comprehension for iterable; use `dict.fromkeys` instead |
| `.github/scripts/update_provenance_pins.py` | `E501` | 40 | Line too long (105 > 88) |
| `.github/scripts/update_provenance_pins.py` | `I001` | 1 | Import block is un-sorted or un-formatted |
| `.github/scripts/update_provenance_pins.py` | `N818` | 1 | Exception name `TrustRootChange` should be named with an Error suffix |
| `.github/scripts/update_provenance_pins.py` | `PTH123` | 1 | `open()` should be replaced by `Path.open()` |
| `.github/scripts/validate_claude.py` | `E501` | 8 | Line too long (100 > 88) |
| `.github/scripts/validate_claude.py` | `I001` | 1 | Import block is un-sorted or un-formatted |

## Ruff formatter

Exact existing files requiring formatting are excluded from the formatter during this rollout. Regenerate payloads after formatting authored source and then remove its exception. New files are checked.

- `.agents/gen_skill_routes.py`
- `.agents/hooks/session_context.py`
- `.agents/hooks/tests/test_session_context.py`
- `.agents/tests/test_attester_safety.py`
- `.agents/tests/test_canonical_names.py`
- `.agents/tests/test_capability_harness.py`
- `.agents/tests/test_cpp_mixin_guidance.py`
- `.agents/tests/test_cpp_structure.py`
- `.agents/tests/test_gpp_scaffold.py`
- `.agents/tests/test_hook_contract.py`
- `.agents/tests/test_marketplace_contract.py`
- `.agents/tests/test_msvc_scaffold.py`
- `.agents/tests/test_provenance_pin_updates.py`
- `.agents/tests/test_route_cli.py`
- `.agents/tests/test_sync_generated_safety.py`
- `.agents/tests/test_validate_claude.py`
- `.agents/tests/test_versionless_packages.py`
- `.agents/tests/test_win32_scaffold.py`
- `.github/scripts/update_provenance_pins.py`
- `.github/scripts/validate_claude.py`

## Mypy

Existing typing debt is baselined by exact module and diagnostic code, with its source file and count below. Add the missing annotations or fix the indicated type mismatch, then remove the corresponding module/code override. No wildcard modules or whole-module ignore was added.

| File | Module | Rule | Existing count | Required repair |
| --- | --- | --- | ---: | --- |
| `.agents/gen_skill_routes.py` | `gen_skill_routes` | `assignment` | 1 | Incompatible types in assignment (expression has type "tuple[str, ...]", variable has type "list[str]") |
| `.agents/gen_skill_routes.py` | `gen_skill_routes` | `type-arg` | 1 | Missing type arguments for generic type "dict" |
| `.agents/hooks/tests/test_session_context.py` | `test_session_context` | `arg-type` | 1 | Argument 1 to "module_from_spec" has incompatible type "ModuleSpec \| None"; expected "ModuleSpec" |
| `.agents/hooks/tests/test_session_context.py` | `test_session_context` | `assignment` | 1 | Incompatible types in assignment (expression has type "dict[Any, Any]", target has type "list[Any]") |
| `.agents/hooks/tests/test_session_context.py` | `test_session_context` | `no-any-return` | 1 | Returning Any from function declared to return "list[str]" |
| `.agents/hooks/tests/test_session_context.py` | `test_session_context` | `type-arg` | 1 | Missing type arguments for generic type "dict" |
| `.agents/hooks/tests/test_session_context.py` | `test_session_context` | `union-attr` | 2 | Item "None" of "ModuleSpec \| None" has no attribute "loader" |
| `.agents/hooks/tests/test_session_context.py` | `test_session_context` | `var-annotated` | 1 | Need type annotation for "declaration" |
| `.agents/tests/test_canonical_names.py` | `test_canonical_names` | `attr-defined` | 11 | "type[CanonicalNameTests]" has no attribute "payloads" |
| `.agents/tests/test_canonical_names.py` | `test_canonical_names` | `no-any-return` | 1 | Returning Any from function declared to return "dict[Any, Any]" |
| `.agents/tests/test_canonical_names.py` | `test_canonical_names` | `type-arg` | 1 | Missing type arguments for generic type "dict" |
| `.agents/tests/test_canonical_names.py` | `test_canonical_names` | `union-attr` | 3 | Item "None" of "Match[str] \| None" has no attribute "group" |
| `.agents/tests/test_capability_harness.py` | `test_capability_harness` | `arg-type` | 1 | Argument 1 to "module_from_spec" has incompatible type "ModuleSpec \| None"; expected "ModuleSpec" |
| `.agents/tests/test_capability_harness.py` | `test_capability_harness` | `no-untyped-def` | 5 | Function is missing a return type annotation |
| `.agents/tests/test_capability_harness.py` | `test_capability_harness` | `union-attr` | 2 | Item "None" of "ModuleSpec \| None" has no attribute "loader" |
| `.agents/tests/test_hook_contract.py` | `test_hook_contract` | `arg-type` | 1 | Argument 1 to "module_from_spec" has incompatible type "ModuleSpec \| None"; expected "ModuleSpec" |
| `.agents/tests/test_hook_contract.py` | `test_hook_contract` | `assignment` | 1 | Incompatible types in assignment (expression has type "Path", variable has type "str") |
| `.agents/tests/test_hook_contract.py` | `test_hook_contract` | `attr-defined` | 18 | "type[HookContractTests]" has no attribute "output" |
| `.agents/tests/test_hook_contract.py` | `test_hook_contract` | `operator` | 2 | Unsupported left operand type for / ("str") |
| `.agents/tests/test_hook_contract.py` | `test_hook_contract` | `union-attr` | 2 | Item "None" of "ModuleSpec \| None" has no attribute "loader" |
| `.agents/tests/test_marketplace_contract.py` | `test_marketplace_contract` | `arg-type` | 1 | Argument 1 to "module_from_spec" has incompatible type "ModuleSpec \| None"; expected "ModuleSpec" |
| `.agents/tests/test_marketplace_contract.py` | `test_marketplace_contract` | `attr-defined` | 22 | "type[MarketplaceContractTests]" has no attribute "marketplace" |
| `.agents/tests/test_marketplace_contract.py` | `test_marketplace_contract` | `no-any-return` | 1 | Returning Any from function declared to return "dict[Any, Any]" |
| `.agents/tests/test_marketplace_contract.py` | `test_marketplace_contract` | `no-untyped-call` | 1 | Call to untyped function "load_generator" in typed context |
| `.agents/tests/test_marketplace_contract.py` | `test_marketplace_contract` | `no-untyped-def` | 1 | Function is missing a return type annotation |
| `.agents/tests/test_marketplace_contract.py` | `test_marketplace_contract` | `type-arg` | 1 | Missing type arguments for generic type "dict" |
| `.agents/tests/test_marketplace_contract.py` | `test_marketplace_contract` | `union-attr` | 3 | Item "None" of "ModuleSpec \| None" has no attribute "loader" |
| `.agents/tests/test_provenance_pin_updates.py` | `test_provenance_pin_updates` | `arg-type` | 1 | Argument 1 to "module_from_spec" has incompatible type "ModuleSpec \| None"; expected "ModuleSpec" |
| `.agents/tests/test_provenance_pin_updates.py` | `test_provenance_pin_updates` | `index` | 1 | Unsupported target for indexed assignment ("object") |
| `.agents/tests/test_provenance_pin_updates.py` | `test_provenance_pin_updates` | `no-untyped-call` | 13 | Call to untyped function "git_blob" in typed context |
| `.agents/tests/test_provenance_pin_updates.py` | `test_provenance_pin_updates` | `no-untyped-def` | 20 | Function is missing a type annotation |
| `.agents/tests/test_provenance_pin_updates.py` | `test_provenance_pin_updates` | `union-attr` | 2 | Item "None" of "ModuleSpec \| None" has no attribute "loader" |
| `.agents/tests/test_route_cli.py` | `test_route_cli` | `no-untyped-def` | 2 | Function is missing a return type annotation |
| `.agents/tests/test_sync_generated_safety.py` | `test_sync_generated_safety` | `arg-type` | 1 | Argument 1 to "module_from_spec" has incompatible type "ModuleSpec \| None"; expected "ModuleSpec" |
| `.agents/tests/test_sync_generated_safety.py` | `test_sync_generated_safety` | `no-untyped-call` | 1 | Call to untyped function (unknown) in typed context |
| `.agents/tests/test_sync_generated_safety.py` | `test_sync_generated_safety` | `type-arg` | 1 | Missing type arguments for generic type "dict" |
| `.agents/tests/test_sync_generated_safety.py` | `test_sync_generated_safety` | `union-attr` | 2 | Item "None" of "ModuleSpec \| None" has no attribute "loader" |
| `.agents/tests/test_validate_claude.py` | `test_validate_claude` | `arg-type` | 1 | Argument 1 to "module_from_spec" has incompatible type "ModuleSpec \| None"; expected "ModuleSpec" |
| `.agents/tests/test_validate_claude.py` | `test_validate_claude` | `index` | 5 | Value of type "object" is not indexable |
| `.agents/tests/test_validate_claude.py` | `test_validate_claude` | `no-untyped-def` | 9 | Function is missing a return type annotation |
| `.agents/tests/test_validate_claude.py` | `test_validate_claude` | `union-attr` | 2 | Item "None" of "ModuleSpec \| None" has no attribute "loader" |
| `.agents/tests/test_validate_claude.py` | `test_validate_claude` | `var-annotated` | 2 | Need type annotation for "invalid" |
| `.agents/tests/test_versionless_packages.py` | `test_versionless_packages` | `arg-type` | 1 | Argument 1 to "module_from_spec" has incompatible type "ModuleSpec \| None"; expected "ModuleSpec" |
| `.agents/tests/test_versionless_packages.py` | `test_versionless_packages` | `no-untyped-def` | 3 | Function is missing a return type annotation |
| `.agents/tests/test_versionless_packages.py` | `test_versionless_packages` | `union-attr` | 2 | Item "None" of "ModuleSpec \| None" has no attribute "loader" |
| `.agents/tests/test_win32_scaffold.py` | `test_win32_scaffold` | `no-any-return` | 1 | Returning Any from function declared to return "int" |
| `.github/scripts/update_provenance_pins.py` | `update_provenance_pins` | `index` | 1 | Value of type "Match[str] \| None" is not indexable |
| `.github/scripts/update_provenance_pins.py` | `update_provenance_pins` | `no-untyped-call` | 34 | Call to untyped function "require_sha" in typed context |
| `.github/scripts/update_provenance_pins.py` | `update_provenance_pins` | `no-untyped-def` | 15 | Function is missing a type annotation |
| `.github/scripts/validate_claude.py` | `validate_claude` | `no-untyped-call` | 5 | Call to untyped function "collect" in typed context |
| `.github/scripts/validate_claude.py` | `validate_claude` | `no-untyped-def` | 3 | Function is missing a type annotation |
| `.github/scripts/validate_claude.py` | `validate_claude` | `var-annotated` | 3 | Need type annotation for "errors" (hint: "errors: list[<type>] = ...") |

## Custom checker

Reason: preserve exact pre-existing custom-checker findings during the standards rollout. Each entry maps to one authored path and rule; repair the stated design issue and remove its exception. No generated or vendored path is included.

| File | Rule | Existing count | Required repair |
| --- | --- | ---: | --- |
| .agents/tests/test_attester_safety.py | PY016 | 5 | Inject process state or confine the read to an entry-point main. |
| .agents/tests/test_canonical_names.py | PY001 | 2 | Rewrite the nested comprehension as named loops or one generator. |
| .agents/tests/test_hook_contract.py | PY016 | 1 | Inject process state or confine the read to an entry-point main. |
| .agents/tests/test_marketplace_contract.py | PY001 | 1 | Rewrite the nested comprehension as named loops or one generator. |
| .agents/tests/test_marketplace_contract.py | PY016 | 2 | Inject process state or confine the read to an entry-point main. |
| .agents/tests/test_msvc_scaffold.py | PY016 | 2 | Inject process state or confine the read to an entry-point main. |
