"""Code to store a copy of the code in an SQLite DB."""

from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.orm import (
    Mapped,
    declarative_base,
    mapped_column,
    relationship,
    sessionmaker,
)

Base = declarative_base()


class CodeClass(Base):
    """Model for a class in a Python file."""

    __tablename__ = "code_class"
    id: Mapped[int] = mapped_column(primary_key=True)
    class_string: Mapped[str] = mapped_column()
    class_name: Mapped[str] = mapped_column()
    file_path: Mapped[str] = mapped_column(nullable=True)
    doc_string: Mapped[str] = mapped_column(nullable=True)
    imports: Mapped[str] = mapped_column(nullable=True)
    test_status: Mapped[str] = mapped_column(nullable=True)
    # Other fields as needed...

    # Relationship to functions
    functions = relationship("CodeFunction", back_populates="code_class")

    def __repr__(self):
        return f"<CodeClass({self.id}, {self.class_name})>"


class CodeFunction(Base):
    """Model for a function in a Python file."""

    __tablename__ = "code_function"
    id: Mapped[int] = mapped_column(primary_key=True)
    function_string: Mapped[str] = mapped_column()
    function_name: Mapped[str] = mapped_column()
    file_path: Mapped[str] = mapped_column(nullable=True)
    doc_string: Mapped[str] = mapped_column(nullable=True)
    vector: Mapped[str] = mapped_column(nullable=True)
    test_status: Mapped[str] = mapped_column(nullable=True)
    imports: Mapped[str] = mapped_column(nullable=True)
    # Can be "function" or "test"
    code_type: Mapped[str] = mapped_column(nullable=True)
    is_test: Mapped[bool] = mapped_column(nullable=True)
    is_function: Mapped[bool] = mapped_column(nullable=True)

    # Foreign Key to class
    class_id: Mapped[int] = mapped_column(ForeignKey("code_class.id"), nullable=True)
    code_class = relationship("CodeClass", back_populates="functions")

    def __repr__(self):
        return f"<CodeFunction({self.id}, {self.function_name})>"


class CodeTest(Base):
    """Model for a test in a Python file."""

    __tablename__ = "code_test"
    id: Mapped[int] = mapped_column(primary_key=True)
    test_string: Mapped[str] = mapped_column()
    test_name: Mapped[str] = mapped_column()
    file_path: Mapped[str] = mapped_column(nullable=True)
    doc_string: Mapped[str] = mapped_column(nullable=True)
    test_status: Mapped[str] = mapped_column(
        nullable=True
    )  # e.g., "pass", "fail", etc.

    # Foreign Key to function being tested
    function_id: Mapped[int] = mapped_column(
        ForeignKey("code_function.id"), nullable=True
    )
    tested_function = relationship("CodeFunction", backref="tests")

    # Foreign Key to class being tested
    class_id: Mapped[int] = mapped_column(ForeignKey("code_class.id"), nullable=True)
    tested_class = relationship("CodeClass", backref="tests")

    def __repr__(self):
        return f"<CodeTest({self.id}, {self.test_name})>"


def setup_db(db_path: str = "sqlite:///code.db"):
    """Set up an SQLite DB with SQLAlchemy to store code as strings and classes.

    Args:
        db_path (str): The path to the SQLite DB. Defaults to 'sqlite:///code.db'.
    """
    engine = create_engine(db_path, echo=True)

    # Create tables for the CodeClass and CodeFunction models
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()
    return session
