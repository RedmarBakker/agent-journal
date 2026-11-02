def configure_grant_capabilities(story, authority, grant_id, changes: dict) -> None:
    entry = authority._latest_entry(grant_id)
    grant = authority._public_grant(entry)
    version_two = authority._grant_v2(entry, grant)
    capabilities = {**version_two["capabilities"], **changes}
    result = story.user_presses("/_supervisor/v1/enrollment/change", {
        "protocol_version": 1,
        "grant_id": grant_id,
        "expected_grant_version": grant["grant_version"],
        "change": {"kind": "configure", "grant": {**version_two, "capabilities": capabilities}},
    }, f"the owner configures {', '.join(changes)}")
    result.expect_viewer_passed()
