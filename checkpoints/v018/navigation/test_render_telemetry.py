"""Standard-Python telemetry tests; no Blender or actual Windows runtime needed."""
import builtins
import importlib.util
import json
from pathlib import Path
import types
import unittest
from unittest import mock

import render_manifest_still as render


class RenderTelemetry(unittest.TestCase):
    def test_import_does_not_load_blender_or_resource(self):
        original_import = builtins.__import__

        def guarded_import(name, *args, **kwargs):
            if name in ('bpy', 'mathutils', 'resource'):
                raise AssertionError('Optional/render dependency imported eagerly: ' + name)
            return original_import(name, *args, **kwargs)

        spec = importlib.util.spec_from_file_location('renderer_import_probe', Path(render.__file__))
        module = importlib.util.module_from_spec(spec)
        with mock.patch('builtins.__import__', side_effect=guarded_import):
            spec.loader.exec_module(module)
        self.assertTrue(callable(module.main))

    def test_linux_value_preserved_without_conversion(self):
        value = 123456
        fake = types.SimpleNamespace(RUSAGE_SELF=0, getrusage=mock.Mock(
            return_value=types.SimpleNamespace(ru_maxrss=value)))
        with mock.patch.object(render.sys, 'platform', 'linux'), mock.patch.dict('sys.modules', resource=fake):
            self.assertEqual(render.peak_rss_linux_kib(), value)
        fake.getrusage.assert_called_once_with(fake.RUSAGE_SELF)

    def test_unsupported_platforms_do_not_import_resource(self):
        for platform in ('win32', 'darwin', 'freebsd14'):
            with self.subTest(platform=platform), mock.patch.object(render.sys, 'platform', platform):
                with mock.patch('builtins.__import__', side_effect=AssertionError('No resource import allowed')):
                    self.assertIsNone(render.peak_rss_linux_kib())

    def test_missing_resource_on_linux_is_optional(self):
        with mock.patch.object(render.sys, 'platform', 'linux'), mock.patch.dict('sys.modules', resource=None):
            self.assertIsNone(render.peak_rss_linux_kib())

    def test_resource_oserror_is_optional(self):
        fake = types.SimpleNamespace(RUSAGE_SELF=0, getrusage=mock.Mock(side_effect=OSError('unavailable')))
        with mock.patch.object(render.sys, 'platform', 'linux'), mock.patch.dict('sys.modules', resource=fake):
            self.assertIsNone(render.peak_rss_linux_kib())

    def test_optional_api_failure_is_not_a_render_failure(self):
        for fake in (types.SimpleNamespace(), types.SimpleNamespace(
                RUSAGE_SELF=0, getrusage=mock.Mock(side_effect=RuntimeError('telemetry unavailable')))):
            with mock.patch.object(render.sys, 'platform', 'linux'), mock.patch.dict('sys.modules', resource=fake):
                self.assertIsNone(render.peak_rss_linux_kib())

    def test_unavailable_serializes_as_explicit_null(self):
        with mock.patch.object(render.sys, 'platform', 'win32'):
            self.assertEqual(json.dumps({'peak_rss_linux_kib': render.peak_rss_linux_kib()}),
                             '{"peak_rss_linux_kib": null}')

    def test_control_flow_interrupts_not_swallowed(self):
        fake = types.SimpleNamespace(RUSAGE_SELF=0, getrusage=mock.Mock(side_effect=KeyboardInterrupt))
        with mock.patch.object(render.sys, 'platform', 'linux'), mock.patch.dict('sys.modules', resource=fake):
            with self.assertRaises(KeyboardInterrupt):
                render.peak_rss_linux_kib()


if __name__ == '__main__':
    unittest.main()
