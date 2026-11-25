import csv

files = {
    'Prace.csv': ['NUMBER(5) PRIMARY KEY', 'VARCHAR(250)', 'NUMBER(4)', 'NUMBER(3)', 'NUMBER(4)'],
    'Autorstwo.csv': ['NUMBER(5)', 'VARCHAR(30)'],
    'Autorzy.csv': ['VARCHAR(30) PRIMARY KEY', 'NUMBER(3)', 'VARCHAR(20)'],
}

with open('plik_do_zaladowania.sql', 'w', encoding="utf-8") as dest:
    for file, types in files.items():
        with open(file, 'r', encoding="utf-8") as src:
            table_name: str = file.split(sep='.')[0].lower()
            reader = csv.reader(src)
            for i, words in enumerate(reader):
                # words są już oczyszczone ze znaków końca linii przez csv.reader
                if i == 0:
                    columns_def = [f"{col.strip()} {t}" for col, t in zip(words, types)]
                    dest.write(f"CREATE TABLE {table_name}({', '.join(columns_def)});\n")
                else:
                    values = []
                    for word in words:
                        word = word.strip()
                        if word.isnumeric():
                            values.append(word)
                        else:
                            word = word.replace("&", "' || CHR(38) || '")
                            # escapowanie apostrofów w tekście na potrzeby SQL
                            escaped = word.replace("'", "''")
                            values.append(f"'{escaped}'")
                    dest.write(f"INSERT INTO {table_name} VALUES ({', '.join(values)});\n")
            
    dest.write(
'''
WITH edges AS (
  SELECT DISTINCT a.autor, b.autor AS wspolnik
  FROM autorstwo a
  JOIN autorstwo b ON a.praca = b.praca
  WHERE a.autor != b.autor
),
path (autor, poziom) AS (
  SELECT DISTINCT autor, 0 FROM autorstwo WHERE autor = 'Pilipczuk Mi'
  UNION ALL
  SELECT e.wspolnik, p.poziom + 1
  FROM path p
  JOIN edges e ON p.autor = e.autor
) CYCLE autor SET cycle_found TO 1 DEFAULT 0
SELECT a.id, MIN(poziom) AS poziom
FROM path
RIGHT JOIN autorzy a
ON a.id = path.autor
GROUP BY a.id
ORDER BY poziom
;

DROP TABLE autorstwo;
DROP TABLE autorzy;
DROP TABLE prace;
'''
)
    
