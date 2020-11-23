from sqlite3 import Connection
from copy import deepcopy
from aequilibrae.project.network.node import Node
from aequilibrae import logger
from aequilibrae.project.field_editor import FieldEditor
from aequilibrae.project.table_loader import TableLoader


class Nodes:
    """
    Access to the API resources to manipulate the links table in the network

    ::

        from aequilibrae import Project

        proj = Project()
        proj.open('path/to/project/folder')

        all_nodes = proj.network.nodes

        # We can just get one link in specific
        node = all_nodes.get(7894)

        # We can save changes for all nodes we have edited so far
        all_nodes.save()
    """
    __items = {}

    #: Query sql for retrieving nodes
    sql = ''

    def __init__(self, net):
        self.__all_nodes = []
        self.conn = net.conn  # type: Connection
        self.curr = net.conn.cursor()
        tl = TableLoader()
        tl.load_structure(self.curr, 'nodes')
        self.sql = tl.sql

        self.__fields = deepcopy(tl.fields)

    def get(self, node_id: int) -> Node:
        """Get a node from the network by its **node_id**

        It raises an error if node_id does not exist

        Args:
            *node_id* (:obj:`int`): Id of a node to retrieve

        Returns:
            *node* (:obj:`Node`): Node object for requested node_id
            """

        self.curr.execute(f'{self.sql} where link_id=?', [node_id])
        data = self.curr.fetchone()
        if data:
            data = {key: val for key, val in zip(self.__fields, data)}
            node = Node(data)
            self.__items[node.node_id] = node
            return node

        raise ValueError(f'Node {node_id} does not exist in the model')

    def save(self):
        """Saves all nodes that have been retrieved so far"""
        for node in self.__items.values():  # type: Node
            node.save()

    @staticmethod
    def fields() -> FieldEditor:
        """Returns a FieldEditor class instance to edit the Links table fields and their metadata

        Returns:
            *field_editor* (:obj:`FieldEditor`): A field editor configured for editing the Links table
            """
        return FieldEditor('nodes')

    def __copy__(self):
        raise Exception('Links object cannot be copied')

    def __deepcopy__(self, memodict=None):
        raise Exception('Links object cannot be copied')

    def __del__(self):
        self.__items.clear()