from sqlalchemy import create_engine, Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Crear el motor de la base de datos (por ejemplo, SQLite)
engine = create_engine('sqlite:///chat_history.db', connect_args={"check_same_thread": False})
Base = declarative_base()

# Crear una sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Modelo de la tabla de historial
class ChatHistory(Base):
    __tablename__ = 'chat_history'

    id = Column(Integer, primary_key=True, index=True)  # ID de la interacción
    question = Column(Text, nullable=False)  # Pregunta realizada
    answer = Column(Text, nullable=False)  # Respuesta generada

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
