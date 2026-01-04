from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# ⚠️ IMPORTANT: URL-encoded password (# → %23)
DATABASE_URL = "postgresql://postgres:lasiPraba123%23@localhost:5432/govai"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


class GovernmentNotice(Base):
    __tablename__ = "government_notices"

    # -----------------
    # PRIMARY KEY
    # -----------------
    id = Column(Integer, primary_key=True, index=True)

    # -----------------
    # VERSIONING (STEP 3)
    # -----------------
    notice_uid = Column(String(64), index=True, nullable=False)

    version = Column(Integer, default=1, nullable=False)
    is_update = Column(Boolean, default=False, nullable=False)

    previous_notice_id = Column(
        Integer,
        ForeignKey("government_notices.id", ondelete="SET NULL"),
        nullable=True
    )
    previous_notice = relationship(
        "GovernmentNotice",
        remote_side=[id],
        uselist=False
    )

    # -----------------
    # CORE NOTICE DATA
    # -----------------
    title = Column(String(500), nullable=False)
    source = Column(String(200), nullable=False)
    source_url = Column(Text, nullable=False)

    content = Column(Text, nullable=False)
    content_hash = Column(String(64), index=True, nullable=False)

    published_date = Column(String(100), nullable=True)

    # -----------------
    # STRUCTURED DATA (STEP 4)
    # -----------------
    structured_data = Column(JSON, nullable=True)

    # -----------------
    # METADATA
    # -----------------
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


# -----------------
# CREATE TABLES
# -----------------
Base.metadata.create_all(bind=engine)
