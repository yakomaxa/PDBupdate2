import html
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime


def get_onlinetxt(url):
    """Fetches plain text list of new PDB IDs from PDBj."""
    req = urllib.request.Request(url, headers={"User-Agent": "Structure-Intelligence/1.0"})
    for _ in range(3):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status == 200:
                    return resp.read().decode("utf-8")
        except Exception:
            continue
    return ""


def get_title(pdbid):
    """Fetches mmJSON entry details (title & contact author email) from PDBj."""
    url = f"https://data.pdbj.org/pdbjplus/data/pdb/mmjson-noatom/{pdbid.lower()}-noatom.json"
    req = urllib.request.Request(url, headers={"User-Agent": "Structure-Intelligence/1.0"})
    
    for _ in range(3):
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    json_data = json.loads(resp.read().decode("utf-8"))
                    name = "data_" + pdbid.upper()
                    entry_data = json_data.get(name, {})
                    
                    title_list = entry_data.get("struct", {}).get("title", [])
                    title = title_list[0] if title_list else "No title"
                    
                    email_list = entry_data.get("pdbx_contact_author", {}).get("email", ["zzzzzzz"])
                    email = email_list[0] if email_list else "zzzzzzz"
                    
                    return f"{pdbid.upper()}: {title}", email
        except Exception as e:
            print(f"[ERROR] Failed fetching metadata for {pdbid}: {e}")
            continue
    return "error", "error"


def generate_tsv_from_entries(entry_list, output_file_name):
    """Generates entries.tsv containing ID, title, and author email."""
    os.makedirs(os.path.dirname(output_file_name) or ".", exist_ok=True)
    with open(output_file_name, "w", encoding="utf-8") as file:
        for count, entry in enumerate(entry_list, start=1):
            entry = entry.strip()
            if not entry:
                continue
            print(f"[{count}/{len(entry_list)}] Processing {entry}...")
            description, email = get_title(entry)
            if description != "error":
                file.write(f"{entry}\t{description}\t{email}\n")


def generate_html_from_tsv(file_name, template_file, modal_block_file, output_file):
    """Builds the modern responsive index.html for GitHub Pages."""
    entries = []
    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as file:
            lines = [line.strip().split("\t") for line in file if line.strip()]
            entries = [(line[0], line[1], line[2]) for line in lines if len(line) >= 3]

    # Sort entries by author email (preserves original sorting logic)
    entries = sorted(entries, key=lambda x: x[2])
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    thumbnail_html = ""
    js_entries = []

    for i, (entry, title, email) in enumerate(entries):
        pdbid = entry.lower()
        pdbid_uc = entry.upper()
        
        safe_title = html.escape(title)
        safe_email = html.escape(email)
        
        thumbnail_url = f"https://pdbj.org/molmil-images/mine/{pdbid}.png"
        pdbj_url = f"https://pdbj.org/mine/summary/{pdbid}"

        thumbnail_html += f"""
<div class="card" onclick="openModal({i})">
  <div class="img-container">
    <img src="{thumbnail_url}" alt="{pdbid_uc}" onerror="this.onerror=null;this.src='https://pdbj.org/images/pdb_logo.png';">
  </div>
  <div class="entry-id">{pdbid_uc}</div>
  <div class="entry-title">
    <a href="{pdbj_url}" target="_blank" onclick="event.stopPropagation()">{safe_title}</a>
  </div>
</div>
"""

        escaped_acc = html.escape(pdbid_uc)
        escaped_title = html.escape(title).replace('"', '\\"')

        js_entries.append(
            f'{{id: "{escaped_acc}", '
            f'title: "{escaped_title}", '
            f'email: "{safe_email}", '
            f'src: "{thumbnail_url}", '
            f'link: "{pdbj_url}"}}'
        )

    image_data_js = ",\n".join(js_entries)

    with open(template_file, "r", encoding="utf-8") as f:
        template = f.read()

    with open(modal_block_file, "r", encoding="utf-8") as f:
        modal_block = f.read().replace("{{IMAGE_DATA}}", image_data_js)

    final_html = (
        template.replace("{{TIMESTAMP}}", now)
        .replace("{{THUMBNAILS}}", thumbnail_html)
        .replace("{{MODAL_JS}}", modal_block)
    )

    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(final_html)


if __name__ == "__main__":
    template_path = sys.argv[1] if len(sys.argv) > 1 else ".github/scripts/template.html"
    modal_path = sys.argv[2] if len(sys.argv) > 2 else ".github/scripts/modal_block.js"
    make_tsv = sys.argv[3] if len(sys.argv) > 3 else "yes"

    tsv_file = "entries.tsv"

    if make_tsv.lower() == "yes":
        print("Fetching new PDB entries list...")
        new_entry_url = "https://pdbj.org/rest/newweb/search/sql?q=select+bs.pdbid+from+pdbj.brief_summary+bs+inner+join+misc.id_meta_list+iml+on+bs.pdbid%3Diml.id+where+iml.category%3D%27pdb_new%27&format=txt"
        entry_text = get_onlinetxt(new_entry_url)
        entry_list = [e for e in entry_text.strip().split("\n") if e.strip()]
        
        print(f"Found {len(entry_list)} entries. Generating TSV...")
        generate_tsv_from_entries(entry_list, tsv_file)

    generate_html_from_tsv(
        file_name=tsv_file,
        template_file=template_path,
        modal_block_file=modal_path,
        output_file="docs/index.html",
    )
    print("PDB summary page generated successfully at docs/index.html.")
    
