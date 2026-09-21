"""Run the minimal agent against Kaggriculture's built-in baselines."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from kaggle_environments import make


ROOT = Path(__file__).resolve().parent
OPPONENTS = ("random", "starter")


def run_match(opponent: str, episode_steps: int, seed: int, output_dir: Path) -> dict:
    env = make(
        "kaggriculture",
        configuration={"episodeSteps": episode_steps, "seed": seed},
        debug=True,
    )
    env.run([str(ROOT / "main.py"), opponent])

    replay_path = output_dir / f"main-vs-{opponent}.json"
    replay_path.write_text(json.dumps(env.toJSON()), encoding="utf-8")

    final = env.steps[-1]
    result = {
        "opponent": opponent,
        "episode_steps": episode_steps,
        "seed": seed,
        "statuses": [state.status for state in final],
        "rewards": [state.reward for state in final],
        "replay": str(replay_path.relative_to(ROOT)),
    }

    if result["statuses"] != ["DONE", "DONE"]:
        raise RuntimeError(f"{opponent} match did not finish cleanly: {result}")
    if replay_path.stat().st_size == 0:
        raise RuntimeError(f"{opponent} replay is empty")

    loaded_replay = json.loads(replay_path.read_text(encoding="utf-8"))
    if len(loaded_replay.get("steps", [])) != episode_steps:
        raise RuntimeError(
            f"{opponent} replay has {len(loaded_replay.get('steps', []))} steps; "
            f"expected {episode_steps}"
        )

    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episode-steps", type=int, default=720)
    parser.add_argument("--seed", type=int, default=20260921)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "replays")
    args = parser.parse_args()

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    results = [
        run_match(opponent, args.episode_steps, args.seed, output_dir)
        for opponent in OPPONENTS
    ]
    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    for result in results:
        print(
            f"main.py vs {result['opponent']}: "
            f"statuses={result['statuses']} rewards={result['rewards']} "
            f"replay={result['replay']}"
        )
    print(f"summary={summary_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
