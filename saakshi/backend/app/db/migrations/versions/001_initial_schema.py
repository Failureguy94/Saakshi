"""Initial forensic schema for cases and evidence images

Revision ID: 001_initial_schema
Revises: None
Create Date: 2026-10-01 22:30:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cases",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("case_number", sa.String(length=64), nullable=False, unique=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("investigator_name", sa.String(length=128), nullable=False),
        sa.Column("agency", sa.String(length=128), nullable=False, server_default="Forensic Science Laboratory"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f("ix_cases_case_number"), "cases", ["case_number"], unique=True)

    op.create_table(
        "evidence_images",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("case_id", sa.String(length=36), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("source_path", sa.String(length=1024), nullable=False),
        sa.Column("format", sa.String(length=32), nullable=False, server_default="RAW_DD"),
        sa.Column("size_bytes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("md5_hash", sa.String(length=32), nullable=False),
        sa.Column("sha256_hash", sa.String(length=64), nullable=False),
        sa.Column("acquired_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f("ix_evidence_images_case_id"), "evidence_images", ["case_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_evidence_images_case_id"), table_name="evidence_images")
    op.drop_table("evidence_images")
    op.drop_index(op.f("ix_cases_case_number"), table_name="cases")
    op.drop_table("cases")
