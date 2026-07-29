.PHONY: install generate-data process-data engineer-features train-models seed-db run-pipeline run-app test clean

install:
	pip install -r requirements.txt

generate-data:
	python3 python/data_generator.py

process-data:
	python3 python/data_processor.py

engineer-features:
	python3 python/feature_engineering.py

train-models:
	python3 python/ml_pipeline.py

seed-db:
	python3 sql/seed_data.py

run-pipeline: generate-data process-data engineer-features train-models seed-db

run-app:
	streamlit run app/streamlit_app.py

test:
	pytest tests/

clean:
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	rm -rf .pytest_cache
	rm -rf models/*.joblib models/*.pkl
	rm -rf data/raw/*.csv data/processed/*.csv
	rm -f database/personal_finance.db personal_finance.db
	rm -rf logs/*.log
