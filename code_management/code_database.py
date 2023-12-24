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
from functions import logger

Base = declarative_base()


class AbstractCode(Base):
    """Abstract base class for code objects."""

    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    code_string: Mapped[str] = mapped_column()
    file_path: Mapped[str] = mapped_column(nullable=True)
    doc_string: Mapped[str] = mapped_column(nullable=True)
    test_status: Mapped[str] = mapped_column(nullable=True)
    imports: Mapped[str] = mapped_column(nullable=True)
    start_line: Mapped[int] = mapped_column(nullable=True)
    end_line: Mapped[int] = mapped_column(nullable=True)

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.id}, {self.name})>"


class CodeClass(AbstractCode):
    """Model for a class in a Python file."""

    __tablename__ = "code_class"
    # Other fields as needed...

    # Relationship to functions
    functions = relationship("CodeFunction", back_populates="code_class")


class CodeFunction(AbstractCode):
    """Model for a function in a Python file."""

    __tablename__ = "code_function"
    vector: Mapped[str] = mapped_column(nullable=True)
    # Can be "function" or "test"
    code_type: Mapped[str] = mapped_column(nullable=True)
    is_test: Mapped[bool] = mapped_column(nullable=True)
    is_function: Mapped[bool] = mapped_column(nullable=True)

    # Foreign Key to class
    class_id: Mapped[int] = mapped_column(ForeignKey("code_class.id"), nullable=True)
    code_class = relationship("CodeClass", back_populates="functions")


class CodeTest(AbstractCode):
    """Model for a test in a Python file."""

    __tablename__ = "code_test"
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

    @property
    def identifier(self):
        """Return a string identifier for the test."""
        return f"{self.file_path}::{self.name}"


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
        class_name = class_obj.name
        # Set the test name
        test_name = f"test_{class_name}_{function.name}"
    else:
        test_name = f"test_{function.name}"
    return test_name


def add_test_to_db(db_session, function, test_code, test_file_name):
    """Add a test to the database."""
    test_name = compute_test_name(db_session, function)
    class_test = True if function.class_id else False
    new_test = CodeTest(
        code_string=test_code,
        name=test_name,
        file_path=test_file_name,
        doc_string="",
        test_status="",
        function_id=function.id,
        class_id=function.class_id,
        class_test=class_test,
    )
    db_session.add(new_test)


def is_class_name_in_test_string(class_names, test_string):
    """
    Checks if any of the class names are present in the test string.

    :param class_names: A list of class names (e.g., ['GitHandler', 'MyClass'])
    :param test_string: A test string of the format 'test_[ClassName]_[function_name]'
    :return: True if any class name is in the test string, False otherwise
    """
    for class_name in class_names:
        if class_name in test_string:
            return True
    return False


def get_class_names(session: Session):
    """Get the names of the classes in the database."""
    classes = session.query(CodeClass).all()
    class_names = [c.name for c in classes]
    return class_names


def link_tests(session: Session):
    """Link tests to the functions they test."""
    class_names = get_class_names(session)
    tests = session.query(CodeTest).all()
    for test in tests:
        if test.class_test is None:
            logger.debug("Setting class_test for %s", test.name)
            test.class_test = is_class_name_in_test_string(class_names, test.name)
            session.commit()
        if not test.class_test and not test.function_id:
            function_name = test.name.replace("test_", "")
            logger.debug("Looking for function %s", function_name)
            function = session.query(CodeFunction).filter_by(name=function_name).first()
            if function is not None:
                logger.debug("Found function %s", function.name)
                test.function_id = function.id
                session.commit()
        if test.class_test and (not test.class_id or not test.function_id):
            class_name = test.name.replace("test_", "").split("_")[0]
            logger.debug("Looking for class %s", class_name)
            class_obj = session.query(CodeClass).filter_by(name=class_name).first()
            if class_obj is not None:
                logger.debug("Found class %s", class_obj.name)
                test.class_id = class_obj.id
                session.commit()
            function_name = "_".join(test.name.replace("test_", "").split("_")[1:])
            logger.debug("Looking for function %s", function_name)
            function = (
                session.query(CodeFunction)
                .filter_by(name=function_name)
                .filter_by(class_id=class_obj.id)
                .first()
            )
            if function is not None:
                logger.debug("Found function %s", function.name)
                test.function_id = function.id
                session.commit()


def reset_db(db_path: str = "sqlite:///code.db"):
    """Reset the database."""
    engine = create_engine(db_path, echo=True)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
