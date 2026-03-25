from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Dict, Any


def _read_lines(file_path) -> list[str]:
    path = Path(file_path)
    with path.open("r", encoding="utf-8") as f:
        return f.readlines()


def read_SOP(file_path) -> Dict[str, Dict[str, str]]:
    lines = _read_lines(file_path)

    sop: Dict[str, Dict[str, str]] = {}
    byte: Dict[str, str] = {}
    bit = "0"

    for i, raw_line in enumerate(lines):
        line = raw_line.replace("\t", "")
        if i % 8 == 0:
            bit = line[0:len(str(i // 8))]
            byte = {}

        byte[line[6]] = line[12:].replace("\n", "").replace(" ", "")
        sop[bit] = byte

    return sop


def get_container(file_path) -> Dict[str, Dict[str, str]]:
    lines = _read_lines(file_path)

    state_container: Dict[str, Dict[str, str]] = {}
    byte: Dict[str, str] = {}
    bit = "0"
    count = 1

    for i, raw_line in enumerate(lines):
        line = raw_line.replace("\t", "")
        if i % 8 == 0:
            bit = line[0:len(str(i // 8))]
            byte = {}

        signal = line[12:].replace("\n", "").replace(" ", "")
        if signal == "":
            signal = f"null_{bit}_{count}"
            count += 1

        byte[signal] = ""
        state_container[bit] = byte

    return state_container


def get_address_update_state_container(file_path) -> Dict[str, int]:
    lines = _read_lines(file_path)

    address_update_state_container: Dict[str, int] = {}
    bit = "0"

    for i, raw_line in enumerate(lines):
        line = raw_line.replace("\t", "")
        if i % 8 == 0:
            bit = line[0:len(str(i // 8))]
        address_update_state_container[bit] = 0

    return address_update_state_container


def build_sop_bundle(file_path) -> Dict[str, Any]:
    return {
        "sop": read_SOP(file_path),
        "state_container": get_container(file_path),
        "address_update_state_container": get_address_update_state_container(file_path),
    }


def _write_json_file(output_path: Path, value) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
    return output_path


def generate_runtime_jsons(file_path, output_dir=None) -> Dict[str, str]:
    source_path = Path(file_path).resolve()

    if output_dir is None:
        # 当前 SOP.py 位于 项目根目录/SOP_con/SOP.py
        # 默认输出到当前文件所在目录，即 SOP_con/
        output_dir = Path(__file__).resolve().parent
    else:
        output_dir = Path(output_dir).resolve()

    bundle = build_sop_bundle(source_path)

    sop_json = _write_json_file(output_dir / "DY_SOP.json", bundle["sop"])
    state_json = _write_json_file(output_dir / "DY_state_container.json", bundle["state_container"])
    address_json = _write_json_file(
        output_dir / "DY_address_update_state_container.json",
        bundle["address_update_state_container"]
    )

    return {
        "source_sop_path": str(source_path),
        "DY_SOP.json": str(sop_json),
        "DY_state_container.json": str(state_json),
        "DY_address_update_state_container.json": str(address_json),
    }


def prepare_sop_for_runtime(file_path, project_root=None, copy_source_to_sop_dir=True) -> Dict[str, str]:
    source_path = Path(file_path).resolve()

    if project_root is None:
        # 当前 SOP.py 位于 项目根目录/SOP_con/SOP.py
        # 因此项目根目录应取上一级
        project_root = Path(__file__).resolve().parent.parent
    else:
        project_root = Path(project_root).resolve()

    sop_dir = project_root / "sop"
    sop_con_dir = project_root / "SOP_con"

    sop_dir.mkdir(parents=True, exist_ok=True)
    sop_con_dir.mkdir(parents=True, exist_ok=True)

    active_sop_path = source_path
    if copy_source_to_sop_dir:
        copied_path = sop_dir / source_path.name
        shutil.copy2(source_path, copied_path)
        active_sop_path = copied_path

    generated = generate_runtime_jsons(active_sop_path, sop_con_dir)
    generated["active_sop_path"] = str(active_sop_path)

    return generated


if __name__ == "__main__":
    default_path = Path("C:/Users/92588/Desktop/TRT1.DY2_2.SOP")
    if default_path.exists():
        result = prepare_sop_for_runtime(default_path)
        print(result)
    else:
        print(f"SOP file not found: {default_path}")