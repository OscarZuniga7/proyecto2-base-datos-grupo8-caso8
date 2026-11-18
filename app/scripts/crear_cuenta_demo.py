"""Aprovisionamiento explícito de un usuario demo en tablas EXISTENTES.

Ejecutar desde /app: python -m scripts.crear_cuenta_demo --usuario ...
                        --trabajador-id ... --rol Administrador|Consulta
Si el trabajador ya tiene cuenta (como ocurre con los datos sintéticos),
se exige --reutilizar-existente y confirmación interactiva.
"""
import argparse
import getpass
import sys
import bcrypt
from sqlalchemy import text
from db.connection import get_engine


def main():
    p = argparse.ArgumentParser(description="Aprovisionar cuenta demo sin contraseña en archivos")
    p.add_argument('--usuario', required=True, help='Nombre nuevo de la cuenta de demostración')
    p.add_argument('--trabajador-id', type=int, required=True, help='ID de TRABAJADOR existente')
    p.add_argument('--rol', required=True, choices=['Administrador', 'Consulta'])
    p.add_argument('--reutilizar-existente', action='store_true',
                   help='Permite sustituir una cuenta sintética preexistente de ese trabajador')
    args = p.parse_args()
    nombre = args.usuario.strip()
    if not nombre or len(nombre)>100 or args.trabajador_id<1:
        p.error('Usuario o identificador inválido')

    clave = getpass.getpass('Contraseña nueva (no se mostrará): ')
    confirmacion = getpass.getpass('Repita la contraseña: ')
    if clave != confirmacion or len(clave)<12 or len(clave.encode('utf8'))>72:
        sys.exit('Contraseñas distintas o longitud inválida (12 caracteres mínimo, 72 bytes máximo).')
    hash_seguro = bcrypt.hashpw(clave.encode('utf8'), bcrypt.gensalt(rounds=12)).decode('ascii')
    del clave, confirmacion

    with get_engine().begin() as conn:
        worker = conn.execute(text('SELECT id_trabajador,nombre FROM trabajador WHERE id_trabajador=:id'),
                              {'id':args.trabajador_id}).mappings().first()
        if worker is None:
            raise RuntimeError('El trabajador no existe. No se han efectuado cambios.')
        cuenta = conn.execute(text('SELECT id_usuario,nombre_usuario FROM usuario WHERE id_trabajador=:id FOR UPDATE'),
                              {'id':args.trabajador_id}).mappings().first()
        repetido = conn.execute(text('SELECT id_usuario FROM usuario WHERE nombre_usuario=:u'), {'u':nombre}).scalar()
        if repetido and (cuenta is None or repetido != cuenta['id_usuario']):
            raise RuntimeError('Nombre de usuario ya ocupado por otra cuenta. Sin cambios.')
        if cuenta and not args.reutilizar_existente:
            raise RuntimeError('El trabajador ya tiene usuario. Requiere --reutilizar-existente para cambios explícitos.')
        if cuenta:
            print(f"ATENCIÓN: reemplazará usuario y hash de la cuenta sintética {cuenta['nombre_usuario']} (ID {cuenta['id_usuario']}).")
            respuesta = input('Escriba REUTILIZAR para confirmar: ')
            if respuesta != 'REUTILIZAR':
                raise RuntimeError('Cancelado; se revierte la transacción.')
            usuario_id = cuenta['id_usuario']
            conn.execute(text('UPDATE usuario SET nombre_usuario=:u, clave_hash=:h WHERE id_usuario=:id'),
                         {'u':nombre,'h':hash_seguro,'id':usuario_id})
        else:
            usuario_id = conn.execute(text('INSERT INTO usuario (id_trabajador,nombre_usuario,clave_hash) VALUES (:t,:u,:h)'),
                                    {'t':args.trabajador_id,'u':nombre,'h':hash_seguro}).lastrowid
        # Crea únicamente las FILAS de rol aprobadas para la demo, no tablas nuevas.
        rol_id = conn.execute(text('SELECT id_rol FROM rol WHERE nombre=:r'), {'r':args.rol}).scalar()
        if rol_id is None:
            rol_id = conn.execute(text('INSERT INTO rol (nombre,descripcion) VALUES (:r,:d)'),
                {'r':args.rol,'d':'Rol demostrativo del PMV, sujeto a ratificación D10'}).lastrowid
        if args.rol == 'Consulta':
            # Consulta no puede contar simultáneamente con privilegio de Administrador.
            tiene_admin = conn.execute(text('''SELECT 1 FROM usuario_rol ur JOIN rol r ON r.id_rol=ur.id_rol
                       WHERE ur.id_usuario=:u AND r.nombre='Administrador' LIMIT 1'''), {'u':usuario_id}).first()
            if tiene_admin:
                raise RuntimeError('La cuenta ya tiene rol Administrador. No puede configurarse como solo consulta.')
        existe = conn.execute(text('SELECT 1 FROM usuario_rol WHERE id_usuario=:u AND id_rol=:r'),
                              {'u':usuario_id,'r':rol_id}).first()
        if not existe:
            conn.execute(text('INSERT INTO usuario_rol (id_usuario,id_rol) VALUES (:u,:r)'),
                         {'u':usuario_id,'r':rol_id})
    print(f'Cuenta de demostración configurada: {nombre} (id={usuario_id}), rol={args.rol}.')
    print('No se ha impreso ni guardado la contraseña en archivo.')


if __name__ == '__main__':
    main()
