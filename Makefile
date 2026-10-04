.PHONY: init demo ui clean start reset

init:
	mkdir -p out
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt || true

demo:
	.venv/bin/python scripts/run_demo.py

ui:
	.venv/bin/streamlit run ui/app.py

clean:
	rm -rf out/*

start:
	.venv/bin/python start_demo.py

reset: clean
	.venv/bin/python scripts/make_synthetic_dvr.py
