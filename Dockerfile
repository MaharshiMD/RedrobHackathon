FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy the repository code and data into the container
COPY . /app

# Default command to run the candidate ranker and produce the submission CSV
CMD ["python", "rank.py", "--candidates", "./[PUB] India_runs_data_and_ai_challenge/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/candidates.jsonl", "--out", "./team_antigravity.csv"]
