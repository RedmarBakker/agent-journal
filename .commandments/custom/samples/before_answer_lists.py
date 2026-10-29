class SkillObligation:
    # @sin BeforeAnswerOutsideListDetector
    blocking = "next decision"

    def handle(self, event):
        return None


class Skills:
    # @righteous BeforeAnswerOutsideListDetector
    answer_listeners = ((SkillObligation, "next decision"),)
