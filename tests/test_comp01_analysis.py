import unittest

from experiments.analyze_comp01 import preregistered_decision


def evidence(
    budget,
    concordant=True,
    ci=True,
    delta_r=1.0,
    family_effect=0.2,
):
    predicted = -1 if delta_r > 0 else 1
    delta_g = predicted * (0.1 if concordant else -0.1)
    return {
        "budget": budget,
        "delta_R": delta_r,
        "predicted_delta_G_sign": predicted,
        "delta_G_bits_per_token": delta_g,
        "prediction_concordant": concordant,
        "ci_excludes_zero_in_predicted_direction": ci,
        "relation_family_delta_G": {
            "horizontal": predicted * family_effect,
            "vertical": predicted * family_effect,
            "depth": predicted * family_effect,
        },
    }


class Comp01AnalysisTests(unittest.TestCase):
    def test_all_joint_support_criteria_produce_promising(self):
        rows = [
            evidence(budget)
            for budget in ("low", "current", "high")
            for _ in range(3)
        ]
        result = preregistered_decision(rows)
        self.assertEqual(result["status"], "PROMISING")
        self.assertTrue(all(result["support_checks"].values()))

    def test_five_or_fewer_concordant_rejects(self):
        rows = [
            evidence(budget, concordant=index < 5, ci=index < 5)
            for index, budget in enumerate(
                ("low",) * 3 + ("current",) * 3 + ("high",) * 3
            )
        ]
        result = preregistered_decision(rows)
        self.assertEqual(result["status"], "REJECT_IDEA")
        self.assertTrue(
            result["rejection_checks"]["sign_concordance_at_most_5_of_9"]
        )


if __name__ == "__main__":
    unittest.main()
