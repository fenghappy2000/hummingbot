
@set CONDA_BIN=%USERPROFILE%/miniconda3

@set CONDA_EXE=%CONDA_BIN%/Scripts/conda.exe
@set ENV_FILE=setup/environment-win64.yml

@set FirstTime=0

@rem first time
@rem %CONDA_EXE% env create -f %ENV_FILE%

@rem not first time
%CONDA_EXE% env update -f %ENV_FILE%

activate hummingbot

%CONDA_EXE% develop .

pip install objgraph

@rem pre-commit install

@pause

