from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, ForeignKeyConstraint, PrimaryKeyConstraint
from database import Base


class MicroConcept(Base):
    __tablename__ = "micro_concepts"

    id = Column(String(50), primary_key=True)
    chapitre_id = Column(String(50), nullable=False)
    matiere = Column(String(50), nullable=False)
    nom = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    code = Column(String(64), unique=True, nullable=True)
    chapter = Column(String(32), nullable=True)
    label_fr = Column(Text, nullable=True)
    label_ar = Column(Text, nullable=True)


class ConceptPrerequisite(Base):
    __tablename__ = "concept_prerequisites"

    concept_id = Column(String(100), nullable=False)
    prerequisite_id = Column(String(100), nullable=False)
    strength = Column(Float, server_default="1.0", nullable=True)
    penalty_factor = Column(Float, server_default="0.15", nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint("concept_id", "prerequisite_id"),
    )


class QuestionConceptMapping(Base):
    __tablename__ = "question_concept_mapping"

    question_id = Column(String(100), nullable=False)
    concept_id = Column(String(100), nullable=False)
    weight = Column(Float, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("question_id", "concept_id"),
    )


class QuestionConceptMap(Base):
    __tablename__ = "question_concept_map"

    question_id = Column(String(100), nullable=False)
    micro_concept = Column(String(64), nullable=True)
    weight = Column(Float, server_default="1.0", nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("question_id", "micro_concept"),
        ForeignKeyConstraint(["micro_concept"], ["micro_concepts.code"], ondelete="CASCADE"),
    )
