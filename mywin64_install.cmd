
@set CONDA_BIN=~/miniconda3

@set CONDA_EXE=%CONDA_BIN%/Scripts/conda.exe
@set ENV_FILE=setup/environment-win64.yml

@set FirstTime=0

@rem first time
@rem %CONDA_EXE% env create -f %ENV_FILE%

@rem not first time
@%CONDA_EXE% env update -f %ENV_FILE%

%CONDA_BIN%/Scripts/activate.bat hummingbot

@rem %CONDA_EXE% develop .

@rem %CONDA_BIN%/Scripts/pip install objgraph

@rem %CONDA_BIN%/envs/hummingbot/bin/pre-commit install

@pause

