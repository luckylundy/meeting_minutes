import os
import sys

# 現在のディレクトリとPythonパスを表示
print("Current Directory:", os.getcwd())
print("\nPython Path:")
for p in sys.path:
    print(p)

print("\nTrying to import app:")
try:
    import app
    print("app module location:", app.__file__)
    
    print("\nTrying to import app.main:")
    import app.main
    print("app.main module location:", app.main.__file__)
except Exception as e:
    print("Error:", str(e))

# ディレクトリの内容を確認
print("\nContents of current directory:")
print(os.listdir('.'))

print("\nContents of app directory:")
print(os.listdir('./app'))
