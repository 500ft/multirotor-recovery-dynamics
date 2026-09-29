"""Host-side demux/manifest tests. No serial port or CircuitPython needed --
`demux()` takes any iterable of lines, so these feed synthetic firmware
output directly."""
import csv
import json
import tempfile
import unittest
from pathlib import Path

from Instrumentation.bench_capture import demux


def _rec(sensor, seq, epoch=0, **fields):
    return json.dumps({"sensor": sensor, "epoch": epoch, "seq": seq,
                        "t_device_us": seq * 1000, **fields})


class DemuxTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.out = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_demuxes_two_sensors_into_separate_csvs(self):
        lines = [
            _rec("_meta", 0, event="boot"),
            _rec("nau7802", 0, raw_adc=100),
            _rec("beam", 0, state="clear"),
            _rec("nau7802", 1, raw_adc=101),
        ]
        manifest = demux(lines, self.out)
        self.assertTrue(manifest["complete"])
        self.assertEqual(manifest["sensors"]["nau7802"]["rows"], 2)
        self.assertEqual(manifest["sensors"]["beam"]["rows"], 1)
        self.assertNotIn("_meta", manifest["sensors"])
        with (self.out / "nau7802.csv").open() as fh:
            rows = list(csv.DictReader(fh))
        self.assertEqual([r["raw_adc"] for r in rows], ["100", "101"])

    def test_seq_gap_is_recorded_not_hidden(self):
        lines = [_rec("nau7802", 0, raw_adc=1), _rec("nau7802", 1, raw_adc=2),
                 _rec("nau7802", 5, raw_adc=3)]
        manifest = demux(lines, self.out)
        self.assertEqual(manifest["sensors"]["nau7802"]["gaps"], [[1, 5]])
        self.assertTrue(manifest["complete"])  # a gap alone is not incompleteness

    def test_epoch_change_marks_run_incomplete_not_spliced(self):
        lines = [_rec("nau7802", 0, epoch=0, raw_adc=1),
                 _rec("nau7802", 0, epoch=1, raw_adc=2)]  # device reset between records
        manifest = demux(lines, self.out)
        self.assertFalse(manifest["complete"])
        self.assertIn("reset", manifest["incomplete_reason"])
        self.assertEqual(manifest["epochs_seen"], [0, 1])
        # both rows are still on disk -- nothing is dropped, just not certified complete
        self.assertEqual(manifest["sensors"]["nau7802"]["rows"], 2)

    def test_schema_change_mid_run_is_rejected_not_coerced(self):
        lines = [_rec("lis3dh", 0, x_m_s2=0.1),
                 _rec("lis3dh", 1, x_m_s2=0.1, extra_field=9)]
        manifest = demux(lines, self.out)
        self.assertFalse(manifest["complete"])
        self.assertIn("schema changed", manifest["incomplete_reason"])
        self.assertEqual(manifest["sensors"]["lis3dh"]["rows"], 1)  # second row not written

    def test_malformed_line_is_counted_and_skipped(self):
        lines = [_rec("nau7802", 0, raw_adc=1), "not json{{{", "", _rec("nau7802", 1, raw_adc=2)]
        manifest = demux(lines, self.out)
        self.assertEqual(manifest["malformed_lines"], 1)
        self.assertEqual(manifest["sensors"]["nau7802"]["rows"], 2)

    def test_record_missing_sensor_or_epoch_is_malformed(self):
        lines = [json.dumps({"seq": 0}), json.dumps({"sensor": "nau7802"})]
        manifest = demux(lines, self.out)
        self.assertEqual(manifest["malformed_lines"], 2)
        self.assertEqual(manifest["sensors"], {})

    def test_manifest_written_to_disk(self):
        demux([_rec("beam", 0, state="clear")], self.out)
        with (self.out / "manifest.json").open() as fh:
            on_disk = json.load(fh)
        self.assertEqual(on_disk["sensors"]["beam"]["rows"], 1)


if __name__ == "__main__":
    unittest.main()
