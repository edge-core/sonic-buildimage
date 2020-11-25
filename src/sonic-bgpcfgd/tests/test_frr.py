from bgpcfgd.frr import FRR


def test_constructor():
    f = FRR(["abc", "cde"])
    assert f.daemons == ["abc", "cde"]
