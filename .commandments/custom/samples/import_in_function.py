# @righteous ImportInFunctionDetector
import json


def parsed(text: str) -> dict:
    return json.loads(text)


def encoded(values: dict) -> str:
    # @sin ImportInFunctionDetector
    import json as encoder
    return encoder.dumps(values)
