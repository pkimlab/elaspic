import argparse
import json
import logging
import logging.config
import os
import os.path as op
from textwrap import dedent

import pandas as pd

from elaspic import CACHE_DIR, DATA_DIR, conf, elaspic_predictor

logger = logging.getLogger(__name__)

LOGGING_LEVELS = {
    None: "ERROR",
    0: "ERROR",
    1: "WARNING",  # -v
    2: "INFO",  # -vv
    3: "DEBUG",  # -vvv
}

# #################################################################################################
# ELASPIC RUN


def elaspic_cli(args):
    validate_args(args)

    # Read configurations
    if args.config_file is not None:
        conf.read_configuration_file(args.config_file)
    elif args.uniprot_id:
        conf.read_configuration_file(
            DATABASE={
                "connection_string": args.connection_string,
            },
            EXTERNAL_DIRS={
                "pdb_dir": args.pdb_dir,
                "blast_db_dir": args.blast_db_dir,
                "archive_dir": args.archive_dir,
            },
            LOGGER={
                "level": LOGGING_LEVELS[args.verbose],
            },
        )
    elif args.structure_file:
        unique_temp_dir = op.abspath(op.join(os.getcwd(), ".elaspic"))
        os.makedirs(unique_temp_dir, exist_ok=True)
        conf.read_configuration_file(
            DEFAULT={"unique_temp_dir": unique_temp_dir},
            EXTERNAL_DIRS={
                "pdb_dir": args.pdb_dir,
                "blast_db_dir": args.blast_db_dir,
                "archive_dir": args.archive_dir,
            },
            LOGGER={
                "level": LOGGING_LEVELS[args.verbose],
            },
        )

    if args.uniprot_id:
        # Run database pipeline
        if args.uniprot_domain_pair_ids:
            logger.debug("uniprot_domain_pair_ids: {}".format(args.uniprot_domain_pair_ids))
            uniprot_domain_pair_ids_asint = [
                int(x) for x in args.uniprot_domain_pair_ids.split(",") if x
            ]
        else:
            uniprot_domain_pair_ids_asint = []
        # Run database pipeline
        from elaspic import database_pipeline

        pipeline = database_pipeline.DatabasePipeline(
            args.uniprot_id,
            args.mutations,
            run_type=args.run_type,
            uniprot_domain_pair_ids=uniprot_domain_pair_ids_asint,
        )
        pipeline.run()
    elif args.structure_file:
        # Run local pipeline
        from elaspic import standalone_pipeline

        pipeline = standalone_pipeline.StandalonePipeline(
            args.structure_file,
            args.sequence_file,
            args.mutations,
            mutation_format=args.mutation_format,
            run_type=args.run_type,
        )
        pipeline.run()


def validate_args(args):
    if args.config_file and not os.path.isfile(args.config_file):
        raise Exception("The configuration file {} does not exist!".format(args.config_file))

    if (args.uniprot_id is None and args.structure_file is None) or (
        args.uniprot_id is not None and args.structure_file is not None
    ):
        raise Exception(
            dedent(
                """\
            One of '-u' ('--uniprot_id') or '-p' ('--structure_file') must be specified!"""
            )
        )

    if args.uniprot_id and (
        (args.config_file is None) and (args.blast_db_dir is None or args.archive_dir is None)
    ):
        raise Exception(
            dedent(
                """\
            When using the database pipeline, \
            you must either provide a configuration file ('-c', '--config_file') or \
            '--blast_db_dir' and '--archive_dir'."""
            )
        )

    if args.sequence_file and not args.structure_file:
        raise Exception(
            dedent(
                """\
            A template PDB file must be specified using the '--structure_file' option, \
            when you specify a target sequence using the '--sequence_file' option!"""
            )
        )


def configure_run_parser(sub_parsers):
    help = "Run ELASPIC"
    description = help + dedent(
        """\


        examples:
        $ elaspic run -p 4DKL.pdb -m A_M6A -n 1 \\
            --blast_db_dir=/path/to/blast/database/

        $ elaspic run -u P00044 -m M1A -c config_file.ini

        $ elaspic run -u P00044 -m M1A \\
            --connection_string=mysql://user:pass@localhost/elaspic \\
            --pdb_dir=/home/pdb/data/data/structures/divided/pdb \\
            --blast_db_dir=/home/ncbi/blast/db \\
            --archive_dir=/home/elaspic
    """
    )
    parser = sub_parsers.add_parser(
        "run",
        help=help,
        description=description,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-c", "--config_file", nargs="?", type=str, help="ELASPIC configuration file."
    )
    parser.add_argument(
        "--connection_string",
        nargs="?",
        type=str,
        default=os.getenv("ELASPIC_DB_STRING"),
        help=dedent(
            """\
            SQLAlchemy formatted string describing the connection to the
            database. Can also be specified using the 'ELASPIC_DB_STRING'
            environment variable.
        """
        ),
    )
    parser.add_argument(
        "--archive_dir",
        nargs="?",
        type=str,
        default=os.getenv("ELASPIC_ARCHIVE_DIR"),
        help=dedent(
            """\
            Folder containing precalculated ELASPIC data. Can also be specified
            using the 'ELASPIC_ARCHIVE_DIR' environment variable.
        """
        ),
    )
    parser.add_argument(
        "--blast_db_dir",
        nargs="?",
        type=str,
        default=os.getenv("BLAST_DB_DIR"),
        help=dedent(
            """\
            Folder containing NCBI `nr` and `pdbaa` databases. Can also be
            specified using the 'BLAST_DB_DIR' environment variable.
        """
        ),
    )
    parser.add_argument(
        "--pdb_dir",
        nargs="?",
        type=str,
        default=os.getenv("PDB_DIR"),
        help=dedent(
            """\
            Folder containing PDB files in split format (e.g.
            'ab/pdb1ab2.ent.gz'). Can also be specified using the 'PDB_DIR'
            environment variable. If this is not specified, ELASPIC will
            automatically download structures from the RCSB website.
        """
        ),
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        help="Increase verbosity level. Can be specified multiple times.",
    )
    parser.add_argument(
        "-u",
        "--uniprot_id",
        help=dedent(
            """\
            The Uniprot ID of the protein that you want to mutate (e.g.
            'P28223'). This option relies on a local elaspic database, which
            has to be specified in the configuration file.
        """
        ),
    )
    parser.add_argument(
        "-p",
        "--structure_file",
        help=dedent(
            """\
            Full filename (including path) of the PDB file that you wish to
            mutate.
        """
        ),
    )
    parser.add_argument(
        "-s",
        "--sequence_file",
        help=dedent(
            """\
            Full filename (including path) of the FASTA file containing the
            sequence that you wish to model. If you choose this option, you
            also have to specify a template PDB file using the '--pdb-file'
            option.
        """
        ),
    )
    parser.add_argument(
        "-m",
        "--mutations",
        nargs="?",
        default=[""],
        help=dedent(
            """\
            Mutation(s) that you wish to evaluate.

            If you used '--uniprot_id', mutations must be provided using
            uniprot coordinates (e.g. 'D172E,R173H' or 'A_V10I').

            If you used '--structure_file', mutations must be provided using
            the chain and residue id (e.g. 'A_M1C,B_C20P' to mutate a residue
            with id '1' on chain A to Cysteine, and residue with id '20' on
            chain B to Proline).

            If you used '--sequence_file', mutations must be provided using
            the chain and residue INDEX (e.g. '1_M1C,2_C20P' to mutate the
            first residue in sequence 1 to Cysteine, and the 20th residue in
            sequence 2 to Proline).
        """
        ),
    )
    parser.add_argument(
        "-n",
        "--mutation_format",
        nargs="?",
        default=None,
        help=dedent(
            """\
            Mutation format:
            1:  {pdb_chain}_{pdb_mutation}
            2:  {pdb_chain}_{sequence_mutation}
            3:  {sequence_pos}_{sequence_mutation} (default)

            If `sequence_file` is None, this does not matter
            (always {pdb_chain}_{pdb_mutation}).
        """
        ),
    )
    parser.add_argument(
        "-i",
        "--uniprot_domain_pair_ids",
        nargs="?",
        default="",
        help=dedent(
            """\
            List of uniprot_domain_pair_ids to analyse (useful if you want to
            restrict your analysis to only a handful of domains).
        """
        ),
    )
    parser.add_argument(
        "-t",
        "--run_type",
        nargs="?",
        type=str,
        default="all",
        help=dedent(
            """\
            Type of analysis to perform. Must be one of:
            1 | sequence:
                Precalculate Provean supporting sets.
            2 | model:
                Precalculate homology models.
            3 | mutation:
                Calculate mutations (assumes Provean supporting sets and
                homology models have been calculated previously)
            4 | model.mutation:
                Calculate homolgy model and evaluate mutation(s) (assumes
                Provean supporting set has been calculated previously).
            5 | all | sequence.model.mutation:
                Calculate Provean supporting sets and homology models and
                evaluate mutations.
            6 | sequence.model:
                Precalculate Provean supporting sets and homology models.
            """
        ),
    )

    parser.set_defaults(func=elaspic_cli)


# #################################################################################################
# ELASPIC DATABASE


def elaspic_database_cli(args):
    if args.config_file:
        conf.read_configuration_file(args.config_file)
    elif args.connection_string:
        conf.read_configuration_file(
            DATABASE={"connection_string": args.connection_string},
            LOGGER={"level": LOGGING_LEVELS[args.verbose]},
        )
    else:
        raise Exception("Either 'config_file' or 'connection_string' must be specified!")

    tables_basic = [
        "domain",
        "domain_contact",
        "uniprot_sequence",
        "provean",
        "uniprot_domain",
        "uniprot_domain_template",
        "uniprot_domain_pair",
        "uniprot_domain_pair_template",
    ]
    tables_complete = [
        "domain",
        "domain_contact",
        "uniprot_sequence",
        "provean",
        "uniprot_domain",
        "uniprot_domain_template",
        "uniprot_domain_pair",
        "uniprot_domain_pair_template",
        "uniprot_domain_model",
        "uniprot_domain_pair_model",
    ]

    if args.action == "create":
        create_database(args)
    elif args.action == "load_basic":
        load_data_to_database(args, tables_basic)
    elif args.action == "load_complete":
        load_data_to_database(args, tables_complete)
    elif args.action == "delete":
        delete_database(args)
    else:
        raise Exception("Unsupported action: {}".format(args.action))


def create_database(args):
    from elaspic import elaspic_database

    db = elaspic_database.MyDatabase()
    db.create_database_tables(drop_schema=True)
    logger.info("Done!")


def load_data_to_database(args, tables):
    if not args.url:
        raise Exception("URL argument was not provided; don't know where to load the data from!")
    from elaspic import elaspic_database

    db = elaspic_database.MyDatabase()

    for table_name in tables:
        load_table_to_database(table_name, args.url, db.engine)

    # # This code tries to load tables faster by directly reading from CSVs
    # args.data_folder = args.data_folder.rstrip('/')
    # table_names = args.data_files.split(',') if args.data_files else None
    # dirpath, dirnames, filenames = next(os.walk(args.data_folder))
    # for table in elaspic_database.Base.metadata.sorted_tables:
    #     if table_names is not None and table.name not in table_names:
    #         logger.warning(
    #             "Skipping table '{}' because it was not included in the 'table_names' list..."
    #             .format(table.name))
    #         continue
    #     if '{}.tsv'.format(table.name) in filenames:
    #         db.copy_table_to_db(table.name, args.data_folder)
    #         logger.info("Successfully loaded data from file '{}' to table '{}'"
    #                     .format('{}.tsv'.format(table.name), table.name))
    #     elif '{}.tsv.gz'.format(table.name) in filenames:
    #         with decompress(os.path.join(args.data_folder, '{}.tsv.gz'.format(table.name))):
    #             db.copy_table_to_db(table.name, args.data_folder.rstrip('/'))
    #         logger.info("Successfully loaded data from file '{}' to table '{}'"
    #                     .format('{}.tsv.gz'.format(table.name), table.name))


def load_table_to_database(table_name, table_url, engine):
    logger.info("Loading table {} from {} into database...".format(table_name, table_url))
    engine.execute("DELETE FROM {}".format(table_name))
    df_header = pd.read_sql_query("select * from {} limit 0".format(table_name), engine)
    csv_file = op.join(table_url, table_name + ".tsv.gz")
    for chunk in pd.read_csv(
        csv_file, chunksize=100000, na_values=["\\N"], names=df_header.columns
    ):
        chunk.to_sql(table_name, engine, if_exists="append", index=False)


def delete_database(args):
    from elaspic import elaspic_database

    db = elaspic_database.MyDatabase()
    if db.engine == "sqlite":
        os.remove(db.engine.database)
    else:
        db.delete_database_tables(drop_schema=True, drop_uniprot_sequence=True)
    logger.info("Done!")


def configure_database_parser(sub_parsers):
    help = "Perform database maintenance tasks"
    description = help + "\n"
    example = dedent(
        """\
    Examples:

        elaspic database -c config_file.ini create

    """
    )
    parser = sub_parsers.add_parser("database", help=help, description=description, epilog=example)
    parser.add_argument(
        "-c", "--config_file", nargs="?", type=str, help="ELASPIC configuration file."
    )
    parser.add_argument(
        "--connection_string",
        nargs="?",
        type=str,
        default=os.getenv("ELASPIC_DB_STRING"),
        help=dedent(
            """\
            SQLAlchemy formatted string describing the connection to the
            database. Can also be specified using the 'ELASPIC_DB_STRING'
            environment variable.
        """
        ),
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        help="Increase verbosity level. Can be specified multiple times.",
    )
    parser.add_argument(
        "action",
        choices=["create", "load_basic", "load_complete", "delete"],
        help="Action to perform",
    )
    parser.add_argument("url", nargs="?", help="URL (or file path) from which to load data.")
    parser.set_defaults(func=elaspic_database_cli)


# #################################################################################################
# ELASPIC TRAIN


def elaspic_train(args):
    # Core predictor
    core_training_set = pd.read_csv(op.join(DATA_DIR, "core_training_set.tsv.gz"), sep="\t")
    with open(op.join(DATA_DIR, "core_options.json"), "rt") as ifh:
        core_options = json.load(ifh)

    core_predictor = elaspic_predictor.CorePredictor()
    core_predictor.train(df=core_training_set, options=core_options)
    core_predictor.save(data_dir=CACHE_DIR)

    # Interface predictor

    interface_training_set = pd.read_csv(
        op.join(DATA_DIR, "interface_training_set.tsv.gz"), sep="\t"
    )
    with open(op.join(DATA_DIR, "interface_options.json")) as ifh:
        interface_options = json.load(ifh)

    interface_predictor = elaspic_predictor.InterfacePredictor()
    interface_predictor.train(df=interface_training_set, options=interface_options)
    interface_predictor.save(data_dir=CACHE_DIR)


def configure_train_parser(sub_parsers):
    help = "Train the ELASPIC classifiers"
    description = help + "\n"
    example = dedent(
        """\

    Examples:

        elaspic train

    """
    )
    parser = sub_parsers.add_parser(
        "train",
        help=help,
        description=description,
        epilog=example,
    )
    parser.set_defaults(func=elaspic_train)


# #################################################################################################
# MAIN


def main():
    parser = argparse.ArgumentParser(
        prog="elaspic",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    sub_parsers = parser.add_subparsers(title="command", help="")
    configure_run_parser(sub_parsers)
    configure_database_parser(sub_parsers)
    configure_train_parser(sub_parsers)
    args = parser.parse_args()
    if "func" not in args.__dict__:
        args = parser.parse_args(["--help"])
    args.func(args)


if __name__ == "__main__":
    import sys

    sys.exit(main())
