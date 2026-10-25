"""Free disposable Docker artifacts before a build on the single production VM."""

import fcntl
import json
import os
from pathlib import Path
import re
import shutil
import subprocess


REPOSITORY = "ghcr.io/shinytsing/modeshift_django"
RELEASE_TAG = re.compile(re.escape(REPOSITORY) + r":[0-9a-f]{40}$")
MIN_FREE = 8 * 1024**3


def removable_tags(images, protected):
    """Keep container/pinned images, non-release aliases and the latest two releases."""
    releases = [image for image in images if any(RELEASE_TAG.fullmatch(tag) for tag in image.get("RepoTags") or [])]
    keep = set(protected) | {image["Id"] for image in sorted(releases, key=lambda image: image["Created"], reverse=True)[:2]}
    for image in releases:
        tags = image.get("RepoTags") or []
        if image["Id"] in keep or any(not RELEASE_TAG.fullmatch(tag) for tag in tags):
            continue
        yield from tags


def docker(*arguments):
    return subprocess.check_output(["docker", *arguments], text=True).strip()


def free_space():
    # This single-VM deployment stores Docker and the project on the root disk.
    return shutil.disk_usage("/").free


def prepare(project):
    print(f"Root disk available before cleanup: {free_space() / 1024**3:.1f} GiB", flush=True)
    if free_space() >= MIN_FREE:
        return
    subprocess.run(["docker", "builder", "prune", "--force", "--filter", "until=24h"], check=True)
    container_ids = docker("ps", "-aq").split()
    protected = set(docker("inspect", "--format", "{{.Image}}", *container_ids).split()) if container_ids else set()
    references = {os.environ.get("QATOOLBOX_IMAGE", "")}
    for name in (".env", ".deployed-image.env"):
        path = project / name
        if path.exists():
            for line in path.read_text().splitlines():
                key, _, value = line.partition("=")
                if key.strip() in {"QATOOLBOX_IMAGE", "QATOOLBOX_PREVIOUS_IMAGE"}:
                    references.add(value.strip().strip("\"'"))
    for reference in references - {""}:
        result = subprocess.run(
            ["docker", "image", "inspect", "--format", "{{.Id}}", reference], capture_output=True, text=True
        )
        if result.returncode == 0:
            protected.add(result.stdout.strip())
    image_ids = sorted(set(docker("image", "ls", "--no-trunc", "--format", "{{.ID}}", REPOSITORY).split()))
    images = json.loads(docker("image", "inspect", *image_ids)) if image_ids else []
    for tag in removable_tags(images, protected):
        print(f"Removing unused old release: {tag}", flush=True)
        # No force: Docker refuses deletion if a container starts using it.
        subprocess.run(["docker", "image", "rm", tag], check=True)
    if free_space() < MIN_FREE:
        subprocess.run(["docker", "builder", "prune", "--all", "--force"], check=True)
    available = free_space()
    print(f"Root disk available after cleanup: {available / 1024**3:.1f} GiB", flush=True)
    if available < MIN_FREE:
        raise SystemExit("Less than 8 GiB free; build/deploy stopped. Expand disk or review usage; volumes were not pruned.")


if __name__ == "__main__":
    project = Path(os.environ.get("QATOOLBOX_DIR", str(Path.home() / "modeshift_django")))
    project.mkdir(parents=True, exist_ok=True)
    with (project / ".production-start.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        prepare(project)
