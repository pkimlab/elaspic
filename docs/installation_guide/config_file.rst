.. _config_file:

Updating the configuration file
================================

Edit the ELASPIC configuration file `./config/config_file.ini`_ to match your system:
  #. Settings in the :ref:`[SEQUENCE]` section should be modified to match the location of your local BLAST and PDB databases.

  #. Settings in the :ref:`[DATABASE]` section should be modified to match the local MySQL, PostgreSQL, or SQLite database.

  #. Settings in the :ref:`[DEFAULT]` and :ref:`[MODEL]` may be left unchanged, since the default values are good enough in most cases.

.. _`./config/config_file.ini`: https://gitlab.com/kimlab/elaspic/blob/develop/tests/config_file.ini

---------------------------------------------------------------------------------------------------

Configuration options
----------------------

.. _`[DEFAULT]`:

[DEFAULT]
~~~~~~~~~

.. glossary::

  global_temp_dir
    Location for storing temporary files. It will be used only if the :envvar:`TMPDIR` environmental variable is not set. **Default = '/tmp/'**.

  temp_dir string
    A folder in the :term:`global_temp_dir` that will contain all the files that are relevant to ELASPIC. Inside this folder, every job will create its own unique subfolder. **Default = 'elaspic/'**.

  debug
    Whether or not to show detailed debugging information. If True, the logging level will be set to ``logging.DEBUG``. If False, the logging level will be set to ``logging.INFO``. **Default = True**.

  look_for_interactions
    Whether or not to compute models of protein-protein interactions. **Default = True**.

  remake_provean_supset
    Whether or not to remake the Provean supporting set if one or more sequences cannot be found in the BLAST database. **Default = False**.

  n_cores
    Number of cores to use by programs that support multithreading. **Default = 1**.

  web_server
    Whether or not the ELASPIC pipeline is being run as part of a webserver. **Default = False**.

  provean_temp_dir
    Location to store provean temporary files if working on any note other than `beagle` or `banting`.
    For internal use only. **Default = ''**.

  copy_data
    Whether or not to copy calculated data back to the archive. Set to 'False' if you are planning to copy the data yourself (e.g. from inside a PBS or SGE script). **Default = True**.


.. _`[SEQUENCE]`:

[SEQUENCE]
~~~~~~~~~~

.. glossary::

  blast_db_dir
    Location of the blast **nr** and **pdbaa** databases.

  blast_db_dir_fallback
    Place to look for blast **nr** and **pdbaa** databases if :term:`blast_db_dir` does not exist.

  matrix_type
    Substitution matrix for calculating the mutation conservation score. **Default = 'blosum80'**.

  gap_start
    Penalty for starting a gap when calculating the mutation conservation score. **Default = -16**.

  gap_extend
    Penalty for extending a gap when calculating the mutation conservation score. **Default = -4**.


.. _`[MODEL]`:

[MODEL]
~~~~~~~

.. glossary::

  modeller_runs
    Number of models that MODELLER should make before choosing the best one. Not implemented! **Default = 1**.

  foldx_water
    - ``-CRYSTAL``: use water molecules in the crystal structure to bridge two protein atoms.
    - ``-PREDICT``: predict water molecules that make 2 or more hydrogen bonds to the protein.
    - ``-COMPARE``: compare predicted water bridges with bridges observed in the crystal structure.
    - ``-IGNORE``: don't predict water molecules. **Default**.

    Source: http://foldx.crg.es/manual3.jsp.

  foldx_num_of_runs
    Number of times that FoldX should evaluate a given mutation. **Default = 1**.


.. _`[DATABASE]`:

[DATABASE]
~~~~~~~~~~~~~~

.. glossary::

  db_type
    The database that you are using. Supported databases are `MySQL`, `PostgreSQL`, and `SQLite`.

  sqlite_db_dir
    Location of the SQLite database. Required only if :term:`db_type` is `SQLite`.

  db_schema
    The name of the schema that holds all elaspic data.

  db_schema_uniprot
    The name of the database schema that holds uniprot sequences. Defaults to :term:`db_schema`.

  db_database
    The name of the database that contains :term:`db_schema` and :term:`db_schema_uniprot`.
    Required only if :term:`db_type` is `PostgreSQL`. Defaults to :term:`db_schema`.

  db_username
    The username for the database. Required only if :term:`db_type` is `MySQL` or `PostgreSQL`.

  db_password
    The password for the database. Required only if :term:`db_type` is `MySQL` or `PostgreSQL`.

  db_url
    The IP address of the database. Required only if :term:`db_type` is `MySQL` or `PostgreSQL`.

  db_port
    The listening port of the database. Required only if :term:`db_type` is `MySQL` or `PostgreSQL`.

  db_socket
    Path to the socket file, if it is not in the default location.
    Used only if :term:`db_url` is `localhost`.
    For example: ``/usr/local/mysql5/mysqld.sock`` for `MySQL` and ``/var/lib/postgresql`` for `PostgreSQL`.

  schema_version
    Database schema to use for storing and retreiving data. **Default = 'elaspic'**.

  archive_type
    - extracted: all archive files are contained in an extracted directory tree.
    - 7zip: archive is made of three compressed 7zip files (provean/provean.7z, uniprot_domain/uniprot_domain.7z, uniprot_domain_pair/uniprot_domain_pair.7z), provided on the `elaspic downloads page <http://elaspic.kimlab.org/static/download/current_release/>`_.

  archive_dir
    Location for storing and retrieving precalculated data.

  pdb_dir
    Location of all pdb structures, equivalent to the "data/data/structures/divided/pdb/" folder in the PDB ftp site. Optional.


Environmental variables
-----------------------

.. envvar:: ELASPIC_DB_STRING

    URL of the ELASPIC database in the format that can be `undrstood by SQLAlchemy <http://docs.sqlalchemy.org/en/latest/core/engines.html>`_. For example, :ref:`ELASPIC_DB_STRING` for a SQLite file ``elaspic.db`` in your home folder would look like: ``sqlite:///${HOME}/elaspic.db``.

.. envvar:: ELASPIC_ARCHIVE_DIR

    Folder where to look for and store previously calculated data. A good place for the ELASPIC archive may be ``${HOME}/elaspic``.

.. envvar:: BLAST_DB_DIR

    Location of the local mirror of the `BLAST *nr* database <ftp://ftp.ncbi.nlm.nih.gov/blast/db/>`_.

.. envvar:: PDB_DIR

    Location of the local mirror of the `wwPDB ftp repository <ftp://ftp.wwpdb.org/pub/pdb/data/>`_.

.. envvar:: TMPDIR

    Location where to create all temporary files and folders. Defaults to ``/tmp``.
