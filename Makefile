run-api:
	uvicorn api.main:app --reload --port 8000

run-ui:
	streamlit run ui/app.py
