from cx_Freeze import setup, Executable 
 
includefiles = ['EDSRSETTINGS.txt', 'README.txt']

target = Executable(
    script="EDSR.py",
    icon="EDSR.ico"
    )

setup(name = "EDSR" , 
      version = "1.0" , 
      description = "" ,
      options = {'build_exe': {'include_files':includefiles}},
      executables = [target]) 