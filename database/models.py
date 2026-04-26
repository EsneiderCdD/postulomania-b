from sqlalchemy import Column, Integer, String, Text, Float, Boolean, TIMESTAMP, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import relationship
from database.db import Base

class Empresa(Base):
    __tablename__ = 'empresas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255))

class Oferta(Base):
    __tablename__ = 'ofertas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_oferta = Column(String(100), unique=True, nullable=False)
    titulo = Column(String(255))
    enlace = Column(Text)
    descripcion = Column(Text)
    fecha_publicacion_estimada = Column(TIMESTAMP)
    experiencia_anios = Column(Float)
    requiere_ingles = Column(Boolean)
    keyword = Column(String(100))
    origen_proceso = Column(String(100))
    empresa_id = Column(Integer, ForeignKey('empresas.id'))

    empresa = relationship('Empresa', backref='ofertas')
    tecnologias = relationship('Tecnologia', secondary='ofertas_tecnologias', backref='ofertas')
    compatibilidades = relationship('Compatibilidad', backref='oferta', cascade="all, delete-orphan")

class CategoriaTech(Base):
    __tablename__ = 'categorias_tech'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)

class Tecnologia(Base):
    __tablename__ = 'tecnologias'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), unique=True, nullable=False)
    categoria_id = Column(Integer, ForeignKey('categorias_tech.id'))
    
    categoria = relationship('CategoriaTech', backref='tecnologias')

class OfertaTecnologia(Base):
    __tablename__ = 'ofertas_tecnologias'
    oferta_id = Column(Integer, ForeignKey('ofertas.id', ondelete="CASCADE"), primary_key=True)
    tecnologia_id = Column(Integer, ForeignKey('tecnologias.id', ondelete="CASCADE"), primary_key=True)

class Compatibilidad(Base):
    __tablename__ = 'compatibilidades'
    id = Column(Integer, primary_key=True, autoincrement=True)
    oferta_id = Column(Integer, ForeignKey('ofertas.id', ondelete="CASCADE"))
    score = Column(Float)
    fecha_calculo = Column(TIMESTAMP, server_default=func.now())
