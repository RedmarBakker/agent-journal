from functools import partial


class Receiver:
    def recorded_outcome(self, entry, fault):
        # @sin MeasurementBeforeAnswerDetector
        self.fault_log.reported("listener before the answer", fault)

    def measure_stored(self, entry, fault):
        # @righteous MeasurementBeforeAnswerDetector
        self.deferred.add(partial(self.fault_log.reported, "listener before the answer", fault))
