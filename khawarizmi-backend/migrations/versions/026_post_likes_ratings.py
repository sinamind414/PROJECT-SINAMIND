"""026_post_likes_ratings — Tables sociales manquantes + like et notation

AJOUTÉ : community_posts, conversations, conversation_members, messages, comments
         qui manquaient dans toutes les migrations précédentes (bug historique).
Tables ajoutées : post_likes, post_ratings

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
    # --- 1. Tables sociales manquantes (jamais créées par Alembic auparavant) ---
    op.create_table(
        "community_posts",
        sa.Column("id", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("file_url", sa.String(), nullable=True),
        sa.Column("chapter_id", sa.String(), nullable=True),
        sa.Column("votes", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_community_posts_author", "community_posts", ["author_id"])

    op.create_table(
        "conversations",
        sa.Column("id", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("is_group", sa.Integer(), server_default=sa.text("0"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "conversation_members",
        sa.Column("conversation_id", sa.Integer(), sa.ForeignKey("conversations.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.PrimaryKeyConstraint("conversation_id", "user_id"),
    )

    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("conversation_id", sa.Integer(), sa.ForeignKey("conversations.id"), nullable=False),
        sa.Column("sender_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("file_url", sa.String(), nullable=True),
        sa.Column("file_type", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_messages_conversation", "messages", ["conversation_id"])
    op.create_index("ix_messages_sender", "messages", ["sender_id"])

    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("post_id", sa.Integer(), sa.ForeignKey("community_posts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_comments_post", "comments", ["post_id"])
    op.create_index("ix_comments_author", "comments", ["author_id"])

    # --- 2. post_likes ---
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

    # --- 3. post_ratings ---
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
    op.drop_table("comments")
    op.drop_table("messages")
    op.drop_table("conversation_members")
    op.drop_table("conversations")
    op.drop_table("community_posts")
