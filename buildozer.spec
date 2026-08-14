[app]

# Nome mostrado no Android
title = jmbelem Gestão

# Identificador permanente do aplicativo
package.name = jmbelemgestao
package.domain = com.jmbelem

# Pasta deste arquivo: inclui main.py, icon.png e settings.json
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,json

version = 1.0.0
orientation = all
fullscreen = 1

# Dependências usadas pelo aplicativo
requirements = python3,kivy,pyjnius

# Permissões para abrir o sistema web dentro do aplicativo
android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.api = 35
android.minapi = 23
android.ndk = 27c
android.archs = arm64-v8a,armeabi-v7a
android.allow_backup = True
android.copy_libs = 1

# Ícone do aplicativo
icon.filename = %(source.dir)s/icon.png

[buildozer]

log_level = 2
warn_on_root = 1