.. _tables_results:

Results
=======

The **results** table exists to hold the metadata for the results stored in the
*results_database.sqlite* in the same folder as the model database.

Although those results could as be stored in the model database, it is possible
that the number of tables in the model file would grow too quickly and would
essentially clutter the *project_database.sqlite*.

This is just a matter of software design and can change in future versions of
the software, however.

There are four fields in this table, which should enough to precisely identify
the results, should the user take their time to input the description of the
data.

* table_name

The actual name of the result table in the *results_database.sqlite*

* procedure

The name of the procedure that generated this result (e.g. Traffic Assignment)

* procedure_id

Unique Alpha-numeric identifier for this procedure. This ID will be visible in
the log file and everywhere else there are references to this specific result
(e.g. in the matrix table that refers the matrices/skims generated by the same
procedure that generated this table)

* description

User-provided description for this result. If no information is provided, some of
AequilibraE's procedures will generate basic information for this field.
