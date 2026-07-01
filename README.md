# Redrob Intelligent Candidate Discovery & Ranking System

This repository contains the candidate discovery and ranking system designed for the **Senior AI Engineer — Founding Team** role at Redrob AI, built for **The Data & AI Challenge**. 

Our ranking system processes a pool of 100,000 candidates and selects the top 100 best-fit professionals. It executes in **under 2 minutes** on a standard CPU, requires no GPU/network resources, and successfully filters out keyword stuffers, consulting-only career histories, and honeypots.

---

## Quick Start & Reproduction

### 1. Installation
The ranker runs on a vanilla Python 3.8+ environment and uses **only standard library modules** to eliminate package version conflicts and dependency overhead during Docker builds.

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/RedrobHackathon.git
cd RedrobHackathon
```

### 2. Run the Ranker
Place your `candidates.jsonl` file in the repository folder. Run the ranker:

```bash
python rank.py --candidates ./candidates.jsonl --out ./team_antigravity.csv
```

### 3. Run the Validator
To verify that the generated file passes all of Redrob's official schema and score formatting rules:

```bash
python "./[PUB] India_runs_data_and_ai_challenge/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/validate_submission.py" team_antigravity.csv
```
*Expected Output: `Submission is valid.`*

---

## Google Colab Sandbox (Dynamic Demo)

To run the ranking system in Google Colab (Stage 1 Sandbox Link requirement):
1. Open the [redrob_ranker.ipynb](./redrob_ranker.ipynb) notebook in Google Colab.
2. Ensure you have your candidate dataset uploaded or access to a small sample.
3. Execute the cells to clone the repository and run the ranker end-to-end.

---

## Running with Docker

You can reproduce the ranking environment inside a sandboxed Docker container:

```bash
# Build the Docker image
docker build -t redrob-ranker .

# Run the container (which generates the output inside)
docker run -it redrob-ranker
```

---

## Methodology & Architecture

Our ranker implements a multi-stage filtering and scoring pipeline designed specifically to combat noisy data and adversarial "traps":

```
  [100,000 Candidate Pool]
             |
             v
   [Stage 1: Hard Filters]  --> Excludes: 70 Honeypots, 9,739 Consulting-Only (TCS, Infosys, etc.)
             |
             v
   [Stage 2: Hybrid Scoring] --> Scores: Skills (45%), Exp (30%), Signals (15%), Logistics (10%)
             |
             v
   [Stage 3: Tiebreaking]   --> deterministic sort (Score DESC, ID ASC)
             |
             v
   [Stage 4: Custom Reasoning] --> Generates unique 1-2 sentence rationales
             |
             v
     [Top 100 Shortlist]
```

### 1. Hard Filters (Adversarial Traps)
*   **Honeypot Detector**: Dynamically catches all **70 honeypots** using 4 logical/mathematical rules:
    1.  *Impossible Job Duration*: Stated job duration is longer than the elapsed months between start date and end date (or current date) by more than 6 months.
    2.  *Expert Skill 0 Duration*: Candidates with $\ge 3$ skills designated as `expert` or `advanced` but with `duration_months == 0` or missing.
    3.  *YoE Mismatch*: Profile `years_of_experience` differs from the sum of career history job durations by $>4.0$ years.
    4.  *Skill Duration Exceeding YoE*: Stated skill duration exceeds total years of experience by $>4.0$ years.
*   **Consulting-Only filter**: Identifies and filters out candidates who have *only* worked at IT consulting/services firms (TCS, Infosys, Wipro, Accenture, Cognizant, Capgemini, HCL, etc.) in their career history. Candidates currently at these firms are allowed *if* they have prior product company experience.

### 2. Hybrid Scoring System
*   **Skills (45%)**: Computes matches against key JD requirements (embeddings, vector search, Pinecone/Weaviate/Milvus, Python, ranking evaluation, and fine-tuning). 
    *   *Anti-Keyword Stuffing Check*: Skills are heavily discounted (multiplied by $0.35$) if the skill term does not appear in the candidate's career descriptions or profile text, neutralizing candidates who dump lists of AI keywords without actual experience.
*   **Experience Quality (30%)**: Matches the 5-9 YoE sweet spot, weights education tier, and scores job descriptions for product engineering action verbs (e.g. `shipped`, `deployed`, `scaled`, `infrastructure`).
*   **Behavioral Signals (15%)**: Assesses availability and activity (`recruiter_response_rate` $\ge 0.5$, response time $\le 24\text{ hours}$, active login within the last 90 days, and GitHub contributions score).
*   **Logistics & Fit (10%)**: Scores location preferences (high score for Noida/Pune, relocatable Tier-1 India) and notice period (buyout warning for $>90\text{ days}$).

### 3. Non-Templated Reasoning Generation
Each shortlist candidate receives a dynamically composed, 1-2 sentence justification detailing:
*   Exact years of experience and core skills.
*   Specific companies worked at (e.g., Zomato, Google, Flipkart).
*   Logistics alignment (notice period, current location, relocation willingness).
*   Honest callouts for potential gaps (e.g. 90-day notice period).
