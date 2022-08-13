#!/usr/bin/env bash
echo "Using bash: $BASH_VERSION"

if [-d ./venv]; then
	echo "Activating virtual environment"
	. venv/bin/activate;
fi

uvicorn api.main:app --reload --host 0.0.0.0 --port 9001
