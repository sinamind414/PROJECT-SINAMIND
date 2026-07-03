"""026_post_likes_ratings — Tables de like et notation pour les posts société

Revision ID: 026
Revises: 025
Create Date: 2026-07-03
"""

import sqlalchemy as sa
from alembic import op

revision = "026"
down_revision = "025"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "post_likes",
        sa.Column("id", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("post_id", sa.Integer(), sa.ForeignKey("community_posts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("post_id", "user_id", name="uq_post_likes"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_post_likes_post_id", "post_likes", ["post_id"])
    op.create_index("ix_post_likes_user_id", "post_likes", ["user_id"])

    op.create_table(
        "post_ratings",
        sa.Column("id", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("post_id", sa.Integer(), sa.ForeignKey("community_posts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rating", sa.SmallInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("rating >= 1 AND rating <= 5", name="ck_post_rating_range"),
        sa.UniqueConstraint("post_id", "user_id", name="uq_post_ratings"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_post_ratings_post_id", "post_ratings", ["post_id"])
    op.create_index("ix_post_ratings_user_id", "post_ratings", ["user_id"])


def downgrade():
    op.drop_table("post_ratings")
    op.drop_table("post_likes")
