"""partition datachunks

Revision ID: 8c5e76b665e8
Revises: 50c56b447bba
Create Date: 2023-08-16 14:44:44.794525

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, Integer, ForeignKey, SmallInteger
from sqlalchemy.dialects.postgresql import BYTEA

# revision identifiers, used by Alembic.
revision: str = "8c5e76b665e8"
down_revision: Union[str, None] = "50c56b447bba"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create main partitioned table
    op.execute(
        """
        CREATE TABLE data_chunks_partitioned (
            id INTEGER PRIMARY KEY,
            patient_id INTEGER REFERENCES patients(id),
            seizure_state INTEGER,
            data_type SMALLINT,
            data BYTEA
        ) PARTITION BY LIST (seizure_state);
    """
    )

    # Create partitions for different seizure states
    op.execute(
        "CREATE TABLE data_chunks_partitioned_0 PARTITION OF data_chunks_partitioned FOR VALUES IN (0);"
    )
    op.execute(
        "CREATE TABLE data_chunks_partitioned_1 PARTITION OF data_chunks_partitioned FOR VALUES IN (1);"
    )
    op.execute(
        "CREATE TABLE data_chunks_partitioned_2 PARTITION OF data_chunks_partitioned FOR VALUES IN (2);"
    )

    # Migrate data from the original table to the new partitioned table
    op.execute("INSERT INTO data_chunks_partitioned SELECT * FROM data_chunks;")

    # Rename original and new tables
    op.rename_table("data_chunks", "data_chunks_old")
    op.rename_table("data_chunks_partitioned", "data_chunks")

    # Recreate indexes if necessary
    op.create_index(
        "idx_patient_seizure_data_type",
        "data_chunks",
        ["patient_id", "seizure_state", "data_type"],
    )


def downgrade():
    op.rename_table("data_chunks", "data_chunks_partitioned")
    op.rename_table("data_chunks_old", "data_chunks")

    op.drop_table("data_chunks_partitioned_0")
    op.drop_table("data_chunks_partitioned_1")
    op.drop_table("data_chunks_partitioned_2")
    op.drop_table("data_chunks_partitioned")
