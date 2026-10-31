"""Numerical regression and input-to-prediction checks for the public source."""
import csv
from pathlib import Path
import sys
import unittest
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from run import load_core


class TestCADE(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ns = load_core()
        cls.chips, cls.y = cls.ns["load_pilot"](ROOT)

    def test_frozen_score_likelihood(self):
        with (ROOT / "tests/normal_reference.csv").open() as f:
            reference = list(csv.DictReader(f))
        with self.ns["threadpool_limits"](limits=1):
            for rho, pattern, alpha, rep in [(0., "single", .2, 0), (.7, "paired_same", .6, 1), (.95, "paired_opposite", 1., 2)]:
                rows = self.ns["cx_normal_case"](rho, pattern, alpha, rep, 20261030)
                for row in rows:
                    old = next(x for x in reference if float(x["rho"]) == rho and x["pattern"] == pattern
                               and float(x["alpha"]) == alpha and int(x["replicate"]) == rep and x["model"] == row["model"])
                    for key in ("coefficient_MSE", "exposure_effect_MSE", "near_far_contrast_MSE"):
                        np.testing.assert_allclose(row[key], float(old[key]), rtol=2e-8, atol=1e-11)

    def test_cross_chip_prediction_replays_parameters(self):
        d = self.ns["make_design"](self.chips["C02943C3"], self.chips["A03599E2"])
        fit = self.ns["fit_cade"](d["Z"][:, :5], d["Z"][:, 5:], self.y["C02943C3"], d["blocks"],
                                  predict_N=d["T"][:, :5], predict_S=d["T"][:, 5:])
        rows = fit["audit"]["responses"]
        q = np.array([r["q_nuisance_beta"] + r["q_sources"] for r in rows])
        m = np.array([r["m_nuisance_beta"] + r["m_sources"] for r in rows])
        pred = self.ns["expit"](d["T"] @ q.T) * np.maximum(d["T"] @ m.T, 0)
        zero_design = d["T"].copy(); zero_design[:, 5:] = 0
        zero = self.ns["expit"](zero_design @ q.T) * np.maximum(zero_design @ m.T, 0)
        np.testing.assert_allclose(pred, fit["observed_prediction"], rtol=1e-10, atol=1e-12)
        np.testing.assert_allclose(zero, fit["observed_zero_prediction"], rtol=1e-10, atol=1e-12)
        self.assertEqual(pred.shape, (6898, 4))
        self.assertTrue(np.isfinite(pred).all())
        self.assertTrue((pred >= 0).all())

    def test_reject_unbounded_sources(self):
        d = self.ns["make_design"](self.chips["C02943C3"])
        source = d["Z"][:, 5:].copy(); source[0, 0] = 2
        with self.assertRaisesRegex(ValueError, "bounded"):
            self.ns["fit_cade"](d["Z"][:, :5], source, self.y["C02943C3"], d["blocks"])

    def test_followup_native_geometry(self):
        with np.load(ROOT / "data/followup/B03018A2.npz", allow_pickle=False) as z:
            data = {key: z[key] for key in z.files}
        np.testing.assert_array_equal(self.ns["fu_native_counts"](data), data["counts"])
        self.assertEqual(len(data["N"]), 49243)


if __name__ == "__main__":
    unittest.main()
