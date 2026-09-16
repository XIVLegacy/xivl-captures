"""External private originals need an immutable locator, not an in-repo cache."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import validate_schemas


class PrivateSourceStorageTests(unittest.TestCase):
    def check(self, document, public_shape=False):
        results = []
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(validate_schemas, "CORPUS_ABSENT", public_shape):
                validate_schemas.check_source_objects(
                    Path(directory) / "web-source", document, results, []
                )
        self.assertEqual(len(results), 1)
        return results[0]

    def private_source(self):
        return {
            "storage": {
                "original_state": "private-repository",
                "repository": "example/private-inputs",
                "path": "web-sources/source.zip",
                "commit": "a" * 40,
                "master_archive": {
                    "file": "source.zip",
                    "sha256": "b" * 64,
                    "size_bytes": 123,
                },
            },
            "members": [],
        }

    def test_private_archive_requires_no_local_original(self):
        _, passed, detail = self.check(self.private_source())
        self.assertTrue(passed)
        self.assertIn("external bytes not verified", detail)

    def test_unpinned_private_archive_fails(self):
        for field in ("commit", "repository", "path"):
            with self.subTest(field=field):
                document = self.private_source()
                del document["storage"][field]
                self.assertFalse(self.check(document)[1])
        for field, value in (
            ("sha256", "bad"),
            ("size_bytes", 0),
            ("file", "different.zip"),
        ):
            with self.subTest(field=field):
                document = self.private_source()
                document["storage"]["master_archive"][field] = value
                self.assertFalse(self.check(document)[1])

    def test_missing_in_repo_original_still_fails(self):
        document = {"storage": {"original_state": "in-repo"}, "members": []}
        self.assertFalse(self.check(document)[1])

    def test_malformed_private_metadata_fails_without_exception(self):
        for field, value in (("master_archive", ["source.zip"]), ("path", 123)):
            with self.subTest(field=field):
                document = self.private_source()
                document["storage"][field] = value
                self.assertFalse(self.check(document)[1])

    def test_private_archive_path_is_repository_relative(self):
        for path in (
            "/source.zip",
            "../source.zip",
            "nested/../source.zip",
            "C:\\source.zip",
        ):
            with self.subTest(path=path):
                document = self.private_source()
                document["storage"]["path"] = path
                self.assertFalse(self.check(document)[1])

    def test_public_shape_still_requires_private_archive_pin(self):
        document = self.private_source()
        self.assertTrue(self.check(document, public_shape=True)[1])
        del document["storage"]["commit"]
        self.assertFalse(self.check(document, public_shape=True)[1])


if __name__ == "__main__":
    unittest.main()
