from journal.support.card_family import CardFamily
from journal.support.card_type_entry import CardTypeEntry
from journal.support.mark_kinds import JOURNAL
from journal.support.card_type import CardType
from journal.features.feature import Feature
from journal.features.phone.listeners.tunnel_settlement import TunnelSettlement
from journal.features.phone.listeners.phone_notice import PhoneNotice
from journal.features.phone.listeners.phone_paired_card import PhonePairedCard


class PhoneFeature(Feature):
    name = "phone"
    card_families = (CardFamily("phones", "Phones", "phone", JOURNAL),)
    card_kinds = (CardTypeEntry(CardType.PHONES, "Phones paired", "phones"),)
    title = "Phone"
    help = "A phone paired through the tunnel reads and answers the journal from anywhere: the user shows a code on the computer, and the phone that opens it keeps a key for the days chosen."
    fixed = True
    listeners = (PhoneNotice, PhonePairedCard, TunnelSettlement)
