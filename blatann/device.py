from blatann.nrf.nrf_driver import NrfDriver
from blatann.nrf.nrf_observers import NrfDriverObserver
from blatann.nrf import nrf_events, nrf_event_sync

from blatann import uuid, advertising, scanning, peer, gatts


class BleDevice(NrfDriverObserver):
    def __init__(self, comport="COM1"):
        self.ble_driver = NrfDriver(comport)
        self.ble_driver.observer_register(self)
        self.ble_driver.event_subscribe(self._on_user_mem_request, nrf_events.EvtUserMemoryRequest)
        self.ble_driver.open()
        # TODO: BLE Configuration
        self.ble_driver.ble_enable()

        self.client = peer.Peer()
        self.peripherals = []

        self.uuid_manager = uuid.UuidManager(self.ble_driver)
        self.advertiser = advertising.Advertiser(self, self.client)
        self.scanner = scanning.Scanner(self)
        self._db = gatts.GattsDatabase(self, self.client)

    def __del__(self):
        self.ble_driver.observer_unregister(self)
        self.ble_driver.close()

    @property
    def database(self):
        return self._db

    def _on_user_mem_request(self, nrf_driver, event):
        # Only action that can be taken
        self.ble_driver.ble_user_mem_reply(event.conn_handle)

    def on_driver_event(self, nrf_driver, event):
        print("Got driver event: {}".format(event))
        if isinstance(event, nrf_events.GapEvtConnected):
            if event.role == nrf_events.BLEGapRoles.periph:
                self.client.peer_connected(event.conn_handle, event.peer_addr)
        elif isinstance(event, nrf_events.GapEvtDisconnected):
            if event.conn_handle == self.client.conn_handle:
                self.client.peer_disconnected()
