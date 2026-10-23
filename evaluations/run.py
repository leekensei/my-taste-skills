"""Agent-neutral decision evals. A runner consumes a prompt on stdin, emits JSON.

This does not execute application code or verify automatic skill discovery.
Only --runner invokes a model; --check and --responses work entirely offline.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / "evaluations/react-composition.cases.json"
SKILL = ROOT / "skills/react-composition/SKILL.md"
FIELDS = {
    "applicable", "ui_api", "feature_context", "source_boundary",
    "shared_action_boundary", "keep_density_prop", "fixture_without_network",
    "local_interaction_state", "preserve_async_errors", "loading",
    "compatibility", "context_api",
}
OUTPUT_CONTRACT = """Return exactly one JSON object, without Markdown fences.
Include a nonempty `reason` explaining the smallest useful change and risks.
Use applicable keys from this decision vocabulary:
applicable, feature_context, source_boundary, shared_action_boundary,
keep_density_prop, fixture_without_network, preserve_async_errors: booleans.
ui_api: props | parts | unchanged.
local_interaction_state: local | provider | unchanged.
loading: unchanged | conditional-mount | query-enabled | suspense-only.
compatibility: keep-react-version | upgrade-react.
context_api: useContext-and-Provider | use-and-context-shorthand | unchanged.
Omit fields irrelevant to the request. Supply decisions, not application code.
feature_context means introducing a NEW feature-level context in this task,
excluding private context internal to a UI primitive. The source_boundary and
shared_action_boundary fields also describe introducing a new boundary.
ui_api=props means choosing/retaining plain props; unchanged means UI API design
is outside the current change. applicable means composition decisions are in scope.
"""


def load_cases(path):
    suite = json.loads(Path(path).read_text())
    if suite.get("schema_version") != 1 or not suite.get("cases"):
        raise ValueError("Expected schema_version 1 with nonempty cases")
    seen = set()
    for case in suite["cases"]:
        case_id = case["id"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", case_id) or case_id in seen:
            raise ValueError(f"Invalid or duplicate case id: {case_id}")
        seen.add(case_id)
        if not isinstance(case["prompt"], str) or not case["prompt"].strip():
            raise ValueError(f"Missing prompt: {case_id}")
        expected = case["expected"]
        if not isinstance(expected, dict) or not expected or expected.keys() - FIELDS:
            raise ValueError(f"Invalid criteria: {case_id}")
        for target in expected.values():
            options = target if isinstance(target, list) else [target]
            if not options or any(type(option) not in (str, bool) for option in options):
                raise ValueError(f"Invalid expected value: {case_id}")
    return suite["cases"]


def build_prompt(case, skill=None):
    # Neither the golden decisions nor evaluation results enter the model input.
    guidance = f"Apply this skill when relevant:\n<skill>\n{skill}\n</skill>\n\n" if skill else ""
    return guidance + case["prompt"] + "\n\n" + OUTPUT_CONTRACT


def grade(response, expected):
    if not isinstance(response, dict) or not isinstance(response.get("reason"), str) or not response["reason"].strip():
        raise ValueError("Response must be an object with a nonempty reason")
    checks = {}
    for key, target in expected.items():
        options = target if isinstance(target, list) else [target]
        actual = response.get(key)
        checks[key] = any(type(actual) is type(option) and actual == option for option in options)
    return {"checks": checks, "score": sum(checks.values()) / len(checks)}


def evaluate(cases, skill, output, *, runner=None, responses=None, runs=1, timeout=120, arms=("with", "without")):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    results = []
    for arm in arms:
        for case in cases:
            for run in range(1, runs + 1):
                folder = output / arm / case["id"]
                folder.mkdir(parents=True, exist_ok=True)
                prompt = build_prompt(case, skill if arm == "with" else None)
                (folder / f"run-{run}.prompt.txt").write_text(prompt)
                item = {"arm": arm, "case": case["id"], "run": run}
                try:
                    if runner:
                        # A baseline must not see files produced by the with arm.
                        with tempfile.TemporaryDirectory(prefix="composition-eval-run-") as work:
                            completed = subprocess.run(
                                runner, input=prompt, text=True, capture_output=True,
                                timeout=timeout, check=True, cwd=work,
                            )
                        raw = completed.stdout
                    else:
                        raw = (Path(responses) / arm / case["id"] / f"run-{run}.json").read_text()
                    (folder / f"run-{run}.raw.txt").write_text(raw)
                    response = json.loads(raw)
                    item.update(grade(response, case["expected"]))
                    item["response"] = response
                    item["status"] = "graded"
                except (ValueError, OSError, subprocess.SubprocessError) as error:
                    item.update(status="error", error=str(error), score=None)
                results.append(item)
                print(f"{arm}/{case['id']}/{run}: {item['score'] if item['status'] == 'graded' else 'ERROR'}", flush=True)
                if item["status"] == "error":
                    # Do not keep making model calls after a broken runner or quota error.
                    return write_report(output, cases, skill, results, arms, runs)
    return write_report(output, cases, skill, results, arms, runs)


def write_report(output, cases, skill, results, arms, runs):
    summary = {}
    for case in cases:
        entry = {}
        for arm in arms:
            matched = [r for r in results if r["case"] == case["id"] and r["arm"] == arm]
            complete = len(matched) == runs and all(r["status"] == "graded" for r in matched)
            entry[arm] = sum(r["score"] for r in matched) / runs if complete else None
        if set(arms) == {"with", "without"}:
            entry["delta"] = entry["with"] - entry["without"] if all(entry[a] is not None for a in arms) else None
        summary[case["id"]] = entry
    report = {
        "schema_version": 1, "skill_sha256": hashlib.sha256(skill.encode()).hexdigest(),
        "case_sha256": hashlib.sha256(json.dumps(cases, sort_keys=True).encode()).hexdigest(),
        "runs_per_arm": runs, "summary": summary, "results": results,
        "complete": len(results) == len(cases) * len(arms) * runs and all(r["status"] == "graded" for r in results),
        "scope": "Structured composition decisions; not code correctness, auto-discovery, or rationale quality.",
    }
    (output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--runner", help="Command reading a prompt on stdin and emitting a plain JSON decision; executed without a shell")
    source.add_argument("--responses", type=Path, help="Existing <arm>/<case>/run-N.json responses to regrade")
    parser.add_argument("--check", action="store_true", help="Validate the suite without model calls")
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--arm", choices=("both", "with", "without"), default="both")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.runs < 1 or args.timeout < 1:
        parser.error("runs and timeout must be positive")
    try:
        cases = load_cases(SUITE)
        skill = SKILL.read_text()
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.error(str(error))
    if args.check:
        print(f"Valid suite: {len(cases)} cases. No model calls made.")
        return 0
    if not args.runner and not args.responses:
        parser.error("choose --check, --runner, or --responses")
    runner = shlex.split(args.runner) if args.runner else None
    if args.runner and not runner:
        parser.error("runner command must not be empty")
    output = args.output or ROOT / "evaluations/results" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    arms = ("with", "without") if args.arm == "both" else (args.arm,)
    report = evaluate(cases, skill, output, runner=runner, responses=args.responses, runs=args.runs, timeout=args.timeout, arms=arms)
    print(f"Report: {output / 'report.json'}")
    if not report["complete"]:
        return 2
    # One-arm baselines are also allowed; they are not quality gates for the skill.
    return 1 if "with" in arms and any(s["with"] < 1 for s in report["summary"].values()) else 0


if __name__ == "__main__":
    sys.exit(main())
