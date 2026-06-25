from pathlib import Path
import re

INLINE_JBEHAVE_FILE_ROOT = Path("/home/WERUM/felix_soltau/projects/private/git/test-artifact-retrieval/data_collection/raw_data/inline_jbehave_java_files")
OUTPUT_ROOT = Path("/home/WERUM/felix_soltau/projects/private/git/test-artifact-retrieval/data_collection/raw_data/specs_from_inline_jbehave_java_files")

META_KEYS = ("filename", "repo_name", "rel_path", "source_type")
STEP_KEYS = ("Given", "When", "Then", "And", "But")
ANNOTATION_KEYS = ("@Narrative", "@Scenario")

META_PATTERN = re.compile(r"^(filename|repo_name|rel_path|source_type):\s*(.*)$")
FIRST_STRING_PATTERN = re.compile(r'"((?:\\.|[^"\\])*)"')
STEP_PATTERN = re.compile(r"\b(Given|When|Then|And|But)\s*\(")
NARRATIVE_ITEM_PATTERN = re.compile(
    r'\b(inOrderTo|asA|iWantTo)\s*=\s*"((?:\\.|[^"\\])*)"',
    re.DOTALL,
)

NARRATIVE_LABELS = {
    "inOrderTo": "In order to",
    "asA": "As a",
    "iWantTo": "I want to",
}


def extract_first_string(text: str):
    m = FIRST_STRING_PATTERN.search(text)
    if m:
        return m.group(1)
    return None


def count_parens(text: str):
    return text.count("(") - text.count(")")


def count_structural_parens(text: str):
    balance = 0
    in_string = False
    in_text_block = False
    escaped = False
    i = 0

    while i < len(text):
        ch = text[i]

        if in_text_block:
            if text.startswith('"""', i):
                in_text_block = False
                i += 3
                continue
            i += 1
            continue

        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            i += 1
            continue

        if text.startswith('"""', i):
            in_text_block = True
            i += 3
            continue
        if ch == '"':
            in_string = True
        elif ch == "(":
            balance += 1
        elif ch == ")":
            balance -= 1

        i += 1

    return balance


def get_step_type(line: str):
    m = STEP_PATTERN.search(line)
    if m:
        return m.group(1)
    return None


def is_relevant_line(line: str):
    stripped = line.strip()
    if any(k in stripped for k in ANNOTATION_KEYS):
        return True
    if re.search(r"\b(Given|When|Then|And|But)\s*\(", stripped):
        return True
    return False


def extract_block_string(block_lines):
    text = "\n".join(block_lines)
    return extract_first_string(text)


def extract_string_fragments(text: str):
    fragments = []
    i = 0

    while i < len(text):
        if text.startswith('"""', i):
            i += 3
            end = text.find('"""', i)
            if end == -1:
                fragments.append(text[i:])
                break
            fragments.append(text[i:end])
            i = end + 3
            continue

        if text[i] == '"':
            i += 1
            buffer = []
            escaped = False

            while i < len(text):
                ch = text[i]
                if escaped:
                    buffer.append(ch)
                    escaped = False
                elif ch == "\\":
                    buffer.append(ch)
                    escaped = True
                elif ch == '"':
                    fragments.append("".join(buffer))
                    i += 1
                    break
                else:
                    buffer.append(ch)
                i += 1
            else:
                fragments.append("".join(buffer))
                break
            continue

        i += 1

    return fragments


def extract_quoted_fragments(block_lines):
    text = "\n".join(block_lines)
    return [fragment.replace(r"\n", "\n") for fragment in extract_string_fragments(text)]


def extract_step_argument_text(block_lines):
    text = "\n".join(block_lines)
    start = text.find("(")
    if start == -1:
        return ""

    in_string = False
    in_text_block = False
    escaped = False
    nested_parens = 0

    index = start + 1
    while index < len(text):
        ch = text[index]

        if in_text_block:
            if text.startswith('"""', index):
                in_text_block = False
                index += 3
                continue
            index += 1
            continue

        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            index += 1
            continue

        if text.startswith('"""', index):
            in_text_block = True
            index += 3
            continue
        if ch == '"':
            in_string = True
        elif ch == "(":
            nested_parens += 1
        elif ch == ")":
            if nested_parens == 0:
                return text[start + 1:index]
            nested_parens -= 1
        elif ch == "," and nested_parens == 0:
            return text[start + 1:index]

        index += 1

    return text[start + 1:]


def extract_scenario_block(block_lines):
    fragments = extract_quoted_fragments(block_lines)

    if not fragments:
        return None

    normalized = [fragment.rstrip("\n") for fragment in fragments]
    return "\n".join(normalized).rstrip("\n")


def block_text(block_lines):
    return "\n".join(block_lines)


def extract_step_lines(block_lines, step_type: str | None):
    argument_text = extract_step_argument_text(block_lines)
    fragments = [fragment.replace(r"\n", "\n") for fragment in FIRST_STRING_PATTERN.findall(argument_text)]

    if not fragments:
        return []

    prefix = step_type or "Step"
    lines = [f"{prefix} {fragments[0]}"]

    for fragment in fragments[1:]:
        lines.append(fragment.lstrip())

    return lines


def extract_narrative_block(block_lines):
    text = "\n".join(block_lines)
    items = []

    for match in NARRATIVE_ITEM_PATTERN.finditer(text):
        key, value = match.groups()
        label = NARRATIVE_LABELS.get(key)
        if label:
            items.append(f"{label} {value}")

    if not items:
        return None

    return "\n".join(["Narrative:", *items])


def process_file(file_path: Path):
    metadata = {}
    narratives = []
    scenarios = []

    collecting = False
    buffer = []
    paren_balance = 0
    current_kind = None
    current_step_type = None

    current_scenario = None
    current_steps = []

    with file_path.open("r", encoding="utf-8", errors="replace") as f:
        for raw_line in f:
            line = raw_line.rstrip("\n")

            # metadata block at start
            if len(metadata) < 4:
                if line.strip() == "metadata:":
                    continue
                mm = META_PATTERN.match(line)
                if mm:
                    key, value = mm.group(1), mm.group(2)
                    metadata[key] = value
                    continue

            stripped = line.strip()

            if not collecting and is_relevant_line(line):
                collecting = True
                buffer = [line]
                paren_balance = count_structural_parens(block_text(buffer))

                if "@Narrative" in stripped:
                    current_kind = "narrative"
                    current_step_type = None
                elif "@Scenario" in stripped:
                    current_kind = "scenario"
                    current_step_type = None
                else:
                    current_kind = "step"
                    current_step_type = get_step_type(stripped)

                if paren_balance <= 0 and ")" in line:
                    block_string = extract_block_string(buffer)

                    if current_kind == "narrative":
                        narrative_block = extract_narrative_block(buffer)
                        if narrative_block:
                            narratives.append(narrative_block)

                    elif current_kind == "scenario":
                        if current_scenario is not None:
                            scenarios.append({
                                "scenario": current_scenario,
                                "steps": current_steps
                            })
                        current_scenario = extract_scenario_block(buffer) or ""
                        current_steps = []

                    elif current_kind == "step":
                        current_steps.extend(extract_step_lines(buffer, current_step_type))

                    collecting = False
                    buffer = []
                    current_kind = None
                    current_step_type = None

                continue

            if collecting:
                buffer.append(line)
                paren_balance = count_structural_parens(block_text(buffer))

                if paren_balance <= 0:
                    block_string = extract_block_string(buffer)

                    if current_kind == "narrative":
                        narrative_block = extract_narrative_block(buffer)
                        if narrative_block:
                            narratives.append(narrative_block)

                    elif current_kind == "scenario":
                        if current_scenario is not None:
                            scenarios.append({
                                "scenario": current_scenario,
                                "steps": current_steps
                            })
                        current_scenario = extract_scenario_block(buffer) or ""
                        current_steps = []

                    elif current_kind == "step":
                        current_steps.extend(extract_step_lines(buffer, current_step_type))

                    collecting = False
                    buffer = []
                    current_kind = None
                    current_step_type = None

    if current_scenario is not None:
        scenarios.append({
            "scenario": current_scenario,
            "steps": current_steps
        })
    elif current_steps:
        scenarios.append({
            "scenario": "",
            "steps": current_steps
        })

    return metadata, narratives, scenarios


def output_name_for(file_path: Path):
    return f"{file_path.stem}_spec.txt"


def write_output(output_path: Path, metadata, narratives, scenarios):
    with output_path.open("w", encoding="utf-8") as out:
        out.write("metadata:\n")
        for key in META_KEYS:
            if key in metadata:
                out.write(f"{key}: {metadata[key]}\n")

        out.write("\n")

        for narrative in narratives:
            out.write(f"{narrative}\n\n")

        for sc in scenarios:
            if sc["scenario"]:
                out.write(f"Scenario: {sc['scenario']}\n")
                out.write("\n")
            else:
                out.write("Scenario: \n")

            for step in sc["steps"]:
                out.write(f"{step}\n")

            out.write("\n")


def process_all_files(input_root: Path, output_root: Path):
    created_files: list[Path] = []
    output_root.mkdir(parents=True, exist_ok=True)

    for file_path in input_root.rglob("*"):
        if not file_path.is_file():
            continue

        metadata, narratives, scenarios = process_file(file_path)

        if not metadata and not narratives and not scenarios:
            continue

        output_path = output_root / output_name_for(file_path)
        write_output(output_path, metadata, narratives, scenarios)
        created_files.append(output_path)

    return created_files       

def main() -> None:
    amount_files = process_all_files(INLINE_JBEHAVE_FILE_ROOT, OUTPUT_ROOT)
    print(f"Created {len(amount_files)} files and saved to {OUTPUT_ROOT}.")


if __name__ == "__main__":
    main()
