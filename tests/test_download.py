"""Download Tests"""

import json
import pytest

from databusclient.api.download import (
    download as api_download,
    _parse_version_key,
    _get_databus_versions_of_artifact,
)


# TODO: overall test structure not great, needs refactoring

DEFAULT_ENDPOINT = "https://databus.dbpedia.org/sparql"
TEST_QUERY = """
PREFIX dcat: <http://www.w3.org/ns/dcat#>
SELECT ?file
WHERE {
  ?file dcat:downloadURL ?url ;
        dcat:byteSize ?size .
  FILTER(STRSTARTS(STR(?file), "https://databus.dbpedia.org/dbpedia/"))
  FILTER(xsd:integer(?size) < 104857600)
}
LIMIT 10
"""
TEST_COLLECTION = (
    "https://databus.dbpedia.org/dbpedia/collections/dbpedia-snapshot-2022-12"
)


def test_with_query():
    api_download("tmp", DEFAULT_ENDPOINT, [TEST_QUERY])


@pytest.mark.skip(
    reason="Live collection download is long-running and flakes on network timeouts"
)
@pytest.mark.skip(
    reason="Integration test: requires live databus.dbpedia.org connection"
)
def test_with_collection():
    api_download("tmp", DEFAULT_ENDPOINT, [TEST_COLLECTION])


@pytest.mark.parametrize(
    "versions, expected_order",
    [
        # ISO dates
        (
            ["2026-09-17", "2026-09-18", "2025-12-31"],
            ["2026-09-18", "2026-09-17", "2025-12-31"],
        ),
        # CalVer
        (
            ["2026.09.17", "2026.10.01", "2026.09.05"],
            ["2026.10.01", "2026.09.17", "2026.09.05"],
        ),
        # Pure numeric
        (
            ["9", "10", "1"],
            ["10", "9", "1"],
        ),
        # Dotted numeric
        (
            ["2.9", "2.10", "2.1"],
            ["2.10", "2.9", "2.1"],
        ),
        # Stable SemVer
        (
            ["2.9.0", "2.10.0", "2.1.0"],
            ["2.10.0", "2.9.0", "2.1.0"],
        ),
        # v-prefixed numeric
        (
            ["v2.9.0", "v2.10.0", "v2.1.0"],
            ["v2.10.0", "v2.9.0", "v2.1.0"],
        ),
    ],
)
def test_parse_version_key_sorting(versions, expected_order):
    assert sorted(versions, key=_parse_version_key, reverse=True) == expected_order


