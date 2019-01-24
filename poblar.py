#!/usr/bin/env python

import ldap3
from ldap3 import Connection, ALL
from getpass import getpass
from sys import exit

#################
### VARIABLES ###

# Shell que se le asigna a los usuarios
shell = '/bin/bash'

# Ruta absoluta del directorio que contiene los directorios personales de los usuarios. Terminado en "/"
home_dir = '/home/'

# El valor inicial para los UID que se asignan al insertar usuarios. 
uid_number = 3000

# El GID que se le asigna a los usuarios. Si no se manda al añadir el usuario da error.
gid = 2500

### VARIABLES ###
#################

# Leemos el fichero .csv de los usuarios y guardamos cada línea en una lista.
with open('usuarios.csv', 'r') as usuarios:
	usuarios = usuarios.readlines()

###################################
### Parámetros para la conexión ###
ldap_ip = 'ldap://172.22.200.116:389'
dominio_base = 'dc=gonzalonazareno,dc=org'
user_admin = 'admin' 
contraseña = getpass('Contraseña: ')
### Parámetros para la conexión ###
###################################

# No es necesario, se puede mandar solo la ip.
#server= Server(ldap_ip, get_info=ALL)

# Intenta realizar la conexión.
conn = Connection(ldap_ip, 'cn={},{}'.format(user_admin, dominio_base),contraseña)

# conn.bind() devuelve "True" si se ha establecido la conexión y "False" en caso contrario.

# Si no se establece la conexión imprime por pantalla un error de conexión.
if not conn.bind():
	print('No se ha podido conectar con ldap') 
	if conn.result['description'] == 'invalidCredentials':
		print('Credenciales no válidas.')
	# Termina el script.
	exit(0)

# Recorre la lista de usuarios
for user in usuarios:
	# Separa los valores del usuario usando como delimitador ":", y asigna cada valor a la variable correspondiente.
	user = user.split(':')
	cn = user[0]
	sn = user[1]
	mail = user[2]
	uid = user[3]
	ssh = user[4][:-1]

	#Añade el usuario.
	#conn.add('uid={},ou=People,{}'.format(uid, dominio_base),object_class = ['inetOrgPerson','posixAccount','ldapPublicKey'],attributes ={'cn': cn,'sn': sn,'mail': mail,'uid': uid,'uidNumber': str(uid_number),'gidNumber': str(gid),'homeDirectory': '{}{}'.format(home_dir,uid),'loginShell': shell,'sshPublicKey': str(ssh)})
	conn.add(
		'uid={},ou=People,{}'.format(uid, dominio_base),
		object_class = 
			[
			'inetOrgPerson',
			'posixAccount',	
			'ldapPublicKey'
			],
		attributes =
			{
			'cn': cn,
			'sn': sn,
			'mail': mail,
			'uid': uid,
			'uidNumber': str(uid_number),
			'gidNumber': str(gid),
			'homeDirectory': '{}{}'.format(home_dir,uid),
			'loginShell': shell,
			'sshPublicKey': str(ssh)
			})

	if conn.result['description'] == 'entryAlreadyExists':
		print('El usuario {} ya existe.'.format(uid))

	# Aumenta el contador para asignar un UID diferente a cada usuario.
	# Nota: No se puede usar dos veces el script con diferentes ficheros de usuarios, solaparían los UID.
	uid_number += 1

#Cierra la conexión.
conn.unbind()