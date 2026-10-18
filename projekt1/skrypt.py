import csv

types = ['NUMBER(5) NOT NULL', 'VARCHAR(250)', 'NUMBER(4)', 'NUMBER(3)', 'NUMBER(4)']

with open('Publikacje.csv', 'r', encoding="utf-8") as src, \
     open('plik_do_zaladowania.sql', 'w', encoding="utf-8") as dest:
    
    reader = csv.reader(src)
    for i, words in enumerate(reader):
        # words są już oczyszczone ze znaków końca linii przez csv.reader
        if i == 0:
            columns_def = [f"{col.strip()} {t}" for col, t in zip(words, types)]
            dest.write(f"CREATE TABLE PUB({', '.join(columns_def)});\n")
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
            dest.write(f"INSERT INTO PUB VALUES ({', '.join(values)});\n")
            
    dest.write('SELECT * FROM PUB WHERE Rok = 2020 AND Punkty/Autorzy >= 100 ORDER BY Autorzy;\n')
    dest.write('DROP TABLE PUB;\n')