import pandas as pd
from sqlalchemy import func
from database.db import get_session, engine, Base
from database.models import Empresa, Oferta, CategoriaTech, Tecnologia, OfertaTecnologia, Compatibilidad
from analytics.data.tech_registry import TECH_CATEGORIES

def init_db():
    """Crea el esquema de base de datos."""
    Base.metadata.create_all(bind=engine)

def reset_db():
    """Reinicia el esquema eliminando y recreando tablas."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def seed_tech_registry(session):
    """Sincroniza categorías y tecnologías desde el registro oficial."""
    for cat_name, techs in TECH_CATEGORIES.items():
        cat_record = session.query(CategoriaTech).filter_by(nombre=cat_name).first()
        if not cat_record:
            cat_record = CategoriaTech(nombre=cat_name)
            session.add(cat_record)
            session.commit()
        
        for t_name in techs:
            tech_record = session.query(Tecnologia).filter_by(nombre=t_name).first()
            if not tech_record:
                tech_record = Tecnologia(nombre=t_name, categoria_id=cat_record.id)
                session.add(tech_record)
        session.commit()

def save_to_db(df):
    """Persistencia de ofertas a PostgreSQL."""
    if df is None or df.empty:
        return
        
    init_db()
    session = get_session()
    try:
        seed_tech_registry(session)
        tech_map = {t.nombre: t.id for t in session.query(Tecnologia).all()}
        
        for _, row in df.iterrows():
            id_of = row.get("id_oferta")
            if not id_of or pd.isna(id_of) or session.query(Oferta).filter_by(id_oferta=id_of).first():
                continue

            emp_name = row.get("empresa")
            emp_id = None
            if emp_name and not pd.isna(emp_name):
                emp_name_clean = str(emp_name).strip()
                emp = session.query(Empresa).filter(
                    func.lower(Empresa.nombre) == emp_name_clean.lower()
                ).first()
                if not emp:
                    emp = Empresa(nombre=emp_name_clean)
                    session.add(emp)
                    session.commit()
                emp_id = emp.id

            fecha_pub = row.get("fecha_publicacion_estimada")
            fecha_ext = row.get("fecha_extraccion")
            oferta = Oferta(
                id_oferta=id_of,
                titulo=row.get("titulo"),
                enlace=row.get("enlace"),
                descripcion=row.get("descripcion"),
                fecha_publicacion_estimada=pd.to_datetime(fecha_pub) if pd.notna(fecha_pub) else None,
                fecha_extraccion=pd.to_datetime(fecha_ext) if pd.notna(fecha_ext) else None,
                experiencia_anios=row.get("experiencia_anios"),
                requiere_ingles=bool(row.get("requiere_ingles")) if pd.notna(row.get("requiere_ingles")) else False,
                keyword=row.get("keyword"),
                origen_proceso=row.get("origen_proceso"),
                empresa_id=emp_id
            )
            session.add(oferta)
            session.flush()
            
            score = row.get("compatibilidad")
            if pd.notna(score):
                session.add(Compatibilidad(oferta_id=oferta.id, score=float(score)))
                
            stack = row.get("tech_stack", [])
            if isinstance(stack, list):
                for t in stack:
                    if t in tech_map:
                        session.add(OfertaTecnologia(oferta_id=oferta.id, tecnologia_id=tech_map[t]))
                    else:
                        print(f"[WARN] Tecnologia '{t}' detectada pero NO registrada en DB. "
                              f"Verifica que este en TECH_KEYWORDS y TECH_CATEGORIES.")
            
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def update_db_scores(df):
    """Actualiza scores de compatibilidad en la base de datos (solo 1 score por oferta)."""
    if df is None or df.empty: return
    
    session = get_session()
    try:
        for _, row in df.iterrows():
            id_of = row.get("id_oferta")
            score = row.get("compatibilidad")
            if not id_of or pd.isna(score): continue
                
            oferta = session.query(Oferta).filter_by(id_oferta=id_of).first()
            if oferta:
                session.query(Compatibilidad).filter(
                    Compatibilidad.oferta_id == oferta.id
                ).delete(synchronize_session='fetch')
                session.add(Compatibilidad(oferta_id=oferta.id, score=float(score)))
        session.commit()
    finally:
        session.close()
