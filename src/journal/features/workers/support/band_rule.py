from dataclasses import dataclass

from journal.models.support.pressure_band import PressureBand


@dataclass(frozen=True)
class BandRule:
    """How one mode's band moves on the smoothed worker queue ρ, with hysteresis: it enters high at one level and leaves under a lower one, enters low under one level and leaves at a higher one, leaves high also once no worker item has waited for the quiet minutes and never enters it on a queue empty that long, and holds a band the held minutes before any other change."""

    high_entry: float
    high_exit: float
    low_entry: float
    low_exit: float
    least_band_seconds: float
    empty_queue_seconds: float

    def moved(self, band: PressureBand, rho: float, band_age_seconds: float, empty_seconds: float) -> PressureBand:
        if band == PressureBand.HIGH and empty_seconds >= self.empty_queue_seconds:
            return PressureBand.NORMAL
        if band_age_seconds < self.least_band_seconds:
            return band
        next_band = self.next_band(band, rho)
        return PressureBand.NORMAL if next_band == PressureBand.HIGH and empty_seconds >= self.empty_queue_seconds else next_band

    def next_band(self, band: PressureBand, rho: float) -> PressureBand:
        if band == PressureBand.HIGH:
            return PressureBand.HIGH if rho >= self.high_exit else self.resting(rho)
        if band == PressureBand.LOW:
            return PressureBand.LOW if rho < self.low_exit else self.resting(rho)
        return self.resting(rho)

    def resting(self, rho: float) -> PressureBand:
        if rho >= self.high_entry:
            return PressureBand.HIGH
        return PressureBand.LOW if rho < self.low_entry else PressureBand.NORMAL
