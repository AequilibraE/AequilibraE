import string
from aequilibrae.project.database_connection import database_connection


class LinkType:
    """A link_type object represents a single record in the *link_types* table"""
    __alowed_characters = string.ascii_letters + '_'

    def __init__(self, data_set: dict) -> None:
        self.__original__ = {}
        for k, v in data_set.items():
            self.__dict__[k] = v
            self.__original__[k] = v

    def __setattr__(self, instance, value) -> None:
        if instance == 'link_type':
            if isinstance(value, str):
                if not len(value):
                    raise ValueError('link_type cannot be zero-length')
                for letter in value:
                    if letter not in self.__alowed_characters:
                        raise ValueError('link_type can only contain letters and "_"')
            else:
                raise ValueError('link_type must be string')
        if instance == 'link_type_id':
            raise ValueError('Changing a link_type_id is not supported. Create a new one and delete this')
        else:
            self.__dict__[instance] = value

    def delete(self):
        conn = database_connection()
        curr = conn.cursor()
        curr.execute(f'DELETE FROM link_types where link_type_id="{self.link_type_id}"')
        conn.commit()
        del self

    def save(self):
        conn = database_connection()
        curr = conn.cursor()

        curr.execute(f'select count(*) from link_types where link_type_id="{self.link_type_id}"')
        if curr.fetchone()[0] == 0:
            data = [self.link_type_id, self.link_type]
            curr.execute('Insert into link_types (link_type_id, link_type) values(?,?)', data)

        for key, value in self.__dict__.items():
            if key != 'link_type_id' and key in self.__original__:
                v_old = self.__original__.get(key, None)
                if value != v_old and value is not None:
                    self.__original__[key] = value
                    curr.execute(f"update 'link_types' set '{key}'=? where link_type_id='{self.link_type_id}'", [value])
        conn.commit()
        conn.close()
