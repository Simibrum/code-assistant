"""Code to store a copy of the code in an SQLite DB."""

from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import sessionmaker, mapped_column, Mapped, declarative_base, relationship

Base = declarative_base()

class CodeClass(Base):
    """Model for a class in a Python file."""
    __tablename__ = 'code_class'
    id: Mapped[int] = mapped_column(primary_key=True)
    class_string: Mapped[str] = mapped_column()
    class_name: Mapped[str] = mapped_column()
    file_path: Mapped[str] = mapped_column()
    doc_string: Mapped[str] = mapped_column()
    imports: Mapped[str] = mapped_column()
    timestamp_created: Mapped[str] = mapped_column()
    test_status: Mapped[str] = mapped_column()
    # Other fields as needed...

    # Relationship to functions
    functions = relationship('CodeFunction', back_populates='code_class')

    def __repr__(self):
        return f'<CodeClass({self.id}, {self.class_name})>'

class CodeFunction(Base):
    """Model for a function in a Python file."""
    __tablename__ = 'code_function'
    id: Mapped[int] = mapped_column(primary_key=True)
    function_string: Mapped[str] = mapped_column()
    function_name: Mapped[str] = mapped_column()
    doc_string: Mapped[str] = mapped_column()
    vector: Mapped[str] = mapped_column()
    test_status: Mapped[str] = mapped_column()
    imports: Mapped[str] = mapped_column()
    # Can be "function"
    code_type: Mapped[str] = mapped_column()

    # Foreign Key to class
    class_id: Mapped[int] = mapped_column(ForeignKey('code_class.id'), nullable=True)
    code_class = relationship('CodeClass', back_populates='functions')

    def __repr__(self):
        return f'<CodeFunction({self.id}, {self.function_name})>'



def setup_db(db_path='sqlite:///code.db'):
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
