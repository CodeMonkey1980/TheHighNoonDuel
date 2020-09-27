import os


from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
import gameinfo

include_files = ['resources/']
packages = ['pygame']
excludes = ['tkinter']

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
# if sys.platform == "win32":
#     base = "Win32GUI"

setup(name=gameinfo.name,
      version=gameinfo.version,
      description=gameinfo.description,
      options={"build_exe": {'packages': packages, 'excludes': excludes, 'include_files': include_files}},
      executables=[Executable("core.py", base=base, targetName='the-high-noon-duel')])
