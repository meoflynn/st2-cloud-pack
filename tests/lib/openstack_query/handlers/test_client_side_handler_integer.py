import unittest
from parameterized import parameterized

from openstack_query.handlers.client_side_handler_integer import (
    ClientSideHandlerInteger,
)
from tests.lib.openstack_query.mocks.mocked_props import MockProperties

from enums.query.query_presets import QueryPresetsInteger


class ClientSideHandlerIntegerTests(unittest.TestCase):
    """
    Run various tests to ensure that ClientSideHandlerInteger class methods function expectedly
    """

    def setUp(self):
        """
        Setup for tests
        """
        super().setUp()
        _FILTER_FUNCTION_MAPPINGS = {
            preset: [MockProperties.PROP_1] for preset in QueryPresetsInteger
        }
        self.instance = ClientSideHandlerInteger(_FILTER_FUNCTION_MAPPINGS)

    @parameterized.expand(
        [(f"test {preset.name}", preset) for preset in QueryPresetsInteger]
    )
    def test_check_supported_all_presets(self, name, preset):
        """
        Tests that handler supports all generic query client_side
        """
        self.assertTrue(self.instance.check_supported(preset, MockProperties.PROP_1))

    @parameterized.expand(
        [
            ("test less than", 8, 10, True),
            ("test equal", 10, 10, False),
            ("test greater than", 10, 8, False),
        ]
    )
    def test_prop_less_than(self, name, val1, val2, expected_out):
        assert self.instance._prop_less_than(val1, val2) == expected_out

    @parameterized.expand(
        [
            ("test less than", 8, 10, False),
            ("test equal", 10, 10, False),
            ("test greater than", 10, 8, True),
        ]
    )
    def test_prop_greater_than(self, name, val1, val2, expected_out):
        assert self.instance._prop_greater_than(val1, val2) == expected_out

    @parameterized.expand(
        [
            ("test less than", 8, 10, True),
            ("test equal", 10, 10, True),
            ("test greater than", 10, 8, False),
        ]
    )
    def test_prop_less_than_or_equal_to(self, name, val1, val2, expected_out):
        assert self.instance._prop_less_than_or_equal_to(val1, val2) == expected_out

    @parameterized.expand(
        [
            ("test less than", 8, 10, False),
            ("test equal", 10, 10, True),
            ("test greater than", 10, 8, True),
        ]
    )
    def test_prop_greater_than_or_equal_to(self, name, val1, val2, expected_out):
        assert self.instance._prop_greater_than_or_equal_to(val1, val2) == expected_out
