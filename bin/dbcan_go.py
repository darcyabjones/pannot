
def parse_dbcan(handle):
    cols = [
        ('family'),
        ('domain'),
        ('class'),
        ('note'),
        ('activities'),
        ]
    fam_map = {
        'Cellulosome': 'Cellulosome',
        'GH': 'Glycoside Hydrolase',
        'GT': 'Glycosyl hydrolase',
        'PL': 'Polysaccharide lyase',
        'CE': 'Carbohydrate esterase',
        'AA': 'CAZyme auxiliary redox enzyme',
        'CBM': 'Carbohydrate-binding module',
        }
    db = defaultdict(dict)
    for line in handle:
        line = line.strip()
        if line.startswith('#'):
            continue
        line = line.split('\t')
        entry = dict()
        for col, val in zip(cols, line):
            entry[col] = val
        entry['class_longname'] = fam_map[entry['class']]
        db[entry['family']] = entry
    return db
