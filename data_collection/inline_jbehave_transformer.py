from __future__ import annotations
from pathlib import Path

import argparse 
import os
import re
import shutil


INLINE_JBEHAVE_FILE_ROOT =  Path("/home/WERUM/felix_soltau/projects/private/git/test-artifact-retrieval/data_collection/raw_data/inline_jbehave_java_files")
OUTPUT_ROOT = Path("/home/WERUM/felix_soltau/projects/private/git/test-artifact-retrieval/data_collection/raw_data/specs_from_inline_jbehave_java_files")

PACKAGE_RE = re.compile(r"^\s*package\s+[^;]+;\s*$", re.MULTILINE)
SCENARIO_RE = re.compile(r'@Scenario\s*\(\s*"([^"]+)"\s*\)')
STEP_RE = re.compile(r'\b(?:Given|When|Then|And)\s*\(\s*"([^"]+)"', re.DOTALL)
NARRATIVE_RE = re.compile(
    r'@Narrative\s*\(\s*asA\s*=\s*"([^"]+)"\s*,\s*iWantTo\s*=\s*"([^"]+)"\s*,\s*inOrderTo\s*=\s*"([^"]+)"\s*\)',
    re.DOTALL            
)

def extract_text_to_new_file(source: Path, output_root: Path) -> Path | None:
    content = source.read_text(encoding="utf-8", errors="ignore")

    package_match = PACKAGE_RE.search(content)
    narrative_match = NARRATIVE_RE.search(content)
    scenario_matches = SCENARIO_RE.findall(content)
    step_matches = STEP_RE.findall(content)

    #if not (narrative_match and scenario_matches and step_matches):
    #    return None
    
    lines: list[str] = []

    if package_match:
        lines.append(package_match.group(0).strip())
        lines.append("")

    if narrative_match:
        as_a, i_want_to, in_order_to = narrative_match.groups()
        lines.append("@Narrative")    
        lines.append(f"As a {as_a}")
        lines.append(f"I want to {i_want_to}")
        lines.append(f"In order to {in_order_to}")
        lines.append("")

    for scenario in scenario_matches:
        lines.append("@Scenario")
        lines.append(scenario)
        lines.append("")  

    for step_text in step_matches:
        lines.append(step_text)
        lines.append("")

    output_root.mkdir(parents=True, exist_ok=True)
    output_name = f"{source.stem}_spec.txt"    
    destination = output_root / output_name
    destination.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return destination


def collect_only_spec() -> list[Path]:
    copied: list[Path] = []

    for source in INLINE_JBEHAVE_FILE_ROOT.rglob("*.java"):
        try:
            destination = extract_text_to_new_file(source, OUTPUT_ROOT)
        except OSError:
            continue

        if destination:
            copied.append(destination)

    return copied  

def main() -> None:
    copied = collect_only_spec()
    print(f"Created {len(copied)} spec text files in {OUTPUT_ROOT}.")

if __name__ == "__main__":
    main()    


