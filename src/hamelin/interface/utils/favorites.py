"""Favorite-model marking, stored as a plain JSON file inside the results
folder rather than app-local state, so any other tool pointed at the same
results directory (e.g. Hamelin) can read the same favorites."""

import json
from pathlib import Path

import hamelin.interface.utils.get_model_paths as gmp

# results_dir defaults to None (not utils.get_model_paths.RESULTS_DIR
# directly) so it's resolved fresh on every call via gmp.RESULTS_DIR below,
# instead of being frozen to whatever that value was when this module was
# first imported. A plain default argument would silently keep using the
# stale directory even after gmp.RESULTS_DIR changes at runtime (e.g. in
# tests, or if the app ever supports switching project folders) - exactly
# the kind of thing that matters here since a wrong directory means
# checking favorite status against the wrong file.


def _favorites_file(results_dir=None):
    return Path(results_dir if results_dir is not None else gmp.RESULTS_DIR) / "favorites.json"


def load_favorites(results_dir=None):
    path = _favorites_file(results_dir)
    if not path.exists():
        return set()
    try:
        with open(path, "r") as f:
            return set(json.load(f))
    except Exception:
        return set()


def save_favorites(favorites, results_dir=None):
    path = _favorites_file(results_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(sorted(favorites), f, indent=2)


def is_favorite(model_name, results_dir=None):
    return model_name in load_favorites(results_dir)


def toggle_favorite(model_name, results_dir=None):
    favorites = load_favorites(results_dir)
    if model_name in favorites:
        favorites.discard(model_name)
    else:
        favorites.add(model_name)
    save_favorites(favorites, results_dir)
    return model_name in favorites
