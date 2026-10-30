from journal.repositories.setting_rows import SettingRows


def test_setting_rows(app):
    # @sin TestSettingWriteDetector
    app.container.get(SettingRows).set("workers.mode", "solo", None)
    settings = app.container.get(SettingRows)
    # @sin TestSettingsVariableWriteDetector
    settings.set("workers.mode", "solo", None)
