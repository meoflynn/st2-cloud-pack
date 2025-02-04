from openstack_query.query_output import QueryOutput
from openstack_query.query_builder import QueryBuilder
from openstack_query.runners.server_runner import QueryRunner

from openstack_query.query_methods import QueryMethods
from openstack_query.query_base import QueryBase

# pylint:disable=too-few-public-methods


class QueryWrapper(QueryMethods, QueryBase):
    """
    Wrapper class - This class is a stub class which inherits from QueryMethods and QueryBase and initialises
    them appropriately
    QueryWrapper is a base class for all Query<Resource> subclasses
    """

    def __init__(self, runner: QueryRunner):
        prop_handler = self._get_prop_handler()

        self.runner = runner
        self._query_results = []

        self.output = QueryOutput(prop_handler)
        self.builder = QueryBuilder(
            prop_handler,
            self._get_client_side_handlers().to_list(),
            self._get_server_side_handler(),
        )
