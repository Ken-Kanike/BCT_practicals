#!/usr/bin/env python3
"""Extract readable evidence lines from the Fabric deployment/invoke logs."""
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "experiments" / "05-hyperledger-chaincode"
ANSI = re.compile(r"\x1b\[[0-9;]*m")


def clean(path: Path) -> list[str]:
    return [ANSI.sub("", line).rstrip() for line in path.read_text(errors="replace").splitlines()]


deploy = clean(BASE / "deploy_chaincode.log")
deploy_keys = (
    "Vendoring Go dependencies",
    "Finished vendoring",
    "Chaincode is packaged",
    "Chaincode code package identifier",
    "Installed chaincode",
    "Chaincode definition approved",
    "Chaincode definition committed",
    "Committed chaincode definition",
    "Version:",
    "Approvals:",
    "Chaincode initialization",
)
deploy_summary = [line for line in deploy if any(key in line for key in deploy_keys)]
(BASE / "output" / "deploy_summary.log").write_text("\n".join(deploy_summary) + "\n")

demo = clean(BASE / "output" / "chaincode_demo.log")
demo_keys = ("===", "Committed chaincode", "Version:", "Approvals:")
demo_summary = []
for line in demo:
    stripped = line.strip()
    if stripped.startswith(demo_keys) or stripped.startswith("{") or stripped.startswith("["):
        demo_summary.append(line)
    elif stripped in {"true", "false"} or "ReadAsset rejected" in stripped:
        demo_summary.append(line)
(BASE / "output" / "chaincode_demo_summary.log").write_text("\n".join(demo_summary) + "\n")

print(f"deploy summary: {len(deploy_summary)} lines")
print(f"demo summary:   {len(demo_summary)} lines")
