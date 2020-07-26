from sqlite3 import IntegrityError, Connection
from aequilibrae.project.network.link_type import LinkType
from aequilibrae import logger
from aequilibrae.project.table_loader import TableLoader


class LinkTypes:
    """
    Access to the API resources to manipulate the link_types table in the network

    ::

        from aequilibrae import Project
        from aequilibrae.project.network import LinkType

        p = Project()
        p.open('path/to/project/folder')

        link_types = p.network.link_types

        # We can get a dictionary of all modes in the model
        all_link_types = modes.all_types()

        #And do a bulk change and save it
        for link_type_id, link_type_obj in all_link_types.items():
            link_type_obj.beta = 1

        # We can save changes for all link types in one go
        all_link_types.save()

        # or just get one link_type in specific
        default_link_type = link_types.get('y')

        # or just get it by name
        default_link_type = link_types.get_by_name('default')

        # We can change the description of the mode
        default_link_type.description = 'My own new description'

        # Let's say we are using alpha to store lane capacity during the night as 90% of the standard
        default_link_type.alpha =0.9 * default_link_type.lane_capacity

        # To save this mode we can simply
        default_link_type.save()

        # We can also create a completely new link_type and add to the model
        new_type = new('a')
        new_type.link_type_name = 'Arterial'  # Only ASCII letters and *_* allowed
        # other fields are not mandatory

        # We then save it to the database
        new_type.save()

        # we can even keep editing and save it directly once we have added it to the project
        new_type.lanes = 3
        new_type.lane_capacity = 1100
        new_type.save()

    """
    __items = {}

    def __init__(self, net):
        self.__all_types = []
        self.conn = net.conn  # type: Connection
        self.curr = net.conn.cursor()

        tl = TableLoader()
        link_types_list = tl.load_table(self.curr, 'link_types')
        if link_types_list:
            self.__properties = list(link_types_list[0].keys())
        for lt in link_types_list:
            if lt['link_type_id'] not in self.__items:
                self.__items[lt['link_type_id']] = LinkType(lt)

    def new(self, link_type_id: str) -> LinkType:
        if link_type_id in self.__items:
            raise ValueError('Link Type ID already exists in the model. It must be unique.')

        tp = {key: None for key in self.__properties}
        tp['link_type_id'] = link_type_id
        lt = LinkType(tp)
        self.__items[link_type_id] = lt
        logger.warning('Link type has not yet been saved to the database. Do so explicitly')
        return lt

    def drop(self, link_type_id: str) -> None:
        """Removes the link_type with **link_type_id** from the project"""
        try:
            lt = self.__items[link_type_id]  # type: LinkType
            lt.delete()
            del self.__items[link_type_id]
            self.conn.commit()
        except IntegrityError as e:
            logger.error(f'Failed to remove link_type {link_type_id}. {e.args}')
            raise e
        logger.warning(f'Link type {link_type_id} was successfully removed from the project database')

    def get(self, link_type_id: str) -> LinkType:
        """Get a link_type from the network by its **link_type_id**"""
        if link_type_id not in self.__items:
            raise ValueError(f'Link type {link_type_id} does not exist in the model')
        return self.__items[link_type_id]

    def get_by_name(self, link_type: str) -> LinkType:
        """Get a link_type from the network by its **link_type** (i.e. name)"""
        for lt in self.__items.values():
            if lt.link_type.lower() == link_type.lower():
                return lt

    def all_types(self) -> dict:
        """Returns a dictionary with all LinkType objects available in the model. link_type_id as key"""
        return self.__items

    def save(self):
        for lt in self.__items.values():  # type: LinkType
            lt.save()

    def __copy__(self):
        raise Exception('Link Types object cannot be copied')

    def __deepcopy__(self, memodict=None):
        raise Exception('Link Types object cannot be copied')

    def __del__(self):
        self.__items.clear()
