#!/usr/bin/env python3
"""Run the verbose requirement audit and print a compact pass/failure summary."""

import contextlib
import io
import traceback

from check_dop_revision_260902I import main


buffer = io.StringIO()
try:
    with contextlib.redirect_stdout(buffer):
        result = main()
except Exception:
    lines = buffer.getvalue().splitlines()
    print("\n".join(lines[-12:]))
    traceback.print_exc()
    raise SystemExit(1)

lines = buffer.getvalue().splitlines()
print(f"requirement assertions passed={sum(line.startswith('PASS  ') for line in lines)}")
print(lines[-1] if lines else "revision checker produced no output")
raise SystemExit(result)
