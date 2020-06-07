-- Guarantees that the mode records have a single letter for mode_id
CREATE TRIGGER mode_single_letter_update BEFORE UPDATE OF mode_id ON "modes"
WHEN
length(new.mode_id)!= 1
BEGIN
    SELECT RAISE(ABORT, 'Mode codes need to be a single letter');
END;

#
CREATE TRIGGER mode_single_letter_insert BEFORE INSERT ON "modes"
WHEN
length(new.mode_id)!= 1
BEGIN
    SELECT RAISE(ABORT, 'Mode codes need to be a single letter');
END;

#

-- Prevents a mode record to be changed when it is in use for any link
CREATE TRIGGER mode_keep_if_in_use_updating BEFORE UPDATE OF mode_id ON "modes"
WHEN
(Select count(*) from links where instr(modes, old.mode_id) > 0)>0

BEGIN
    SELECT RAISE(ABORT, 'Mode in use on your network. Cannot change it');
END;

#
-- Prevents a mode record to be removed when it is in use for any link
CREATE TRIGGER mode_keep_if_in_use_deleting BEFORE DELETE ON "modes"
WHEN
(Select count(*) from links where instr(modes, old.mode_id) > 0)>0
BEGIN
    SELECT RAISE(ABORT, 'Mode in use on your network. Cannot change it');
END;

#
-- Ensures an ALTERED link does not reference a non existing mode
CREATE TRIGGER modes_on_links_update BEFORE UPDATE OF 'modes' ON "links"
WHEN
(select count(*) from modes where instr(new.modes, mode_id)>0)<length(new.modes)
BEGIN
    SELECT RAISE(ABORT, 'Mode codes need to exist in the modes table in order to be used');
END;

#
-- Ensures an added link does not reference a non existing mode
CREATE TRIGGER modes_on_links_insert BEFORE INSERT ON "links"
WHEN
(select count(*) from modes where instr(new.modes, mode_id)>0)<length(new.modes)
BEGIN
    SELECT RAISE(ABORT, 'Mode codes need to exist in the modes table in order to be used');
END;

#
-- Ensures an ALTERED link has at least one mode added to it
CREATE TRIGGER modes_length_on_links_update BEFORE UPDATE OF 'modes' ON "links"
WHEN
length(new.modes)<1
begin
    select RAISE(ABORT, 'Mode codes need to exist in the modes table in order to be used');
end;

#
-- Ensures an added link has at least one mode added to it
CREATE TRIGGER modes_length_on_links_insert BEFORE INSERT ON "links"
WHEN
length(new.modes)<1
BEGIN
    SELECT RAISE(ABORT, 'Mode codes need to exist in the modes table in order to be used');
END;

#
-- Keeps the list of modes at a node up-to-date when we change the links' a_node
create trigger modes_on_nodes_table_update_a_node after update of a_node on links
begin

-- We update the modes for the node ID that just received a new link ending in it
update nodes
set modes = (select GROUP_CONCAT(mode_id, '') from modes where instr((
select GROUP_CONCAT(modes, '') from links where (links.a_node = new.a_node) or (links.b_node = new.a_node))
, mode_id) > 0)
where nodes.node_id=new.a_node;

-- We update the modes for the node ID that just LOST a link ending in it
update nodes
set modes = (select GROUP_CONCAT(mode_id, '') from modes where instr((
select GROUP_CONCAT(modes, '') from links where (links.a_node = old.a_node) or (links.b_node = old.a_node))
, mode_id) > 0)
where nodes.node_id=old.a_node;
end;

#
-- Keeps the list of modes at a node up-to-date when we change the links' b_node
create trigger modes_on_nodes_table_update_b_node after update of b_node on links
begin

-- We update the modes for the node ID that just received a new link ending in it
update nodes
set modes = (select GROUP_CONCAT(mode_id, '') from modes where instr((
select GROUP_CONCAT(modes, '') from links where (links.a_node = new.b_node) or (links.b_node = new.b_node))
, mode_id) > 0)
where nodes.node_id=new.b_node;

-- We update the modes for the node ID that just LOST a link ending in it
update nodes
set modes = (select GROUP_CONCAT(mode_id, '') from modes where instr((
select GROUP_CONCAT(modes, '') from links where (links.a_node = old.b_node) or (links.b_node = old.b_node))
, mode_id) > 0)
where nodes.node_id=old.b_node;
end;

#
-- Keeps the list of modes at a node up-to-date when we change the links' mode
create trigger modes_on_nodes_table_update_links_modes after update of modes on links
begin

-- We update the modes for the node ID that just received a new link ending in it
update nodes
set modes = (select GROUP_CONCAT(mode_id, '') from modes where instr((
select GROUP_CONCAT(modes, '') from links where (links.a_node = new.b_node) or (links.b_node = new.b_node))
, mode_id) > 0)
where nodes.node_id=new.b_node;

-- We update the modes for the node ID that just received a new link ending in it
update nodes
set modes = (select GROUP_CONCAT(mode_id, '') from modes where instr((
select GROUP_CONCAT(modes, '') from links where (links.a_node = new.b_node) or (links.b_node = new.b_node))
, mode_id) > 0)
where nodes.node_id=new.a_node;

end;

#
-- Keeps the list of modes at a node up-to-date when we try to manually change the modes field in the nodes table
create trigger modes_on_nodes_table_update_nodes_modes after update of modes on nodes
begin

-- We update the modes for the node ID that just received a new link ending in it
update nodes
set modes = (select GROUP_CONCAT(mode_id, '') from modes where instr((
select GROUP_CONCAT(modes, '') from links where (links.a_node = new.node_id) or (links.b_node = new.node_id))
, mode_id) > 0)
where nodes.node_id=new.node_id;
end;

#
-- We have to have at least one mode in the database
CREATE TRIGGER mode_keep_at_least_one BEFORE DELETE ON "modes"
WHEN
(Select count(*) from modes where mode_id != old.mode_id) =0
BEGIN
    SELECT RAISE(ABORT, 'Modes table needs to have at least one mode at any time.');
END;
