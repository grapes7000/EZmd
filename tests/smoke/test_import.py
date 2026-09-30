"""Cheap smoke coverage for the real application package."""


def test_ezmd_package_imports() -> None:
    import ezmd

    assert ezmd.__name__ == "ezmd"
