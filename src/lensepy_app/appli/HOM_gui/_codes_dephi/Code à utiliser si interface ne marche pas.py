
# -*- coding: utf-8 -*-
"""

Created on Wed Feb 12 15:48:20 2025

*************************************************

@author: Le Lay Noé et Duboeuf Jeanne
Written thanks to the work of Villemejane Julien : https://lense.institutoptique.fr/mine/python-pyserial-premier-script/

*************************************************

Le but de ce programme est de créer un lien entre python et
la carte Nucléo G431KB (en langage C++) pour pouvoir transférer
à la carte Nucléo une valeur T_int de temps d'intégration.

*************************************************

 *  Tested with G431KB / Mbed OS 6

 *************************************************

 *  Solec / https://solecgroup.wordpress.com/
 *  ProTIS / https://lense.institutoptique.fr/

"""

# Avant de lancer le programme, il faut mettre 'pip install pyserial' dans la console et pylab et il faut ouvrir une fenêtre 'Pylab'

import serial
import serial.tools.list_ports
import struct
import time

serial_port = serial.tools.list_ports.comports()  # L’objet serial_port est alors une liste contenant tous les objets de type port de communication série de votre machine


for port in serial_port:
    # Cela affiche chaque élément de la liste serial_port, c'est à dire tous les ports de communication série de l'ordinateur
    print(f"{port.name} // {port.device} // D={port.description}")

ser = serial.Serial("COM7",
                    baudrate=9600)  # Cela permet d'ouvrir une connexion avec le port série "COM70" -> Vérifier que la Nucléo se trouve bien sur le COM70
# "COM7" : port – obligatoire pour spécifier la nom du port auquel se connecter
# baudrate=9600 : baudrate (int) – la vitesse de transfert des données

"""
Il est indispensable de libérer le port série une fois que vous avez fini 
de l’utiliser. La commande pour le faire est la suivante : ser.close()
"""

print(ser)  # Cela permet d'avoir le nom du port, la vitesse de transfert, la parité, etc...

# Cela crée une chaîne de caractères (seulement un octet est envoyé à la fois)
T_int = 500
byt_val = T_int.to_bytes(2, 'big')
print(byt_val)
ser.write(byt_val)

# %%

"""
*************************************************
Le programme qui suit permet de lire des sonnées envoyées par la carte Nucléo

Remarque :
    - Les données sont envoyées sur 3 octets
    - Il faut s'assurer qu'il n'y a pas de printf dans le programme C++ de la Nucléo
*************************************************
"""
ser.flushInput()


# Fonction pour lire les compteurs envoyés par le Nucleo
def read_counters():
    # Lire 18 octets (3 octets par compteur)
    data = ser.read(18)
    if len(data) == 18:
        # Convertir les 18 octets reçus en 6 compteurs (3 octets pour chaque compteur)
        counter_A = struct.unpack('>I', b'\x00' + data[0:3])[0]  # Utilise '>I' pour un entier Big Endian
        counter_AB = struct.unpack('>I', b'\x00' + data[3:6])[0]
        counter_AC = struct.unpack('>I', b'\x00' + data[6:9])[0]
        counter_ABC = struct.unpack('>I', b'\x00' + data[9:12])[0]
        counter_B = struct.unpack('>I', b'\x00' + data[12:15])[0]
        counter_C = struct.unpack('>I', b'\x00' + data[15:18])[0]

        return counter_A, counter_AB, counter_AC, counter_ABC, counter_B, counter_C
    else:
        print("Erreur de lecture des données")
        return None, None, None, None

# Boucle principale
while True:
    try:
        counter_A, counter_AB, counter_AC, counter_ABC, counter_B, counter_C = read_counters()
        if counter_A is not None:
            # Afficher les résultats
            print("----------------------------")
            print(f"Counter A: {counter_A}")
            print(f"Counter AB: {counter_AB}")
            print(f"Counter AC: {counter_AC}")
            print(f"Counter ABC: {counter_ABC}")
            print(f"Counter B: {counter_B}")
            print(f"Counter C: {counter_C}")

        # Attendre un peu avant de lire à nouveau les données
        time.sleep(1)

    except KeyboardInterrupt:
        ser.close()
        print("Fin du programme.")
        break

# Ne pas oublier de mettre ser.close() dans la console pour fermer le port avant de relancer le code
