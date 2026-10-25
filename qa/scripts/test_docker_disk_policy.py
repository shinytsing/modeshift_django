"""Protect production and rollback images during bounded release cleanup."""

import importlib.util
from pathlib import Path
import unittest


path = Path(__file__).resolve().parents[2] / "scripts/maintenance/prepare_docker_disk.py"
spec = importlib.util.spec_from_file_location("prepare_docker_disk", path)
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


def image(number, tags=None):
    return {
        "Id": f"sha256:{number:064x}",
        "Created": f"2026-10-{number:02d}T00:00:00Z",
        "RepoTags": tags if tags is not None else [f"{policy.REPOSITORY}:{number:040x}"],
    }


class DockerDiskPolicyTests(unittest.TestCase):
    def test_running_and_pinned_images_are_retained_even_when_old(self):
        images = [image(number) for number in range(1, 6)]
        tags = list(policy.removable_tags(images, {images[0]["Id"], images[1]["Id"]}))
        self.assertEqual(tags, images[2]["RepoTags"])

    def test_latest_two_releases_are_kept_without_containers(self):
        images = [image(number) for number in range(1, 4)]
        self.assertEqual(list(policy.removable_tags(images, set())), images[0]["RepoTags"])

    def test_other_repositories_and_custom_aliases_are_not_deleted(self):
        images = [
            image(1, [f"{policy.REPOSITORY}:{1:040x}", "other-project:stable"]),
            image(2, ["postgres:15-alpine"]),
            image(3, [f"{policy.REPOSITORY}:main"]),
            image(4),
            image(5),
        ]
        self.assertEqual(list(policy.removable_tags(images, set())), [])

    def test_all_sha_aliases_of_one_unused_image_are_removed(self):
        old = image(1, [f"{policy.REPOSITORY}:{1:040x}", f"{policy.REPOSITORY}:{2:040x}"])
        self.assertEqual(list(policy.removable_tags([old, image(3), image(4)], set())), old["RepoTags"])

    def test_empty_and_untagged_images_are_ignored(self):
        self.assertEqual(list(policy.removable_tags([], set())), [])
        self.assertEqual(list(policy.removable_tags([image(1, [])], set())), [])


if __name__ == "__main__":
    unittest.main()
