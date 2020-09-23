import os


from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
include_files = ['resources/']
packages = ['pygame']
excludes = ['tkinter']

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
# if sys.platform == "win32":
#     base = "Win32GUI"

setup(name="The High Noon Duel",
      version="0.1.0",
      description="A reaction speed game set in the old old west.",
      options={"build_exe": {'packages': packages, 'excludes': excludes, 'include_files': include_files}},
      executables=[Executable("core.py", base=base, targetName='the-high-noon-duel')])
