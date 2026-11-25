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
SELECT ID, COALESCE(wynik_publikacyjny, 0) AS wynik_publikacyjny
FROM autorzy
LEFT JOIN
(
  SELECT autor, SUM(punkty_na_autora) AS wynik_publikacyjny
  FROM
  (
    SELECT 
      autor, 
      Punkty / autorzy AS punkty_na_autora, 
      ROW_NUMBER() OVER (PARTITION BY autor ORDER BY punkty / autorzy DESC) AS nr
    FROM autorstwo
    JOIN prace
    ON Praca = ID
  )
  WHERE nr <= 4
  GROUP BY autor
)
ON ID = autor
ORDER BY wynik_publikacyjny DESC
;
'''
)
    
