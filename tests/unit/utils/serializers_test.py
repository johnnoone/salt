# -*- coding: utf-8 -*-

# Import Salt Testing libs
from salttesting import skipIf, TestCase
from salttesting.helpers import ensure_in_syspath
ensure_in_syspath('../../')

# Import salt libs
from salt.utils.serializers import json, silas, yaml
from salt.utils.odict import OrderedDict

class TestSerializers(TestCase):
    def test_serialize_json(self):
        data = {
            "foo": "bar"
        }
        serialized = json.serialize(data)
        assert serialized == '{"foo": "bar"}', serialized

        deserialized = json.deserialize(serialized)
        assert deserialized == data, deserialized

    def test_serialize_yaml(self):
        data = {
            "foo": "bar"
        }
        serialized = yaml.serialize(data)
        assert serialized == '{foo: bar}', serialized

        deserialized = yaml.deserialize(serialized)
        assert deserialized == data, deserialized

    def test_serialize_silas(self):
        data = {
            "foo": "bar"
        }
        serialized = silas.serialize(data)
        assert serialized == '{foo: bar}', serialized

        deserialized = silas.deserialize(serialized)
        assert deserialized == data, deserialized

    def test_serialize_complex_silas(self):
        data = OrderedDict([
            ("foo", 1),
            ("bar", 2),
            ("baz", True),
        ])
        serialized = silas.serialize(data)
        assert serialized == '{foo: 1, bar: 2, baz: true}', serialized

        deserialized = silas.deserialize(serialized)
        assert deserialized == data, deserialized


if __name__ == '__main__':
    from integration import run_tests
    run_tests(TestSerializers, needs_daemon=False)
