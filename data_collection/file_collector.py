from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path

DEFAULT_GIT_ROOT = Path("/home/WERUM/felix_soltau/projects/pasx-3.4.X/git/file.collection")
DEFAULT_OUTPUT_ROOT = Path("/home/WERUM/felix_soltau/projects/private/git/test-artifact-retrieval/data_collection/raw_data")


def copy_matching_files(repo_root: Path, target_root: Path, suffix: str) -> list[Path]:
    copied: list[Path] = []

    for dirpath, dirnames, filenames in os.walk(repo_root):
        current_dir = Path(dirpath)

        # skip output folders if they live inside the repo
        dirnames[:] =[
            d for d in dirnames 
            if(current_dir / d) != target_root
            and target_root not in (current_dir / d).parents
        ] 

        for filename in filenames:
            if not filename.endswith(suffix):
                continue

            source = current_dir / filename
            rel_path = source.relative_to(repo_root)
            destination = target_root / rel_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            copied.append(source)

    return copied    

def iter_repo_roots(git_root: Path) -> list[Path]:
    return [  
        p for p in git_root.iterdir()
        if p.is_dir() and (p / ".git").exists()
    ] 


def collect_feature_files(repo_root: str, repo_name: str, output_root: str) -> list[Path]:
    target = output_root / "feature_files" / f"feature_files_from_{repo_name}"
    target.mkdir(parents=True, exist_ok=True)
    return copy_matching_files(repo_root, target, ".feature")

def collect_story_files(repo_root: str, repo_name: str, output_root: str) -> list[Path]:
    target = output_root / "story_files" / f"story_files_from_{repo_name}"
    target.mkdir(parents=True, exist_ok=True)
    return copy_matching_files(repo_root, target, ".story")

def collect_inline_jbehave_java_files(repo_root: str, repo_name: str, output_root: str) -> list[Path]:
    target = output_root / "inline_jbehave_java_files" / f"inline_jbehave_java_files_from_{repo_name}"
    target.mkdir(parents=True, exist_ok=True)

    copied: list[Path] = []
    markers = ("@Scenario(",)

    for source in repo_root.rglob("*.java"):
        if output_root in source.parents:
            continue
        try:
            content = source.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        if not any(marker in content for marker in markers):
            continue

        rel_path = source.relative_to(repo_root)
        destination = target / rel_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        copied.append(source)

    return copied   

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect feature and story files from central repo.")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=DEFAULT_GIT_ROOT,
        help="Path to the central repo to scan.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Path to the raw_data output directory.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    git_root = args.repo_root.resolve()
    output_root = args.output_root.resolve()

    all_feature_files: list[Path] = []
    all_story_files: list[Path] = []
    all_inline_jbehave_java_files: list[Path] = []

    for repo_root in iter_repo_roots(git_root):
        repo_name = repo_root.name
        feature_files = collect_feature_files(repo_root, repo_name, output_root)
        story_files = collect_story_files(repo_root, repo_name, output_root)
        inline_jbehave_java_files = collect_inline_jbehave_java_files(repo_root, repo_name, output_root)

        all_feature_files.extend(feature_files)
        all_story_files.extend(story_files)
        all_inline_jbehave_java_files.extend(inline_jbehave_java_files)

        print(
            f"{repo_name}: "
            f"{len(feature_files)} feature files, "
            f"{len(story_files)} story files, "
            f"{len(inline_jbehave_java_files)} inline JBehave Java files"
        )

    print("Summary:")  
    print(f"Total feature files: {len(all_feature_files)}")  
    print(f"Total story files: {len(all_story_files)}")  
    print(f"Total inline JBehave Java files: {len(all_inline_jbehave_java_files)}")  
    print(f"Total copied files: {len(all_feature_files) + len(all_story_files) + len(all_inline_jbehave_java_files)}")
    

if __name__ == "__main__":
    main()