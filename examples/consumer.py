# Example only: how another Intelligent Contract can consume Chronicle.

from genlayer import *


@gl.contract_interface
class IChronicle:
    class View:
        def get_relation(self, timeline_id: u256, event_a: u256, event_b: u256) -> dict: ...
        def is_before(self, timeline_id: u256, event_a: u256, event_b: u256) -> bool: ...


class ChronologyConsumer(gl.Contract):
    chronicle_address: Address

    def __init__(self, chronicle_address: Address):
        self.chronicle_address = chronicle_address

    @gl.public.view
    def cancellation_preceded_fulfillment(
        self,
        timeline_id: u256,
        cancellation_event: u256,
        fulfillment_event: u256,
    ) -> bool:
        chronicle = gl.get_contract_at(self.chronicle_address, IChronicle)
        return chronicle.view().is_before(timeline_id, cancellation_event, fulfillment_event)
