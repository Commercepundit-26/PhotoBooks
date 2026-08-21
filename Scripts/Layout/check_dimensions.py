import json

with open("/Users/cp/Ronak/CC/Photobooks/Layout/analysis_data.json") as f:
    data = json.load(f)

for doc in data:
    print(f"\n--- {doc['name']} ---")
    for ab in doc['artboards']:
        if (ab['orientation'] == 'Square' and (ab['width'] != 720 or ab['height'] != 720)) or \
           (ab['orientation'] == 'Landscape' and (ab['width'] != 864 or ab['height'] != 576)) or \
           (ab['orientation'] == 'Portrait' and (ab['width'] != 576 or ab['height'] != 864)):
            print(f"  Non-standard {ab['orientation']} AB {ab['index']}: {ab['width']}x{ab['height']} pt (Name: {ab['name']})")
