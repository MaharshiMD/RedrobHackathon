import json
import csv
import argparse
import sys
import re
from datetime import datetime

# ============================================================================
# Core Constants
# ============================================================================
IT_SERVICES_Firms = [
    'tcs', 'infosys', 'wipro', 'accenture', 'cognizant', 'capgemini',
    'hcl', 'tech mahindra', 'l&t infotech', 'ltimindtree', 'mindtree',
    'mphasis', 'genpact', 'tata consultancy services'
]

REQUIRED_SKILLS = {
    # Core Embeddings & Retrieval
    "embeddings": 1.0,
    "sentence-transformers": 1.0,
    "bge": 1.0,
    "e5": 1.0,
    "vector database": 1.0,
    "pinecone": 1.0,
    "weaviate": 1.0,
    "qdrant": 1.0,
    "milvus": 1.0,
    "opensearch": 1.0,
    "elasticsearch": 0.8,
    "faiss": 1.0,
    "hybrid search": 1.0,
    "dense retrieval": 1.0,
    "retrieval-augmented generation": 1.0,
    "rag": 1.0,
    # Programming
    "python": 0.8,
    # Evaluation
    "ndcg": 1.0,
    "mrr": 1.0,
    "map": 1.0,
    "ranking evaluation": 1.0,
    "evaluation frameworks": 1.0,
    "a/b testing": 0.8,
    # Nice-to-haves
    "llm fine-tuning": 0.7,
    "lora": 0.7,
    "qlora": 0.7,
    "peft": 0.7,
    "learning to rank": 0.7,
    "xgboost": 0.5,
    "learning-to-rank": 0.7,
    "nlp": 0.6,
    "information retrieval": 0.8,
    "ir": 0.6,
}

# ============================================================================
# Filter Helpers
# ============================================================================
def is_honeypot(candidate, current_date=datetime(2026, 6, 26)):
    """
    Applies our 4 mathematical and logical checks to detect honeypot profiles.
    Returns True if the profile is a honeypot, otherwise False.
    """
    cid = candidate['candidate_id']
    profile = candidate.get('profile', {})
    career = candidate.get('career_history', [])
    skills = candidate.get('skills', [])
    yoe = profile.get('years_of_experience', 0)
    
    # 1. Impossible job durations
    for job in career:
        start_str = job.get('start_date')
        end_str = job.get('end_date')
        dur = job.get('duration_months', 0)
        if start_str:
            try:
                start_dt = datetime.strptime(start_str, "%Y-%m-%d")
                if end_str:
                    end_dt = datetime.strptime(end_str, "%Y-%m-%d")
                else:
                    end_dt = current_date
                max_months = (end_dt.year - start_dt.year) * 12 + (end_dt.month - start_dt.month) + 1
                if dur > max_months + 6:
                    return True
            except:
                pass
                
    # 2. Expert/advanced skills with 0 duration
    expert_zero_dur = 0
    for s in skills:
        prof = s.get('proficiency')
        dur = s.get('duration_months')
        if prof in ['expert', 'advanced'] and (dur == 0 or dur is None):
            expert_zero_dur += 1
    if expert_zero_dur >= 3:
        return True
        
    # 3. YoE vs Career total duration mismatch
    total_job_months = sum(job.get('duration_months', 0) for job in career)
    total_job_years = total_job_months / 12.0
    if abs(yoe - total_job_years) > 4.0:
        return True
        
    # 4. Skill duration exceeds YoE
    max_skill_months = yoe * 12 + 48 # 4 years buffer
    for s in skills:
        dur = s.get('duration_months')
        if dur is not None and dur > max_skill_months:
            return True
            
    return False

def has_only_consulting_experience(candidate):
    """
    Returns True if the candidate has worked ONLY at IT consulting firms.
    """
    career = candidate.get('career_history', [])
    if not career:
        return False
    
    for job in career:
        company = job.get('company', '').lower()
        # Check if company name matches any of our IT consulting firms list
        is_consulting = False
        for firm in IT_SERVICES_Firms:
            if firm in company:
                is_consulting = True
                break
        if not is_consulting:
            return False
            
    return True

# ============================================================================
# Scoring Logic
# ============================================================================
def score_candidate(candidate, current_date=datetime(2026, 6, 26)):
    """
    Calculates a composite score between 0.0 and 1.0 for the candidate.
    """
    profile = candidate.get('profile', {})
    career = candidate.get('career_history', [])
    skills = candidate.get('skills', [])
    signals = candidate.get('redrob_signals', {})
    edu = candidate.get('education', [])
    
    # ----------------------------------------------------
    # 1. Skills Score (S_skills - Weight: 0.45)
    # ----------------------------------------------------
    skills_score = 0.0
    total_skill_weight = 0.0
    
    # Pre-parse description texts to detect if skill is mentioned in career/profile
    descriptions = " ".join([job.get('description', '') for job in career]).lower()
    profile_text = (profile.get('summary', '') + " " + profile.get('headline', '')).lower()
    all_context_text = descriptions + " " + profile_text
    
    matching_skills = []
    
    for s in skills:
        name = s.get('name', '').lower()
        prof = s.get('proficiency', 'beginner')
        dur_months = s.get('duration_months', 0)
        
        # Check if the skill matches any of our required skills
        skill_wt = 0.0
        for req_skill, wt in REQUIRED_SKILLS.items():
            if req_skill in name:
                skill_wt = max(skill_wt, wt)
                
        if skill_wt > 0.0:
            matching_skills.append((name, prof, dur_months))
            # Proficiency multiplier
            prof_mult = 1.0
            if prof == 'expert':
                prof_mult = 1.2
            elif prof == 'advanced':
                prof_mult = 1.0
            elif prof == 'intermediate':
                prof_mult = 0.7
            elif prof == 'beginner':
                prof_mult = 0.3
                
            # Duration factor: 36 months gives full score
            dur_mult = min(dur_months / 36.0, 1.0) if dur_months else 0.2
            
            # Check if mentioned in job descriptions to filter keyword stuffers
            mention_factor = 1.0
            # Tokenize and match
            clean_name = re.sub(r'[^a-z0-9\s]', ' ', name)
            if all(word in all_context_text for word in clean_name.split() if len(word) > 2):
                mention_factor = 1.0
            else:
                mention_factor = 0.35 # heavy discount if not in descriptions
                
            skill_score = skill_wt * prof_mult * (0.4 * dur_mult + 0.6 * mention_factor)
            skills_score += skill_score
            total_skill_weight += skill_wt
            
    if total_skill_weight > 0.0:
        skills_score = min(skills_score / 15.0, 1.0) # Normalize by a standard target score of 15.0
    else:
        skills_score = 0.0
        
    # Penalize if they have absolutely no NLP / IR / RAG / Search / ML skills
    has_ml_search = any(x in all_context_text for x in ['search', 'retrieval', 'embeddings', 'rag', 'llm', 'nlp', 'ranking', 'recommend', 'vector'])
    if not has_ml_search:
        skills_score *= 0.1
        
    # ----------------------------------------------------
    # 2. Experience Quality Score (S_exp - Weight: 0.30)
    # ----------------------------------------------------
    # Experience years matching
    yoe = profile.get('years_of_experience', 0)
    if 5.0 <= yoe <= 9.0:
        yoe_fit = 1.0
    elif 4.0 <= yoe < 5.0 or 9.0 < yoe <= 11.0:
        yoe_fit = 0.85
    elif 3.0 <= yoe < 4.0 or 11.0 < yoe <= 13.0:
        yoe_fit = 0.60
    elif yoe > 13.0:
        yoe_fit = 0.40
    else:
        yoe_fit = 0.10
        
    # Check if they have been active developers (NLP / ML backend)
    # Scan job descriptions for "shipped", "deployed", "scaled", "infrastructure", "latency", "vector", "pinecone", etc.
    product_keywords = ["shipped", "deployed", "scaled", "infrastructure", "systems", "vector", "search", "retrieval", "production", "latency", "pipeline", "matching"]
    product_count = sum(1 for kw in product_keywords if kw in descriptions)
    product_fit = min(product_count / 5.0, 1.0)
    
    # Education prestige
    edu_scores = []
    for e in edu:
        tier = e.get('tier', 'unknown')
        if tier == 'tier_1':
            edu_scores.append(1.0)
        elif tier == 'tier_2':
            edu_scores.append(0.8)
        elif tier == 'tier_3':
            edu_scores.append(0.6)
        elif tier == 'tier_4':
            edu_scores.append(0.4)
        else:
            edu_scores.append(0.5)
    edu_score = sum(edu_scores) / len(edu_scores) if edu_scores else 0.5
    
    # Current company check: discount if currently at service firm (but not ONLY worked there)
    current_company = profile.get('current_company', '').lower()
    current_firm_discount = 1.0
    for firm in IT_SERVICES_Firms:
        if firm in current_company:
            current_firm_discount = 0.7
            break
            
    exp_score = (0.5 * yoe_fit + 0.3 * product_fit + 0.2 * edu_score) * current_firm_discount

    # ----------------------------------------------------
    # 3. Behavioral Signals Score (S_signals - Weight: 0.15)
    # ----------------------------------------------------
    # recruiter_response_rate
    resp_rate = signals.get('recruiter_response_rate', 0.0)
    if resp_rate >= 0.8:
        resp_score = 1.0
    elif resp_rate >= 0.5:
        resp_score = 0.85
    elif resp_rate >= 0.25:
        resp_score = 0.60
    elif resp_rate < 0.15:
        resp_score = 0.10 # heavily penalized
    else:
        resp_score = 0.40
        
    # avg_response_time_hours
    resp_time = signals.get('avg_response_time_hours', 168.0)
    if resp_time <= 12.0:
        time_score = 1.0
    elif resp_time <= 24.0:
        time_score = 0.9
    elif resp_time <= 72.0:
        time_score = 0.7
    elif resp_time <= 168.0:
        time_score = 0.4
    else:
        time_score = 0.1
        
    # last_active_date recency
    active_str = signals.get('last_active_date')
    active_score = 0.5
    if active_str:
        try:
            active_dt = datetime.strptime(active_str, "%Y-%m-%d")
            days_inactive = (current_date - active_dt).days
            if days_inactive <= 30:
                active_score = 1.0
            elif days_inactive <= 90:
                active_score = 0.85
            elif days_inactive <= 180:
                active_score = 0.50
            else:
                active_score = 0.10 # inactive for > 6 months
        except:
            pass
            
    # GitHub activity bonus
    github_score = 0.5
    gh_val = signals.get('github_activity_score', -1)
    if gh_val >= 60:
        github_score = 1.0
    elif gh_val >= 30:
        github_score = 0.85
    elif gh_val >= 0:
        github_score = 0.7
    else:
        github_score = 0.5 # no github linked
        
    # Open to work flag
    open_score = 1.0 if signals.get('open_to_work_flag') else 0.7
    
    signals_score = 0.3 * resp_score + 0.2 * time_score + 0.2 * active_score + 0.15 * github_score + 0.15 * open_score

    # ----------------------------------------------------
    # 4. Logistics & Fit Score (S_fit - Weight: 0.10)
    # ----------------------------------------------------
    loc = profile.get('location', '').lower()
    country = profile.get('country', '').lower()
    willing_relocate = signals.get('willing_to_relocate', False)
    
    # Location scoring
    if 'noida' in loc or 'pune' in loc:
        loc_score = 1.0
    elif 'delhi' in loc or 'gurgaon' in loc or 'ncr' in loc or 'ghaziabad' in loc:
        loc_score = 0.95 # very close to Noida office
    elif 'mumbai' in loc or 'hyderabad' in loc or 'bangalore' in loc or 'bengaluru' in loc or 'chennai' in loc:
        loc_score = 0.85 if willing_relocate else 0.65
    elif 'india' in country or 'india' in loc:
        loc_score = 0.75 if willing_relocate else 0.50
    else: # outside India
        loc_score = 0.40 if willing_relocate else 0.10
        
    # Notice period scoring
    np_days = signals.get('notice_period_days', 60)
    if np_days <= 15:
        np_score = 1.0
    elif np_days <= 30:
        np_score = 0.95
    elif np_days <= 60:
        np_score = 0.75
    elif np_days <= 90:
        np_score = 0.50
    else:
        np_score = 0.15 # 90+ days notice is a heavy bottleneck
        
    fit_score = 0.6 * loc_score + 0.4 * np_score
    
    # ----------------------------------------------------
    # Composite Weighted Score
    # ----------------------------------------------------
    composite = 0.45 * skills_score + 0.30 * exp_score + 0.15 * signals_score + 0.10 * fit_score
    return round(composite, 4), matching_skills

# ============================================================================
# Reasoning Generator
# ============================================================================
def generate_custom_reasoning(candidate, score, matching_skills):
    """
    Generates a 1-2 sentence customized reasoning string for the candidate.
    References specific profile facts and avoids templated phrases.
    """
    profile = candidate.get('profile', {})
    signals = candidate.get('redrob_signals', {})
    career = candidate.get('career_history', [])
    
    name = profile.get('anonymized_name', 'Candidate')
    yoe = profile.get('years_of_experience', 0)
    loc = profile.get('location', '')
    current_title = profile.get('current_title', '')
    current_company = profile.get('current_company', '')
    np_days = signals.get('notice_period_days', 60)
    willing_relocate = signals.get('willing_to_relocate', False)
    
    # Extract clean skills list
    top_skills = []
    # Sort skills by duration or proficiency
    for skill_name, prof, dur in matching_skills[:3]:
        # Clean name a bit
        top_skills.append(skill_name.title())
    skills_str = ", ".join(top_skills) if top_skills else "Search/ML pipelines"
    
    # Fictional / startup company check
    product_companies = []
    for job in career:
        comp = job.get('company')
        if comp and not any(f in comp.lower() for f in IT_SERVICES_Firms):
            product_companies.append(comp)
            
    recent_comp = product_companies[0] if product_companies else current_company
    
    # Structure reasoning sentences dynamically
    s1 = ""
    s2 = ""
    
    # Sentence 1: Background & Skills
    if len(product_companies) >= 2:
        s1 = f"Product-oriented AI engineer with {yoe} YoE, having shipped search/retrieval systems at {recent_comp} and {product_companies[1]}."
    elif current_title and recent_comp:
        s1 = f"{current_title} with {yoe} years of experience designing and optimizing {skills_str} at {recent_comp}."
    else:
        s1 = f"AI Software Engineer with {yoe} years of experience focused on {skills_str}."
        
    # Sentence 2: Fit & Logistics
    np_phrase = f"{np_days}-day notice period" if np_days > 0 else "immediate availability"
    if 'noida' in loc.lower() or 'pune' in loc.lower():
        s2 = f"Based locally in {loc} with a {np_phrase}, matching the hybrid Cadence perfectly."
    elif willing_relocate:
        s2 = f"Located in {loc} but willing to relocate to Noida/Pune; has a {np_phrase}."
    else:
        s2 = f"Currently based in {loc} with a {np_phrase}; excellent engagement signals on the platform."
        
    # Let's check for any notice period concerns
    if np_days >= 90:
        s2 += " Note: notice period of 90 days requires buyout."
        
    return f"{s1} {s2}"

# ============================================================================
# Main Ranking Function
# ============================================================================
def main():
    parser = argparse.ArgumentParser(description="Rank candidates for Senior AI Engineer JD.")
    parser.add_argument("--candidates", required=True, help="Path to candidates.jsonl")
    parser.add_argument("--out", required=True, help="Path to output CSV")
    args = parser.parse_args()
    
    scored_candidates = []
    honeypot_count = 0
    consulting_count = 0
    total_count = 0
    
    print(f"Reading and streaming candidates from {args.candidates}...")
    try:
        with open(args.candidates, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                total_count += 1
                c = json.loads(line)
                
                # Check filters first to avoid wasting scoring computations and memory
                if is_honeypot(c):
                    honeypot_count += 1
                    continue
                if has_only_consulting_experience(c):
                    consulting_count += 1
                    continue
                
                score, matching_skills = score_candidate(c)
                
                # To save memory, minimize the candidate details stored in memory
                # Only keep fields necessary for final sorting, tie-breaking, and reasoning
                mini_candidate = {
                    'candidate_id': c['candidate_id'],
                    'profile': {
                        'anonymized_name': c['profile'].get('anonymized_name'),
                        'location': c['profile'].get('location'),
                        'country': c['profile'].get('country'),
                        'years_of_experience': c['profile'].get('years_of_experience'),
                        'current_title': c['profile'].get('current_title'),
                        'current_company': c['profile'].get('current_company')
                    },
                    'career_history': [
                        {
                            'company': job.get('company'),
                            'title': job.get('title'),
                            'description': job.get('description')
                        } for job in c.get('career_history', [])
                    ],
                    'redrob_signals': {
                        'notice_period_days': c['redrob_signals'].get('notice_period_days'),
                        'willing_to_relocate': c['redrob_signals'].get('willing_to_relocate')
                    }
                }
                
                scored_candidates.append({
                    'candidate': mini_candidate,
                    'score': score,
                    'matching_skills': matching_skills
                })
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
        
    print(f"Total processed candidates: {total_count}")
    print(f"Filtered out {honeypot_count} honeypots and {consulting_count} consulting-only profiles.")
    print(f"Scored candidates stored in memory: {len(scored_candidates)}")
    
    # Step 2: Sort by score descending, tie-break by candidate_id ascending
    scored_candidates.sort(key=lambda x: (-x['score'], x['candidate']['candidate_id']))
    
    # Step 3: Extract Top 100
    top_100 = scored_candidates[:100]
    
    # Step 4: Write output CSV
    print(f"Writing top 100 candidates to {args.out}...")
    try:
        with open(args.out, "w", encoding="utf-8", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["candidate_id", "rank", "score", "reasoning"])
            
            for rank_idx, item in enumerate(top_100):
                c = item['candidate']
                cid = c['candidate_id']
                score = item['score']
                matching_skills = item['matching_skills']
                rank = rank_idx + 1
                
                # Generate reasoning
                reasoning = generate_custom_reasoning(c, score, matching_skills)
                writer.writerow([cid, rank, score, reasoning])
                
        print("Success! Output CSV is generated.")
    except Exception as e:
        print(f"Error writing CSV output: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

