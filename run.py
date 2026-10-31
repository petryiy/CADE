"""Command-line interface for the implementation in CADE.ipynb."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent


def load_core():
    namespace = {"__name__": "cade_notebook"}
    notebook = json.loads((ROOT / "CADE.ipynb").read_text())
    for index, cell in enumerate(notebook["cells"]):
        if "cade-core" in cell.get("metadata", {}).get("tags", []):
            exec(compile("".join(cell["source"]), f"CADE.ipynb:cell{index}", "exec"), namespace)
    return namespace


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", choices=[
        "demo", "check", "normal", "spatial", "permutations",
        "external-normal", "external-spatial", "external-native",
        "followup-normal", "followup-spatial", "followup-native",
        "followup-randomization", "followup-components", "followup-prepare",
    ])
    parser.add_argument("--replicates", type=int)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--shard", type=int, default=0)
    parser.add_argument("--shards", type=int, default=1)
    parser.add_argument("--input-gef", type=Path)
    args = parser.parse_args()
    if args.shards < 1 or not 0 <= args.shard < args.shards:
        parser.error("Require 0 <= shard < shards")
    if args.replicates is not None and args.replicates < 1:
        parser.error("--replicates must be positive")
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be positive")
    if args.task == "check":
        import unittest
        suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        return 0 if result.wasSuccessful() else 1
    ns = load_core()
    with ns["threadpool_limits"](limits=1):
        if args.task == "demo":
            chips, outcomes = ns["load_pilot"](ROOT)
            d = ns["make_design"](chips["C02943C3"], chips["A03599E2"])
            fit = ns["fit_cade"](d["Z"][:, :5], d["Z"][:, 5:], outcomes["C02943C3"], d["blocks"],
                                 predict_N=d["T"][:, :5], predict_S=d["T"][:, 5:])
            effect = fit["observed_prediction"] - fit["observed_zero_prediction"]
            print(json.dumps({"training_chip": "C02943C3", "prediction_chip": "A03599E2",
                              "prediction_shape": list(fit["observed_prediction"].shape),
                              "mean_absolute_source_contrast": float(abs(effect).mean())}, indent=2))
        elif args.task == "normal":
            ns["run_normal"](ROOT, args.replicates or 100)
        elif args.task == "spatial":
            ns["run_spatial"](ROOT, args.replicates or 12, args.limit)
        elif args.task == "permutations":
            ns["run_permutations"](ROOT, args.limit or 99)
        elif args.task == "followup-prepare":
            if args.input_gef is None:
                parser.error("--input-gef is required")
            (ROOT / "results/followup").mkdir(parents=True, exist_ok=True)
            ns["fu_prepare_gef"](ROOT, args.input_gef)
        else:
            family, task = args.task.split("-", 1)
            (ROOT / "results" / family).mkdir(parents=True, exist_ok=True)
            prefix = "ex_run_" if family == "external" else "fu_run_"
            if task in ("normal", "spatial") or args.task == "external-native":
                ns[prefix + task](ROOT, args.shard, args.shards)
            elif args.task == "followup-randomization":
                needed = ROOT / "results/followup/native_parameters_pilot_CADE_pooled.json"
                if not needed.exists():
                    parser.error("Run followup-native before followup-randomization")
                ns["fu_run_native_permutations"](ROOT)
            else:
                ns[prefix + task](ROOT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
