from typing import List, Dict, Callable, Any

from openstack.network.v2.floating_ip import FloatingIP
from openstack_api.dataclasses import (
    NonExistentCheckParams,
    NonExistentProjectCheckParams,
    EmailQueryParams,
)

from openstack_api.openstack_connection import OpenstackConnection
from openstack_api.openstack_identity import OpenstackIdentity
from openstack_api.openstack_wrapper_base import OpenstackWrapperBase
from openstack_api.openstack_query_base import OpenstackQueryBase


class OpenstackFloatingIP(OpenstackWrapperBase, OpenstackQueryBase):
    # Lists all possible query client_side for floating.ip.list
    SEARCH_QUERY_PRESETS: List[str] = [
        "all_fips",
        "fips_older_than",
        "fips_younger_than",
        "fips_last_updated_before",
        "fips_last_updated_after",
        "fips_id_in",
        "fips_id_not_in",
        "fips_name_in",
        "fips_name_not_in",
        "fips_name_contains",
        "fips_name_not_contains",
        "fips_down",
        "fips_down_before",
    ]

    # Lists possible queries client_side that don't require a project to function
    SEARCH_QUERY_PRESETS_NO_PROJECT: List[str] = [
        "fips_older_than",
        "fips_last_updated_before",
        "fips_down",
        "fips_down_before",
    ]

    # Queries to be used for OpenstackQuery
    def _query_down(self, floating_ip: FloatingIP):
        """
        Returns whether a floating ip has down in its status
        """
        return "DOWN" in floating_ip["status"]

    def __init__(self, connection_cls=OpenstackConnection):
        OpenstackWrapperBase.__init__(self, connection_cls)
        OpenstackQueryBase.__init__(self, connection_cls)
        self._identity_api = OpenstackIdentity(self._connection_cls)

    def get_query_property_funcs(
        self, cloud_account: str
    ) -> Dict[str, Callable[[Any], Any]]:
        """
        Returns property functions for use with OpenstackQuery.parse_properties
        :param cloud_account: The associated clouds.yaml account
        """
        return {
            "project_name": lambda a: self._query_api.get_project_prop(
                cloud_account, a["project_id"], "name"
            ),
            "project_email": lambda a: self._identity_api.find_project_email(
                cloud_account, a["project_id"]
            ),
        }

    def search_all_fips(
        self, cloud_account: str, project_identifier: str, **_
    ) -> List[FloatingIP]:
        """
        Returns a list of floating ips matching a given query
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated floating ips with, can be empty for all projects
        :return: A list of all floating ips
        """
        filters = {}
        if project_identifier != "":
            # list_floating_ips can only take project ids in the filters, not names so workaround
            project = self._identity_api.find_mandatory_project(
                cloud_account=cloud_account, project_identifier=project_identifier
            )
            filters.update({"project_id": project.id})

        with self._connection_cls(cloud_account) as conn:
            return conn.list_floating_ips(filters=filters)

    def search_fips_older_than(
        self, cloud_account: str, project_identifier: str, days: int, **_
    ) -> List[FloatingIP]:
        """
        Returns a list of floating ips older than a given number of days
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated floating ips with, can be empty for all projects
        :param days: The number of days the floating ips should be older than
        :return: A list of floating ips matching the query
        """
        selected_fips = self.search_all_fips(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_fips,
            self._query_api.query_datetime_before("created_at", days),
        )

    def search_fips_younger_than(
        self, cloud_account: str, project_identifier: str, days: int, **_
    ) -> List[FloatingIP]:
        """
        Returns a list of floating ips older than a given number of days
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated floating ips with, can be empty for all projects
        :param days: The number of days the floating ips should be older than
        :return: A list of floating ips matching the query
        """
        selected_fips = self.search_all_fips(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_fips,
            self._query_api.query_datetime_after("created_at", days),
        )

    def search_fips_last_updated_before(
        self, cloud_account: str, project_identifier: str, days: int, **_
    ) -> List[FloatingIP]:
        """
        Returns a list of floating ips updated before a specified number of days in the past
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated floating ips with, can be empty for all projects
        :param days: The number of days before which the floating ips should have last been updated
        :return: A list of floating ips matching the query
        """
        selected_fips = self.search_all_fips(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_fips,
            self._query_api.query_datetime_before("updated_at", days),
        )

    def search_fips_last_updated_after(
        self, cloud_account: str, project_identifier: str, days: int, **_
    ) -> List[FloatingIP]:
        """
        Returns a list of floating ips updated after a specified number of days in the past
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated floating ips with, can be empty for all projects
        :param days: The number of days after which the floating ips should have last been updated
        :return: A list of floating ips matching the query
        """
        selected_fips = self.search_all_fips(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_fips,
            self._query_api.query_datetime_after("updated_at", days),
        )

    def search_fips_name_in(
        self, cloud_account: str, project_identifier: str, names: List[str], **_
    ) -> List[FloatingIP]:
        """
        Returns a list of floating ips with names in the list given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated floating ips with, can be empty for all projects
        :param names: List of names that should pass the query
        :return: A list of floating ips matching the query
        """
        selected_fips = self.search_all_fips(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_fips, self._query_api.query_prop_in("name", names)
        )

    def search_fips_name_not_in(
        self, cloud_account: str, project_identifier: str, names: List[str], **_
    ) -> List[FloatingIP]:
        """
        Returns a list of floating ips with names that aren't in the list given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated floating ips with, can be empty for all projects
        :param names: List of names that should not pass the query
        :return: A list of floating ips matching the query
        """
        selected_fips = self.search_all_fips(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_fips,
            self._query_api.query_prop_not_in("name", names),
        )

    def search_fips_name_contains(
        self, cloud_account: str, project_identifier: str, name_snippets: List[str], **_
    ) -> List[FloatingIP]:
        """
        Returns a list of floating ips with names containing the snippets given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated floating ips with, can be empty for all projects
        :param name_snippets: List of name snippets that should be in the floating ip names returned
        :return: A list of floating ips matching the query
        """
        selected_fips = self.search_all_fips(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_fips,
            self._query_api.query_prop_contains("name", name_snippets),
        )

    def search_fips_name_not_contains(
        self, cloud_account: str, project_identifier: str, name_snippets: List[str], **_
    ) -> List[FloatingIP]:
        """
        Returns a list of floating ips with names that don't contain the snippets given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated floating ips with, can be empty for all projects
        :param name_snippets: List of name snippets that should not be in the floating ip names returned
        :return: A list of floating ips matching the query
        """
        selected_fips = self.search_all_fips(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_fips,
            self._query_api.query_prop_not_contains("name", name_snippets),
        )

    def search_fips_id_in(
        self, cloud_account: str, project_identifier: str, ids: List[str], **_
    ) -> List[FloatingIP]:
        """
        Returns a list of floating ips with ids in the list given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated floating ips with, can be empty for all projects
        :param ids: List of ids that should pass the query
        :return: A list of floating ips matching the query
        """
        selected_fips = self.search_all_fips(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_fips, self._query_api.query_prop_in("id", ids)
        )

    def search_fips_id_not_in(
        self, cloud_account: str, project_identifier: str, ids: List[str], **_
    ) -> List[FloatingIP]:
        """
        Returns a list of floating ips with ids that aren't in the list given
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated floating ips with, can be empty for all projects
        :param ids: List of ids that should not pass the query
        :return: A list of floating ips matching the query
        """
        selected_fips = self.search_all_fips(cloud_account, project_identifier)

        return self._query_api.apply_query(
            selected_fips, self._query_api.query_prop_not_in("id", ids)
        )

    def search_fips_down(
        self, cloud_account: str, project_identifier: str, **_
    ) -> List[FloatingIP]:
        """
        Returns a list of floating ips with the status DOWN
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated floating ips with, can be empty for all projects
        :return: A list of floating ips matching the query
        """
        selected_fips = self.search_all_fips(cloud_account, project_identifier)

        return self._query_api.apply_query(selected_fips, self._query_down)

    def search_fips_down_before(
        self, cloud_account: str, project_identifier: str, days: int, **_
    ) -> List[FloatingIP]:
        """
        Returns a list of floating ips with the status DOWN
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated floating ips with, can be empty for all projects
        :param days: The number of days before which the servers should have last updated
        :return: A list of floating ips matching the query
        """
        selected_fips = self.search_all_fips(cloud_account, project_identifier)

        return self._query_api.apply_queries(
            selected_fips,
            [
                self._query_down,
                self._query_api.query_datetime_before("updated_at", days),
            ],
        )

    def find_non_existent_fips(
        self, cloud_account: str, project_identifier: str
    ) -> Dict[str, List[str]]:
        """
        Returns a dictionary containing the ids of projects along with a list of non-existent servers found within them
        :param cloud_account: The associated clouds.yaml account
        :param project_identifier: The project to get all associated servers with, can be empty for all projects
        :return: A dictionary containing the non-existent server ids and their projects
        """
        return self._query_api.find_non_existent_objects(
            cloud_account=cloud_account,
            project_identifier=project_identifier,
            check_params=NonExistentCheckParams(
                object_list_func=lambda conn, project: conn.list_floating_ips(
                    filters={
                        "project_id": project.id,
                    },
                ),
                object_get_func=lambda conn, object_id: conn.network.get_ip(object_id),
                object_id_param_name="id",
                object_project_param_name="project_id",
            ),
        )

    def find_non_existent_projects(self, cloud_account: str) -> Dict[str, List[str]]:
        """
        Returns a dictionary containing the ids of non-existent projects along with a list of floating ips that
        refer to them
        :param cloud_account: The associated clouds.yaml account
        :return: A dictionary containing the non-existent projects and a list of floating ips that refer to them
        """
        return self._query_api.find_non_existent_object_projects(
            cloud_account=cloud_account,
            check_params=NonExistentProjectCheckParams(
                object_list_func=lambda conn: conn.list_floating_ips(),
                object_id_param_name="id",
                object_project_param_name="project_id",
            ),
        )
