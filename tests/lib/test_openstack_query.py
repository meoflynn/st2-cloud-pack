import datetime
import unittest
from unittest import mock
from unittest.mock import MagicMock

from openstack_api.openstack_query import OpenstackQuery


class OpenstackQueryTests(unittest.TestCase):
    """
    Runs various tests to ensure OpenstackQuery functions in the expected way
    """

    # pylint:disable=too-few-public-methods
    class ItemTest:
        def __init__(self, test1, test2):
            self.test1 = test1
            self.test2 = test2
            self.user_id = test1

        def __getitem__(self, key):
            return getattr(self, key)

    def setUp(self) -> None:
        super().setUp()
        self.mocked_connection = MagicMock()
        self.instance = OpenstackQuery(self.mocked_connection)
        self.identity_api = (
            self.mocked_connection.return_value.__enter__.return_value.identity
        )

    @mock.patch("openstack_api.openstack_query.datetime", wraps=datetime)
    def test_datetime_before_x_days(self, mock_datetime):
        """
        Tests datetime_before_x_days works as expected
        """
        mock_datetime.datetime.now.return_value = datetime.datetime(2021, 8, 1)

        # Should pass
        assert (
            self.instance.datetime_before_x_days(
                "2021-06-28T14:00:00Z", 20, "%Y-%m-%dT%H:%M:%SZ"
            )
            is True
        )

        # Should fail
        assert (
            self.instance.datetime_before_x_days(
                "2021-07-28T14:00:00Z", 20, "%Y-%m-%dT%H:%M:%SZ"
            )
            is False
        )

        # Edgecases
        assert (
            self.instance.datetime_before_x_days(
                "2021-07-11T23:59:59Z", 20, "%Y-%m-%dT%H:%M:%SZ"
            )
            is True
        )

        assert (
            self.instance.datetime_before_x_days(
                "2021-07-12T00:00:01Z", 20, "%Y-%m-%dT%H:%M:%SZ"
            )
            is False
        )

    def test_apply_query(self):
        """
        Tests apply_query works as expected
        """

        items = [1, 2, 3, 4]

        assert self.instance.apply_query(items, lambda item: True) == items
        assert not self.instance.apply_query(items, lambda item: False)
        assert self.instance.apply_query(items, lambda item: item > 2) == [3, 4]

    def test_parse_properties(self):
        """
        Tests parse_properties works as expected
        """
        property_funcs = {"test2": lambda item: item.test2 + " World"}

        items = [self.ItemTest("Item1", "Hello"), self.ItemTest("Item2", "Hello")]

        result = self.instance.parse_properties(
            items, ["test1", "test2"], property_funcs
        )

        assert result == [
            {"test1": "Item1", "test2": "Hello World"},
            {"test1": "Item2", "test2": "Hello World"},
        ]

    def test_collate_results(self):
        """
        Tests collate_results works as expected
        """
        property_funcs = {"test2": lambda item: item.test2 + " World"}

        items = [
            self.ItemTest("Item1", "Hello"),
            self.ItemTest("Item2", "Hello"),
            self.ItemTest("Item3", "Test"),
        ]

        properties_dict = self.instance.parse_properties(
            items, ["test1", "test2"], property_funcs
        )

        result = self.instance.collate_results(properties_dict, "test2", False)

        assert len(result) == 2
        assert len(result["Hello World"]) > 0
        assert "Item1" in result["Hello World"] and "Item2" in result["Hello World"]
        assert len(result["Test World"]) > 0

    def test_parse_and_output_table_with_grouping(self):
        """
        Tests parse_and_output_table works as expected when collating results
        """
        items = [
            self.ItemTest("Item1", "Hello"),
            self.ItemTest("Item2", "Hello"),
            self.ItemTest("Item3", "Test"),
        ]

        self.instance.collate_results = MagicMock()

        self.instance.parse_and_output_table(
            "test_account",
            items,
            "server",
            ["test2", "user_email"],
            "user_email",
            False,
        )

        self.mocked_connection.assert_called_with("test_account")
        self.identity_api.find_user.assert_has_calls(
            [
                mock.call("Item1", ignore_missing=True),
                mock.call("Item2", ignore_missing=True),
                mock.call("Item3", ignore_missing=True),
            ],
            any_order=True,
        )

        self.instance.collate_results.assert_called_once()

    def test_parse_and_output_table_no_grouping(self):
        """
        Tests parse_and_output_table works as expected when no collatating is required
        """
        items = [
            self.ItemTest("Item1", "Hello"),
            self.ItemTest("Item2", "Hello"),
            self.ItemTest("Item3", "Test"),
        ]

        self.instance.collate_results = MagicMock()
        self.instance.generate_table = MagicMock()

        self.instance.parse_and_output_table(
            "test_account",
            items,
            "server",
            ["test2", "user_email"],
            "",
            False,
        )

        self.instance.collate_results.assert_not_called()
        self.instance.generate_table.assert_called_once()
