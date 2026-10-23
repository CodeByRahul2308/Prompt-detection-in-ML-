"""
Generate professional, publication-quality PDFs for Minor Project preparation documents:
1. presentation_speaker_notes.pdf
2. viva_questions.pdf
3. demo_script.pdf
4. major_project_roadmap.pdf

Uses markdown-it-py to parse markdown, applies rich academic CSS styling with full
Unicode Devanagari support, and invokes Edge headless to print pristine PDFs.
"""

import os
import sys
import subprocess
import re
from markdown_it import MarkdownIt
import PyPDF2

sys.stdout.reconfigure(encoding='utf-8')

workspace_dir = os.path.abspath(".")
presentation_dir = os.path.join(workspace_dir, "presentation")
scripts_dir = os.path.join(workspace_dir, "scripts")
edge_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# Base CSS for academic document styling
COMMON_CSS = """
@page {
    size: A4;
    margin: 18mm 16mm 20mm 16mm;
    @bottom-right {
        content: counter(page);
    }
}

* {
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', 'Nirmala UI', -apple-system, BlinkMacSystemFont, Arial, sans-serif;
    color: #1e293b;
    line-height: 1.55;
    font-size: 10pt;
    margin: 0;
    padding: 0;
    background: #ffffff;
}

/* Header & Banner */
.doc-header {
    border-bottom: 2px solid #0f172a;
    padding-bottom: 12px;
    margin-bottom: 20px;
}

.doc-header h1 {
    font-size: 18pt;
    color: #0f172a;
    margin: 0 0 6px 0;
    font-weight: 700;
    letter-spacing: -0.3px;
}

.doc-meta {
    font-size: 9pt;
    color: #475569;
    display: flex;
    flex-wrap: wrap;
    gap: 14px;
    margin-top: 6px;
    line-height: 1.4;
}

.doc-meta strong {
    color: #0f172a;
}

.badge {
    display: inline-block;
    padding: 2px 7px;
    font-size: 8pt;
    font-weight: 600;
    border-radius: 4px;
    background: #e2e8f0;
    color: #1e293b;
}

.badge-navy { background: #0f172a; color: #ffffff; }
.badge-teal { background: #0d9488; color: #ffffff; }
.badge-purple { background: #6366f1; color: #ffffff; }

/* Headings */
h1 { font-size: 16pt; color: #0f172a; margin-top: 20px; margin-bottom: 10px; border-bottom: 1.5px solid #cbd5e1; padding-bottom: 4px; }
h2 { font-size: 13pt; color: #0f172a; margin-top: 18px; margin-bottom: 8px; border-bottom: 1px solid #e2e8f0; padding-bottom: 3px; page-break-after: avoid; }
h3 { font-size: 11pt; color: #0f172a; margin-top: 14px; margin-bottom: 6px; page-break-after: avoid; }
h4 { font-size: 10pt; color: #0f172a; margin-top: 10px; margin-bottom: 4px; page-break-after: avoid; }

p {
    margin: 0 0 8px 0;
}

/* Viva Q&A Cards */
.qa-card {
    border-left: 3px solid #0d9488;
    background: #f8fafc;
    padding: 10px 14px;
    margin-bottom: 12px;
    border-radius: 0 6px 6px 0;
    page-break-inside: avoid;
}

.qa-card.accent-navy {
    border-left-color: #0f172a;
}

.qa-question {
    font-weight: 700;
    color: #0f172a;
    font-size: 10.5pt;
    margin-bottom: 6px;
}

.qa-answer {
    color: #334155;
    font-size: 9.5pt;
}

.qa-answer p:last-child {
    margin-bottom: 0;
}

/* Slide Notes Cards */
.slide-note-card {
    border: 1px solid #e2e8f0;
    border-top: 3px solid #0f172a;
    background: #ffffff;
    border-radius: 4px;
    padding: 12px 14px;
    margin-bottom: 14px;
    page-break-inside: avoid;
}

.slide-note-card.rahul {
    border-top-color: #0f172a;
}

.slide-note-card.kishan {
    border-top-color: #0d9488;
}

.slide-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #f1f5f9;
    padding-bottom: 6px;
    margin-bottom: 8px;
}

.slide-title-text {
    font-size: 11pt;
    font-weight: 700;
    color: #0f172a;
}

.speaker-pill {
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 8pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.speaker-rahul { background: #e0e7ff; color: #3730a3; }
.speaker-kishan { background: #ccfbf1; color: #115e59; }
.speaker-both { background: #fef3c7; color: #92400e; }

blockquote {
    margin: 8px 0;
    padding: 8px 12px;
    background: #f8fafc;
    border-left: 3px solid #0d9488;
    color: #1e293b;
    font-style: italic;
    font-size: 9.5pt;
}

/* Tables */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0 14px 0;
    font-size: 9pt;
    page-break-inside: auto;
}

tr {
    page-break-inside: avoid;
}

th {
    background: #0f172a;
    color: #ffffff;
    font-weight: 600;
    text-align: left;
    padding: 7px 10px;
    border: 1px solid #0f172a;
}

td {
    padding: 6px 10px;
    border: 1px solid #cbd5e1;
    color: #334155;
    vertical-align: top;
}

tr:nth-child(even) td {
    background: #f8fafc;
}

/* Code Blocks */
pre {
    background: #0f172a;
    color: #f8fafc;
    padding: 10px 12px;
    border-radius: 4px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 8.5pt;
    overflow-x: auto;
    margin: 8px 0;
    page-break-inside: avoid;
}

code {
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 9pt;
    background: #f1f5f9;
    color: #0f172a;
    padding: 1px 4px;
    border-radius: 3px;
    border: 1px solid #e2e8f0;
}

pre code {
    background: transparent;
    color: inherit;
    padding: 0;
    border: none;
}

/* Lists */
ul, ol {
    margin: 0 0 8px 0;
    padding-left: 20px;
}

li {
    margin-bottom: 4px;
}

/* Footer & Page Numbers */
.footer-note {
    margin-top: 24px;
    padding-top: 10px;
    border-top: 1px solid #e2e8f0;
    font-size: 8pt;
    color: #64748b;
    text-align: center;
}

hr {
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 16px 0;
}
"""

def md_to_html(md_text):
    """Convert markdown text to HTML using markdown-it-py."""
    md = MarkdownIt().enable('table').enable('strikethrough')
    return md.render(md_text)

def build_viva_questions_html(md_path):
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split into sections and parse Q&A cleanly
    lines = content.split('\n')
    header_info = []
    body_lines = []
    
    in_header = True
    for line in lines:
        if in_header:
            if line.strip().startswith('---'):
                in_header = False
                continue
            header_info.append(line)
        else:
            body_lines.append(line)
            
    raw_body = '\n'.join(body_lines)
    
    # Process Q&A blocks to wrap them in .qa-card
    # Questions start with #### Q
    qa_blocks = re.split(r'(####\s+Q\d+\.\s+.*?)(?=\n####\s+Q\d+\.|\n###\s+Category|\Z)', raw_body, flags=re.DOTALL)
    
    processed_body = ""
    md = MarkdownIt().enable('table')
    
    for block in qa_blocks:
        block = block.strip()
        if not block:
            continue
        if block.startswith('#### Q'):
            # It's a question block
            q_match = re.match(r'####\s+(Q\d+\.\s+.*?)\n(.*)', block, flags=re.DOTALL)
            if q_match:
                q_title = q_match.group(1).strip()
                ans_content = q_match.group(2).strip()
                ans_html = md.render(ans_content)
                processed_body += f"""
                <div class="qa-card">
                    <div class="qa-question">{q_title}</div>
                    <div class="qa-answer">{ans_html}</div>
                </div>
                """
            else:
                processed_body += md.render(block)
        else:
            processed_body += md.render(block)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Comprehensive Viva Voce Preparation Guide</title>
<style>
{COMMON_CSS}
</style>
</head>
<body>
<div class="doc-header">
    <h1>Comprehensive Viva Voce Preparation Guide</h1>
    <div class="doc-meta">
        <div><strong>Project:</strong> Explainable Detection of Prompt Injection Attacks in Hindi and Hinglish</div>
        <div><strong>Candidates:</strong> Rahul Patel & Kishan Gupta</div>
        <div><strong>Degree:</strong> B.Tech CSE (7th Semester Minor Project)</div>
        <div><span class="badge badge-navy">35 Verified Q&A</span> <span class="badge badge-teal">Academic Reference</span></div>
    </div>
</div>
{processed_body}
<div class="footer-note">
    B.Tech Minor Project Viva Guide · Department of Computer Science & Engineering · Academic Session 2026–2027
</div>
</body>
</html>"""
    return html

def build_speaker_notes_html(md_path):
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split into sections and parse slide by slide
    parts = re.split(r'(###\s+Slide\s+\d+:.*?)(?=\n###\s+Slide\s+\d+:|\Z)', content, flags=re.DOTALL)
    
    md = MarkdownIt().enable('table')
    intro_html = md.render(parts[0])
    
    slides_html = ""
    for part in parts[1:]:
        part = part.strip()
        if not part:
            continue
        m = re.match(r'###\s+Slide\s+(\d+):\s+(.*?)\n(.*)', part, flags=re.DOTALL)
        if m:
            slide_num = m.group(1)
            slide_title = m.group(2).strip()
            rest = m.group(3).strip()
            
            # Check speaker
            speaker = "Both"
            card_class = "both"
            pill_class = "speaker-both"
            if "Rahul Patel" in rest or "Rahul" in rest:
                speaker = "Rahul Patel"
                card_class = "rahul"
                pill_class = "speaker-rahul"
            elif "Kishan Gupta" in rest or "Kishan" in rest:
                speaker = "Kishan Gupta"
                card_class = "kishan"
                pill_class = "speaker-kishan"
                
            body_html = md.render(rest)
            
            slides_html += f"""
            <div class="slide-note-card {card_class}">
                <div class="slide-header">
                    <span class="slide-title-text">Slide {slide_num}: {slide_title}</span>
                    <span class="speaker-pill {pill_class}">{speaker}</span>
                </div>
                <div class="slide-content">
                    {body_html}
                </div>
            </div>
            """
        else:
            slides_html += md.render(part)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Minor Project Presentation: Speaker Notes</title>
<style>
{COMMON_CSS}
</style>
</head>
<body>
<div class="doc-header">
    <h1>Minor Project Presentation: Speaker Notes (16-Slide Deck)</h1>
    <div class="doc-meta">
        <div><strong>Project:</strong> Explainable Detection of Prompt Injection Attacks in Hindi and Hinglish</div>
        <div><strong>Speakers:</strong> Rahul Patel & Kishan Gupta</div>
        <div><strong>Duration:</strong> 6 to 8 Minutes</div>
        <div><span class="badge badge-navy">16 Slides</span> <span class="badge badge-teal">Slide-by-Slide Script</span></div>
    </div>
</div>
{intro_html}
<h2>Slide-by-Slide Presentation Script</h2>
{slides_html}
<div class="footer-note">
    Minor Project Presentation Notes · Rahul Patel & Kishan Gupta · Department of CSE · 2026–2027
</div>
</body>
</html>"""
    return html

def build_demo_script_html(md_path):
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    md = MarkdownIt().enable('table')
    body_html = md.render(content)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>2-Minute Prototype Demonstration Script</title>
<style>
{COMMON_CSS}
</style>
</head>
<body>
<div class="doc-header">
    <h1>2-Minute Prototype Demonstration Script</h1>
    <div class="doc-meta">
        <div><strong>Application:</strong> Explainable Hybrid Prompt Injection Detector (Streamlit)</div>
        <div><strong>Presenters:</strong> Rahul Patel & Kishan Gupta</div>
        <div><strong>Target Time:</strong> 2 Minutes</div>
        <div><span class="badge badge-teal">app.py</span> <span class="badge badge-navy">Live Demo Routine</span></div>
    </div>
</div>
{body_html}
<div class="footer-note">
    Streamlit Prototype Live Demo Script · Rahul Patel & Kishan Gupta · 2026–2027
</div>
</body>
</html>"""
    return html

def build_roadmap_html(md_path):
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    md = MarkdownIt().enable('table')
    body_html = md.render(content)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Major Project Roadmap (8th Semester B.Tech)</title>
<style>
{COMMON_CSS}
</style>
</head>
<body>
<div class="doc-header">
    <h1>Major Project Roadmap (8th Semester B.Tech)</h1>
    <div class="doc-meta">
        <div><strong>Continuation From:</strong> 7th Semester Minor Project (Hybrid Rule-Based + TF-IDF Baseline)</div>
        <div><strong>Team:</strong> Rahul Patel & Kishan Gupta</div>
        <div><strong>Target Duration:</strong> January 2027 – May 2027 (5 Months)</div>
        <div><span class="badge badge-navy">IndicBERT / XLM-R</span> <span class="badge badge-teal">Phase 1 to Phase 5</span></div>
    </div>
</div>
{body_html}
<div class="footer-note">
    B.Tech 8th Semester Major Project Roadmap · Rahul Patel & Kishan Gupta · 2026–2027
</div>
</body>
</html>"""
    return html

def convert_html_to_pdf(html_content, output_pdf_path):
    temp_html_path = output_pdf_path.replace(".pdf", "_temp.html")
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    html_file_url = f"file:///{temp_html_path.replace(os.sep, '/')}"
    
    cmd = [
        edge_exe,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={output_pdf_path}",
        html_file_url
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Clean up temp html
    if os.path.exists(temp_html_path):
        os.remove(temp_html_path)
        
    if os.path.exists(output_pdf_path) and os.path.getsize(output_pdf_path) > 1000:
        return True, None
    else:
        return False, f"Return code {result.returncode}, stderr: {result.stderr}"

def verify_pdf(pdf_path):
    """Verify that PDF opens, has pages, and contains text."""
    try:
        reader = PyPDF2.PdfReader(pdf_path)
        num_pages = len(reader.pages)
        total_chars = 0
        sample_text = ""
        for page in reader.pages:
            t = page.extract_text() or ""
            total_chars += len(t)
            if not sample_text and t.strip():
                sample_text = t.strip()[:100].replace('\n', ' ')
        return {
            "valid": True,
            "pages": num_pages,
            "characters": total_chars,
            "sample": sample_text,
            "size_kb": os.path.getsize(pdf_path) / 1024
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }

def main():
    docs_to_generate = [
        {
            "md": os.path.join(presentation_dir, "presentation_speaker_notes.md"),
            "pdf": os.path.join(presentation_dir, "presentation_speaker_notes.pdf"),
            "builder": build_speaker_notes_html,
            "name": "Speaker Notes"
        },
        {
            "md": os.path.join(presentation_dir, "viva_questions.md"),
            "pdf": os.path.join(presentation_dir, "viva_questions.pdf"),
            "builder": build_viva_questions_html,
            "name": "Viva Voce Preparation Guide"
        },
        {
            "md": os.path.join(presentation_dir, "demo_script.md"),
            "pdf": os.path.join(presentation_dir, "demo_script.pdf"),
            "builder": build_demo_script_html,
            "name": "Demo Script"
        },
        {
            "md": os.path.join(presentation_dir, "major_project_roadmap.md"),
            "pdf": os.path.join(presentation_dir, "major_project_roadmap.pdf"),
            "builder": build_roadmap_html,
            "name": "Major Project Roadmap"
        }
    ]

    print("="*70)
    print("TASK 1: GENERATING PREPARATION DOCUMENTATION PDFS")
    print("="*70)

    for item in docs_to_generate:
        print(f"\nProcessing {item['name']}...")
        print(f"  Source MD: {item['md']}")
        print(f"  Target PDF: {item['pdf']}")
        
        html = item["builder"](item["md"])
        success, err = convert_html_to_pdf(html, item["pdf"])
        
        if success:
            v = verify_pdf(item["pdf"])
            if v["valid"]:
                print(f"  SUCCESS: {v['pages']} pages, {v['characters']} chars, {v['size_kb']:.1f} KB")
                print(f"  Sample: {v['sample'][:60]}...")
            else:
                print(f"  VERIFICATION FAILED: {v.get('error')}")
        else:
            print(f"  GENERATION FAILED: {err}")

    print("\n" + "="*70)
    print("TASK 1 EXECUTION COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()
