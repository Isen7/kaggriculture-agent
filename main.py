"""Minimal Kaggriculture submission used to verify the local toolchain."""


def agent(obs):
    """Return a valid no-op action without applying any game strategy."""
    return {
        "farmer": ["PASS"],
        "hands": [],
        "market": [],
    }
