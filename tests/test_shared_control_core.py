from grc_control_core import __version__, load_schema


def test_shared_control_core_release_is_explicitly_approved():
    assert __version__ == "0.1.0"
    assert load_schema("finding-v1.schema.json")["title"] == "GRC Finding v1"
