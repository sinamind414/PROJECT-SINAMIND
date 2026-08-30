"""T3 — le client n'envoie pas un int libre (G10)."""

from services.economy import REWARD_ACTIONS, UnknownRewardAction, delta_for_action


def test_known_actions_are_small_positive():
    for name, delta in REWARD_ACTIONS.items():
        assert delta_for_action(name) == delta
        assert 0 < delta <= 50


def test_unknown_and_empty_rejected():
    for bad in ("", "hack", "points=99999", "admin"):
        try:
            delta_for_action(bad)
            raise AssertionError(f"{bad!r} aurait dû échouer")
        except UnknownRewardAction:
            pass


def test_g10_client_delta_not_in_whitelist():
    assert 99999 not in REWARD_ACTIONS.values()
    assert delta_for_action("start") != 99999
