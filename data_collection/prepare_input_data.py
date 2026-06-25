from logging import root
from pathlib import Path
import shutil

DEFAULT_ROOT = Path("/home/WERUM/felix_soltau/projects/private/git/test-artifact-retrieval/data_collection/raw_data")
DEFAULT_TARGET_ROOT = Path("/home/WERUM/felix_soltau/projects/private/git/test-artifact-retrieval/data_collection/input_data")

def copy_file(root: Path, target_root: Path) -> list[Path]:
    copied: list[Path] = []

    for source in root.rglob("*"):
        if source.is_file():
            destination = target_root / source.name        
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            copied.append(destination)

    return copied


def copy_feature_files():
    root = DEFAULT_ROOT / "feature_files"
    target_root = DEFAULT_TARGET_ROOT / "feature_files"
    return copy_file(root, target_root)

def copy_story_files():
    root = DEFAULT_ROOT / "story_files"
    target_root = DEFAULT_TARGET_ROOT / "story_files"
    return copy_file(root, target_root)

def copy_inline_jbehave_text_files():
    root = DEFAULT_ROOT / "specs_from_inline_jbehave_java_files"
    target_root = DEFAULT_TARGET_ROOT / "inline_jbehave_text_files"
    return copy_file(root, target_root)


feature_files = copy_feature_files()
story_files = copy_story_files()
inline_jbehave_text_files = copy_inline_jbehave_text_files()

print(f"Copied {len(feature_files)} feature files to {DEFAULT_TARGET_ROOT / 'feature_files'}")
print(f"Copied {len(story_files)} story files to {DEFAULT_TARGET_ROOT / 'story_files'}")
print(f"Copied {len(inline_jbehave_text_files)} inline jbehave text files to {DEFAULT_TARGET_ROOT / 'inline_jbehave_text_files'}")

