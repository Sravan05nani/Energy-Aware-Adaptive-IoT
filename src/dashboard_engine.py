
import pandas as pd
import numpy as np


ALGORITHMS = {
    "Fixed": "fixed_transmissions.csv.gz",
    "Rate": "rate_transmissions.csv.gz",
    "Threshold": "threshold_transmissions.csv.gz",
    "Threshold-H120": "threshold_h120_transmissions.csv.gz",
    "Threshold-H180": "threshold_h180_transmissions.csv.gz"
}


class HistoricalReplayEngine:

    def __init__(self, data, transmissions):

        self.data = data.copy()

        self.data["timestamp"] = pd.to_datetime(
            self.data["timestamp"]
        )

        self.data = self.data.sort_values(
            ["timestamp", "moteid"]
        ).reset_index(drop=True)

        self.transmissions = transmissions

        self.nodes = sorted(
            self.data["moteid"].unique().tolist()
        )

        self.cursor = 0

        self.processed = 0
        self.eligible_processed = 0
        self.transmitted = 0
        self.skipped = 0

        self.node_states = {}

        self._reset_nodes()

    def _reset_nodes(self):

        self.node_states = {}

        for node in self.nodes:

            self.node_states[int(node)] = {
                "source_temperature": None,
                "source_humidity": None,
                "source_light": None,
                "source_voltage": None,

                "received_temperature": None,
                "received_humidity": None,
                "received_light": None,
                "received_voltage": None,

                "last_transmission": None,
                "last_segment": None,

                "transmissions": 0,
                "skipped": 0,

                "last_activity": "WAITING"
            }

    @staticmethod
    def _key(node, timestamp):

        return (
            int(node),
            pd.Timestamp(timestamp).value
        )

    def reset(self):

        self.cursor = 0

        self.processed = 0
        self.eligible_processed = 0
        self.transmitted = 0
        self.skipped = 0

        self._reset_nodes()

    def step(self):

        if self.cursor >= len(self.data):
            return None

        row = self.data.iloc[self.cursor]

        self.cursor += 1
        self.processed += 1

        node = int(row["moteid"])

        state = self.node_states[node]

        timestamp = pd.Timestamp(row["timestamp"])

        segment = row.get("segment_id", None)

        # Clear old received data when a new source segment begins.
        if pd.notna(segment):

            if (
                state["last_segment"] is not None
                and state["last_segment"] != segment
            ):

                state["received_temperature"] = None
                state["received_humidity"] = None
                state["received_light"] = None
                state["received_voltage"] = None

                state["last_transmission"] = None

            state["last_segment"] = segment

        eligible = bool(row["environment_valid"])

        # Update actual historical sensor measurements.
        if eligible:

            self.eligible_processed += 1

            state["source_temperature"] = row["temperature_clean"]
            state["source_humidity"] = row["humidity_clean"]
            state["source_light"] = row["light_clean"]

            voltage = row.get("voltage_clean", np.nan)

            state["source_voltage"] = (
                None if pd.isna(voltage) else float(voltage)
            )

            key = self._key(node, timestamp)

            packet = self.transmissions.get(key)

            if packet is not None:

                state["received_temperature"] = packet.get(
                    "temperature"
                )

                state["received_humidity"] = packet.get(
                    "humidity"
                )

                state["received_light"] = packet.get(
                    "light"
                )

                packet_voltage = packet.get("voltage")

                state["received_voltage"] = (
                    None if pd.isna(packet_voltage)
                    else packet_voltage
                )

                state["last_transmission"] = timestamp

                state["transmissions"] += 1

                state["last_activity"] = "TRANSMITTED"

                self.transmitted += 1

            else:

                state["skipped"] += 1

                state["last_activity"] = "SKIPPED"

                self.skipped += 1

        age = None

        if state["last_transmission"] is not None:

            age = (
                timestamp - state["last_transmission"]
            ).total_seconds()

        return {
            "timestamp": timestamp,
            "node": node,
            "eligible": eligible,
            "activity": state["last_activity"],
            "freshness_age_sec": age,
            "node_state": state.copy(),
            "progress": self.progress()
        }

    def progress(self):

        return {
            "processed": self.processed,
            "total_records": len(self.data),
            "eligible_processed": self.eligible_processed,
            "transmitted": self.transmitted,
            "skipped": self.skipped,
            "progress_percent": (
                self.cursor / len(self.data) * 100
            )
        }

    def get_node_states(self):

        return self.node_states
