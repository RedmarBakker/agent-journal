from supervisor.service import Service


class Services:
    """The named processes a supervisor runs beside the agent, each running until it is stopped; a child runs only while the service it names as its parent runs, is started after it and stopped before it."""

    def __init__(self, *services: Service) -> None:
        self._table = {service.name: service for service in services}

    def service(self, name: str) -> Service:
        if name not in self._table:
            raise LookupError(f"no process is named {name!r}")
        return self._table[name]

    def runs(self, name: str) -> bool:
        return name in self._table and self._table[name].is_active()

    def add(self, service: Service) -> None:
        if service.parent and not self.runs(service.parent):
            raise LookupError(f"{service.name} is a child of {service.parent}, which is not running")
        if self.runs(service.name):
            return
        self._table[service.name] = service
        service.start()

    def remove(self, name: str) -> None:
        for child in self.children(name):
            self.remove(child.name)
        self.service(name).stop()
        del self._table[name]

    def children(self, name: str) -> list[Service]:
        return [service for service in self._table.values() if service.parent == name]

    def start_all(self) -> None:
        for service in self._table.values():
            service.start()

    def revive_stopped(self) -> None:
        for service in list(self._table.values()):
            if service.parent and not self.runs(service.parent):
                self.remove(service.name)
            else:
                service.revive()

    def described(self) -> list[dict]:
        return [service.described() for service in self._table.values()]

    def stop_all(self) -> None:
        for service in sorted(self._table.values(), key=lambda service: not service.parent):
            service.stop()
