from enum import Flag, auto

class Permission(Flag):
    READ  = auto()  # 1
    WRITE = auto()  # 2
    EXEC  = auto()  # 4

# Ajout de plusieurs permissions
perm = Permission.READ
print(f"Avant suppression : {perm}")

# Suppression de WRITE
perm = perm | Permission.WRITE
print(f"Après suppression de WRITE : {perm}")

# Vérification
if perm & Permission.WRITE:
    print("Écriture autorisée")
else:
    print("Écriture refusée")