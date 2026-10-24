from journal.features.feature import Feature
from journal.features.phone.listeners.tunnel_settlement import TunnelSettlement
from journal.features.phone.listeners.phone_notice import PhoneNotice
from journal.features.phone.listeners.phone_paired_card import PhonePairedCard


class PhoneFeature(Feature):
    name = "phone"
    title = "Phone"
    help = "A phone paired through the tunnel reads and answers the journal from anywhere: the user shows a code on the computer, and the phone that opens it keeps a key for the days chosen."
    fixed = True
    listeners = (PhoneNotice, PhonePairedCard, TunnelSettlement)
