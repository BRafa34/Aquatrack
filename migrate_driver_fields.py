#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para agregar los nuevos campos al modelo Order para el rol de conductor.
Ejecutar este script una vez para actualizar la base de datos.
"""

from app import create_app, db
from app.models import Order
from sqlalchemy import text

app = create_app()

def migrate_database():
    """Agrega los nuevos campos a la tabla orders si no existen"""
    with app.app_context():
        try:
            # Verificar si las columnas ya existen
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('orders')]
            
            print("Columnas actuales en 'orders':", columns)
            
            # Agregar driver_id si no existe
            if 'driver_id' not in columns:
                print("Agregando columna 'driver_id'...")
                db.session.execute(text("""
                    ALTER TABLE orders 
                    ADD COLUMN driver_id INTEGER REFERENCES users(id)
                """))
                print("✓ Columna 'driver_id' agregada")
            else:
                print("✓ Columna 'driver_id' ya existe")
            
            # Agregar delivered_at si no existe
            if 'delivered_at' not in columns:
                print("Agregando columna 'delivered_at'...")
                db.session.execute(text("""
                    ALTER TABLE orders 
                    ADD COLUMN delivered_at TIMESTAMP
                """))
                print("✓ Columna 'delivered_at' agregada")
            else:
                print("✓ Columna 'delivered_at' ya existe")
            
            # Agregar driver_notes si no existe
            if 'driver_notes' not in columns:
                print("Agregando columna 'driver_notes'...")
                db.session.execute(text("""
                    ALTER TABLE orders 
                    ADD COLUMN driver_notes TEXT
                """))
                print("✓ Columna 'driver_notes' agregada")
            else:
                print("✓ Columna 'driver_notes' ya existe")
            
            db.session.commit()
            print("\n✅ Migración completada exitosamente!")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error durante la migración: {e}")
            print("Si las tablas no existen, primero ejecuta: db.create_all()")
            raise

if __name__ == '__main__':
    print("Iniciando migración de base de datos...")
    print("=" * 50)
    migrate_database()
    print("=" * 50)

