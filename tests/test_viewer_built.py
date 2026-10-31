from journal.support.viewer_built import digest, is_source_path, problems


def test_viewer_build_check_fails_when_a_newer_source_has_no_matching_bundle_stamp(tmp_path):
    web = tmp_path / "src" / "web"
    source = web / "src" / "App.vue"
    stamp = web / "dist" / "built-from"
    source.parent.mkdir(parents=True)
    stamp.parent.mkdir(parents=True)
    source.write_text("the first viewer source\n")
    stamp.write_text(digest(web))

    source.write_text("a newer viewer source\n")

    failures = problems(web)
    assert len(failures) == 1 and "Run npm --prefix src/web run build" in failures[0]


def test_package_manifest_changes_make_the_viewer_build_stale(tmp_path):
    web = tmp_path / "src" / "web"
    manifest = web / "package.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text('{"scripts": {"build": "vite build"}}\n')
    built = digest(web)

    manifest.write_text('{"scripts": {"build": "vite build --strict"}}\n')

    assert digest(web) != built
    assert is_source_path("src/web/package.json")
    assert is_source_path("src/web/package-lock.json")
