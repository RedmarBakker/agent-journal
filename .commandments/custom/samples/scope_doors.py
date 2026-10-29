class CardListener:
    def handle(self, event):
        # @sin ScopeSetOutsideDoorDetector
        with self.scope.entered(event.origin):
            return None


class Listener:
    def handle(self, event):
        # @righteous ScopeSetOutsideDoorDetector
        with self.scope.environment(event.environment_id):
            return None
