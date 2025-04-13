import json
import sys
import os

#Json Downloaded from ESCO link 
#https://esco.ec.europa.eu/en/classification/skills?uri=http://data.europa.eu/esco/isced-f/0613

def extract_skills_from_esco(json_path, output_path="../skills_ontology.txt"):
    unique_skills = set()

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Optional: Add the root title itself as a skill
    root_title = data.get("title")
    if isinstance(root_title, str):
        root_title = root_title.strip().lower()
        if 2 <= len(root_title) <= 60:
            unique_skills.add(root_title)

    # Now go into links -> narrowerSkill -> title
    try:
        narrower_skills = data["links"]["narrowerSkill"]
        for skill in narrower_skills:
            title = skill.get("title")
            if isinstance(title, str):
                clean = title.strip().lower()
                if 2 <= len(clean) <= 60:
                    unique_skills.add(clean)
    except KeyError:
        print("❌ Could not find narrowerSkill in the expected path: links → narrowerSkill → title")
        return

    # Write to output file
    with open(output_path, "w", encoding="utf-8") as out:
        for skill in sorted(unique_skills):
            out.write(skill + "\n")

    print(f"✅ Extracted {len(unique_skills)} skills into {output_path}")


# ---- Main entry point ----
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Usage: python convert_esco_json_to_ontology.py <path_to_esco.json>")
    else:
        input_path = sys.argv[1]
        if not os.path.exists(input_path):
            print(f"❌ File not found: {input_path}")
        else:
            extract_skills_from_esco(input_path)


#Run by calling
#python convert_esco_json_to_ontology.py esco_skills.json