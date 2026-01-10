import arxiv
import datetime
import pytz

# --- CONFIGURATION ---
# 'all:' searches Title + Abstract + Authors. Broader than 'abs:'
QUERY = 'all:neuromorphic OR all:"spiking neural network" OR all:memristor OR all:"in-memory computing" OR all:"event-based vision"'
MAX_RESULTS = 30  # Increased to ensure we catch enough relevant papers

# Define Keywords for Categorization
# NOTE: The keys here (including emojis) must match EXACTLY with the keys used in display_order later.
CATEGORIES = {
    "🛠 Hardware & Materials": [
        "memristor", "rram", "pcm", "device", "material", "circuit", "cmos", 
        "transistor", "fpga", "accelerator", "chip", "integrated", "hardware", 
        "synaptic device", "crossbar", "conductance"
    ],
    "🧠 Algorithms & Theory": [
        "plasticity", "stdp", "learning rule", "backpropagation", "dynamics", 
        "bifurcation", "chaos", "neuron model", "snn", "spiking", "theory", 
        "optimization", "encoding", "decoding", "information", "liquid state"
    ],
    "👁️ Applications & Sensing": [
        "vision", "camera", "dvs", "event-based", "sensor", "tactile", "skin", 
        "robot", "recognition", "classification", "detection", "tracking", 
        "audio", "speech", "gesture", "uav", "drone"
    ]
}

def clean_text(text):
    """Remove newlines and extra spaces."""
    return text.replace('\n', ' ').strip()

def classify_paper(title, summary):
    """Assigns a category based on keyword matching scores."""
    text = (title + " " + summary).lower()
    scores = {cat: 0 for cat in CATEGORIES}
    
    for cat, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in text:
                scores[cat] += 1
    
    # Find category with max score
    best_cat = max(scores, key=scores.get)
    
    # If no keywords match (score is 0), it goes to Uncategorized
    if scores[best_cat] == 0:
        return "📂 General / Uncategorized"
    return best_cat

def main():
    print(f"🔎 Searching ArXiv for: {QUERY}...")
    
    # --- SEARCH ARXIV ---
    client = arxiv.Client()
    search = arxiv.Search(
        query = QUERY,
        max_results = MAX_RESULTS,
        sort_by = arxiv.SortCriterion.SubmittedDate,
        sort_order = arxiv.SortOrder.Descending
    )
    
    results = list(client.results(search))
    print(f"✅ Found {len(results)} papers.")
    
    # --- GROUP BY CATEGORY ---
    # Dictionary structure: { "Category Name": [List of Papers] }
    paper_groups = {cat: [] for cat in CATEGORIES}
    paper_groups["📂 General / Uncategorized"] = []

    for result in results:
        cat = classify_paper(result.title, result.summary)
        paper_groups[cat].append(result)
        # Debug log to see where papers are going
        print(f"   -> [{cat}] {result.title[:40]}...")

    # --- GENERATE MARKDOWN ---
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    formatted_time = utc_now.strftime('%Y-%m-%d %H:%M UTC')
    
    md_content = f"# 🧠 Open Neuromorphic - Daily ArXiv\n\n"
    md_content += f"**Automated Daily Update** | Last Run: {formatted_time}\n\n"
    md_content += "Papers are automatically categorized by topic and sorted by date.\n\n"
    
    # Check if we have any papers at all
    if not results:
        md_content += "### 😴 No new papers found today.\n"
        md_content += "Check back tomorrow!"
    else:
        # Iterate through categories in a specific order
        # CRITICAL FIX: These strings must match CATEGORIES keys exactly
        display_order = ["🛠 Hardware & Materials", "🧠 Algorithms & Theory", "👁️ Applications & Sensing", "📂 General / Uncategorized"]
        
        for category in display_order:
            papers = paper_groups.get(category, [])
            
            if not papers:
                continue
            
            md_content += f"## {category}\n\n"
            
            for p in papers:
                pub_date = p.published.strftime('%Y-%m-%d')
                authors = [a.name for a in p.authors]
                if len(authors) > 3:
                    author_str = ", ".join(authors[:3]) + " et al."
                else:
                    author_str = ", ".join(authors)
                
                summary = clean_text(p.summary)
                
                md_content += f"### [{p.title}]({p.entry_id})\n"
                md_content += f"**{pub_date}** | *{author_str}*\n\n"
                md_content += f"> {summary}\n\n"
            
            md_content += "---\n\n"

    # --- WRITE TO FILE ---
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(md_content)
    
    print(f"📝 README updated successfully.")

if __name__ == "__main__":
    main()