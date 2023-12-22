"""Code to store a copy of the code in an SQLite DB."""

from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.orm import (
    Mapped,
    declarative_base,
    mapped_column,
    relationship,
    sessionmaker,
    Session,
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
    # Does the test relate to a class method
    class_test: Mapped[bool] = mapped_column(nullable=True)

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

    @property
    def identifier(self):
        """Return a string identifier for the test."""
        return f"{self.file_path}::{self.test_name}"


def setup_db(db_path: str = "sqlite:///code.db"):
    """Set up an SQLite DB with SQLAlchemy to store code as strings and classes.

    Args:
        db_path (str): The path to the SQLite DB. Defaults to 'sqlite:///code.db'.
    """
    engine = create_engine(db_path, echo=True)

    # Create tables for the CodeClass and CodeFunction models
    Base.metadata.create_all(engine)

    session_maker = sessionmaker(bind=engine)
    session = session_maker()
    return session


def compute_test_name(db_session, function):
    """Compute the name of the test for a function."""
    # Check whether function is part of a class
    if function.class_id:
        # Get the class name
        class_obj = db_session.query(CodeClass).filter_by(id=function.class_id).first()
        class_name = class_obj.class_name
        # Set the test name
        test_name = f"test_{class_name}_{function.function_name}"
    else:
        test_name = f"test_{function.function_name}"
    return test_name


def add_test_to_db(db_session, function, test_code, test_file_name):
    """Add a test to the database."""
    test_name = compute_test_name(db_session, function)
    class_test = True if function.class_id else False
    new_test = CodeTest(
        test_string=test_code,
        test_name=test_name,
        file_path=test_file_name,
        doc_string="",
        test_status="",
        function_id=function.id,
        class_id=function.class_id,
        class_test=class_test,
    )
    db_session.add(new_test)


def link_tests(session: Session):
    """Link tests to the functions they test."""
    tests = session.query(CodeTest).all()
    for test in tests:
        if not test.class_test and not test.function_id:
            function_name = test.test_name.replace("test_", "")
            function = (
                session.query(CodeFunction)
                .filter_by(function_name=function_name)
                .first()
            )
            if function is not None:
                test.function_id = function.id
                session.commit()
        if test.class_test and (not test.class_id or not test.function_id):
            class_name = test.test_name.replace("test_", "").split("_")[0]
            class_obj = (
                session.query(CodeClass).filter_by(class_name=class_name).first()
            )
            if class_obj is not None:
                test.class_id = class_obj.id
                session.commit()
            function_name = test.test_name.replace("test_", "").split("_")[1]
            function = (
                session.query(CodeFunction)
                .filter_by(function_name=function_name)
                .first()
            )
            if function is not None:
                test.function_id = function.id
                session.commit()


def reset_db(db_path: str = "sqlite:///code.db"):
    """Reset the database."""
    engine = create_engine(db_path, echo=True)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
