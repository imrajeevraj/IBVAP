"""p2_forensics

Revision ID: 7b96ded74b21
Revises: 494432d1d9c5
Create Date: 2026-08-30 02:13:36.386378

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7b96ded74b21'
down_revision: Union[str, Sequence[str], None] = '494432d1d9c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Evidence table
    op.create_table('evidence',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('camera_id', sa.String(), nullable=False),
        sa.Column('capture_timestamp', sa.DateTime(), nullable=True),
        sa.Column('data_origin', sa.String(), nullable=False, server_default='LIVE'),
        sa.Column('integrity_hash', sa.String(), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['camera_id'], ['cameras.id'], ),
        sa.ForeignKeyConstraint(['event_id'], ['security_events.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_evidence_event_id'), 'evidence', ['event_id'], unique=False)
    op.create_index(op.f('ix_evidence_id'), 'evidence', ['id'], unique=False)
    op.create_index(op.f('ix_evidence_data_origin'), 'evidence', ['data_origin'], unique=False)

    # Plate events
    op.add_column('plate_events', sa.Column('source_frame_id', sa.String(), nullable=True))
    op.add_column('plate_events', sa.Column('raw_candidates', sa.String(), nullable=True))
    op.add_column('plate_events', sa.Column('validation_state', sa.String(), nullable=True))
    op.add_column('plate_events', sa.Column('vehicle_bbox_x1', sa.Integer(), nullable=True))
    op.add_column('plate_events', sa.Column('vehicle_bbox_y1', sa.Integer(), nullable=True))
    op.add_column('plate_events', sa.Column('vehicle_bbox_x2', sa.Integer(), nullable=True))
    op.add_column('plate_events', sa.Column('vehicle_bbox_y2', sa.Integer(), nullable=True))
    op.add_column('plate_events', sa.Column('plate_bbox_x1', sa.Integer(), nullable=True))
    op.add_column('plate_events', sa.Column('plate_bbox_y1', sa.Integer(), nullable=True))
    op.add_column('plate_events', sa.Column('plate_bbox_x2', sa.Integer(), nullable=True))
    op.add_column('plate_events', sa.Column('plate_bbox_y2', sa.Integer(), nullable=True))

    # Face events
    op.add_column('face_events', sa.Column('frame_id', sa.String(), nullable=True))
    op.add_column('face_events', sa.Column('face_quality', sa.Float(), nullable=True))
    op.add_column('face_events', sa.Column('similarity_score', sa.Float(), nullable=True))
    op.add_column('face_events', sa.Column('face_bbox_x1', sa.Integer(), nullable=True))
    op.add_column('face_events', sa.Column('face_bbox_y1', sa.Integer(), nullable=True))
    op.add_column('face_events', sa.Column('face_bbox_x2', sa.Integer(), nullable=True))
    op.add_column('face_events', sa.Column('face_bbox_y2', sa.Integer(), nullable=True))
    op.add_column('face_events', sa.Column('data_origin', sa.String(), nullable=False, server_default='LIVE'))
    op.create_index(op.f('ix_face_events_data_origin'), 'face_events', ['data_origin'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_face_events_data_origin'), table_name='face_events')
    op.drop_column('face_events', 'data_origin')
    op.drop_column('face_events', 'face_bbox_y2')
    op.drop_column('face_events', 'face_bbox_x2')
    op.drop_column('face_events', 'face_bbox_y1')
    op.drop_column('face_events', 'face_bbox_x1')
    op.drop_column('face_events', 'similarity_score')
    op.drop_column('face_events', 'face_quality')
    op.drop_column('face_events', 'frame_id')

    op.drop_column('plate_events', 'plate_bbox_y2')
    op.drop_column('plate_events', 'plate_bbox_x2')
    op.drop_column('plate_events', 'plate_bbox_y1')
    op.drop_column('plate_events', 'plate_bbox_x1')
    op.drop_column('plate_events', 'vehicle_bbox_y2')
    op.drop_column('plate_events', 'vehicle_bbox_x2')
    op.drop_column('plate_events', 'vehicle_bbox_y1')
    op.drop_column('plate_events', 'vehicle_bbox_x1')
    op.drop_column('plate_events', 'validation_state')
    op.drop_column('plate_events', 'raw_candidates')
    op.drop_column('plate_events', 'source_frame_id')

    op.drop_index(op.f('ix_evidence_data_origin'), table_name='evidence')
    op.drop_index(op.f('ix_evidence_id'), table_name='evidence')
    op.drop_index(op.f('ix_evidence_event_id'), table_name='evidence')
    op.drop_table('evidence')
