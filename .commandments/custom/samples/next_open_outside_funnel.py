class WaitLines:
    def line(self, data):
        # @sin NextOpenOutsideFunnelDetector
        work = data.part(TasksPart).next_open
        # @righteous NextOpenOutsideFunnelDetector
        return data.next_work() or work
