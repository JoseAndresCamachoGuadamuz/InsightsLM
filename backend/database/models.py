from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sources = relationship("Source", back_populates="project")

class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    file_path = Column(String, unique=True, nullable=False)
    url = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    project = relationship("Project", back_populates="sources")
    transcription = relationship("Transcription", back_populates="source", uselist=False)

class Transcription(Base):
    __tablename__ = "transcriptions"
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    full_text = Column(Text, nullable=False)
    language = Column(String, nullable=True)
    source = relationship("Source", back_populates="transcription")

class Template(Base):
    __tablename__ = "templates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    prompt_text = Column(Text, nullable=False)
    language = Column(String, nullable=False, server_default="English")
    created_at = Column(DateTime(timezone=True), server_default=func.now())