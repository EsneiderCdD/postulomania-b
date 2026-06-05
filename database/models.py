import enum
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, TIMESTAMP, ForeignKey, func, UniqueConstraint, Enum, CheckConstraint
from sqlalchemy.orm import relationship
from database.db import Base


class EstadoProceso(str, enum.Enum):
    POSTULADO = "Postulado"
    HDV_VISTA = "HdV Vista"
    FINALISTA = "Finalista"
    PROCESO_FINALIZADO = "Proceso finalizado"

class Empresa(Base):
    __tablename__ = 'empresas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255))
    website = Column(Text)
    direccion = Column(String(255))
    municipio = Column(String(255))
    departamento = Column(String(255))
    lat = Column(Float)
    lng = Column(Float)
    en_seguimiento = Column(Boolean, default=False)
    estado_visual = Column(String(25), nullable=True)
    tipo = Column(String(50), nullable=True)
    foto_url = Column(Text, nullable=True)

class Oferta(Base):
    __tablename__ = 'ofertas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_oferta = Column(String(100), unique=True, nullable=False)
    titulo = Column(String(255))
    enlace = Column(Text)
    descripcion = Column(Text)
    municipio = Column(String(255))
    departamento = Column(String(255))
    fecha_publicacion_estimada = Column(TIMESTAMP)
    fecha_extraccion = Column(TIMESTAMP)
    experiencia_anios = Column(Float)
    requiere_ingles = Column(Boolean)
    keyword = Column(String(100))
    origen_proceso = Column(String(100), nullable=False, index=True)
    empresa_id = Column(Integer, ForeignKey('empresas.id'))

    empresa = relationship('Empresa', backref='ofertas')
    tecnologias = relationship('Tecnologia', secondary='ofertas_tecnologias', backref='ofertas')
    compatibilidades = relationship('Compatibilidad', backref='oferta', cascade="all, delete-orphan")
    postulaciones = relationship('Postulacion', backref='oferta', cascade="all, delete-orphan")

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


class Postulacion(Base):
    __tablename__ = 'postulaciones'
    id = Column(Integer, primary_key=True, autoincrement=True)
    oferta_id = Column(Integer, ForeignKey('ofertas.id'), nullable=False)
    fecha_postulacion = Column(TIMESTAMP)
    plataforma = Column(String(100))
    estado_proceso = Column(String(25), nullable=False)

class Nota(Base):
    __tablename__ = 'notas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    oferta_id = Column(Integer, ForeignKey('ofertas.id', ondelete="CASCADE"), nullable=True)
    empresa_id = Column(Integer, ForeignKey('empresas.id', ondelete="CASCADE"), nullable=True)
    contenido = Column(Text, nullable=False)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "(oferta_id IS NOT NULL AND empresa_id IS NULL) OR (oferta_id IS NULL AND empresa_id IS NOT NULL)",
            name="notas_una_entidad"
        ),
    )

    oferta = relationship('Oferta', backref='notas')
    empresa = relationship('Empresa', backref='notas')