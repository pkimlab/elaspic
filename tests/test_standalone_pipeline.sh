#!/bin/bash

set -ev

# Sanity checks
if [[ -z ${TEST_DIR} || \
      -z ${PDB_DIR} || \
      -z ${BLAST_DB_DIR} || \
      -z ${TEST_NUMBER} ]] ; then
    echo 'Required environment variable not set!'
    exit -1
fi

# Run tests
CONFIG_FILE="${TEST_DIR}/$(basename ${0%%.sh}).ini"
ARCHIVE_DIR="${TEST_DIR}/archive"
mkdir -p "${ARCHIVE_DIR}"

# Update the configuration file
cp -f "${TEST_DIR}/standalone_pipeline.ini" "${CONFIG_FILE}"
sed -i "s|^pdb_dir = .*|pdb_dir = ${PDB_DIR}|" "${CONFIG_FILE}"
sed -i "s|^blast_db_dir = .*|blast_db_dir = ${BLAST_DB_DIR}|" "${CONFIG_FILE}"
sed -i "s|^archive_dir = .*|archive_dir = ${ARCHIVE_DIR}|" "${CONFIG_FILE}"
sed -i "s|^archive_type = .*|archive_type = directory|" "${CONFIG_FILE}"

# Run tests
py.test "${TEST_DIR}/test_standalone_pipeline.py" -vsx --cache-clear --cov=elaspic \
    --config-file="${CONFIG_FILE}"
