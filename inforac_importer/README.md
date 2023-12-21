# InfoRac importer

### Funzionamento script

Come definito nei requisiti e nelle minute, lo script `inforac_importer.py` funziona come segue:

1. Cicla su tutti i file `.xlsx` presenti nella cartella di input fornita allo script

1. Per ogni file `xlsx` crea una nuova riga nella tabella dei log chiamata `inforac_importer_log` salvata nel db `infomapnode`
    1. Se il file non è mai stato processato, crea una nuova riga e prosegue
    2. Se il file è già stato processato in passato, ma ha una data di ultima modifica più recente rispetto alla data di processamento, l'importazione viene rieseguita resettandone status e data
1. Estrae da un file di configurazione definito per ogni standard. Nel file di configurazione sono salvati:
    1. sheet name da dove estrarre i dati
    1. nomi delle colonne geometriche
    1. colonne da estrarre nei file
1. Utilizzando `pandas` viene letto il file `xlsx`, estratti i dati delle colonne necessarie.
1. Il country code estratto viene convertito da codice a nome
1. i campi di `lat/long` vengono convertiti in un `GeoDataframe` così da rendere più ottimizzata la scrittura su `PostGis`

**NOTA**: Nelle configurazioni è possible estrarre dati da più `sheet` del file excel. Lo script ciclerà su tutti i nomi definiti nelle configurazioni ed estrarrà i dati. I dati finiranno nello stesso dataframe.

7. Se nessun errore viene sollevato dallo script, vengono rimosse le eventuali righe duplicate e il tutto viene salvato dentro `PostGis`

**NOTA:** Le operazioni sopra descritte dal punto 2 al punto 7 vengono rieseguite per ogni singolo file `xlsx` presente nella cartella di input ed eventuali errori vengono scritti sia a terminale che nella tabella di log `inforac_importer_log`

### Come eseguirlo

Lo script viene proposto come un servizio all'interno del `docker-compose.yaml` già presente nel repository.

#### Step 1: Build delle immagini:
```
docker-compose build
```

#### Step 2: Up del docker-compose
```
docker-compose up
```

**NOTA**: se il servizio del DB non dovesse funzionare, il container di `inforac_importer` non partirà

### Step 3 manual operation

Lo script necessita della creazione della tabella `inforac_importer_log` nel db `infomapnode`
Di base viene creata automaticamente dallo script stesso se non esiste. Nel caso in cui si voglia creare manualmente
Di seguito il DLL necessario per la creazione:

```
CREATE TABLE public.inforac_importer_log (
	id serial4 NOT NULL,
	processed_file varchar(250) NOT NULL,
	import_date_time timestamptz NOT NULL,
	successful bool NULL,
	logs text NULL,
	CONSTRAINT inforac_importer_log_pkey PRIMARY KEY (id)
);
GRANT ALL ON ALL TABLES IN SCHEMA public TO infomapnode;
GRANT USAGE, SELECT ON SEQUENCE inforac_importer_log_id_seq TO infomapnode;

```


#### Step 4: Eseguire il file da dentro il container

**NOTA:** lo script andrà eseguito tramite un servizio CRON che verrà gestito dal cliente finale direttamente. Di seguito viene spiegato come eseguire manualmente lo script

```
➜ docker exec -it inforac4infomapnode bash
➜ python /usr/src/inforac_importer/inforac_importer.py <path_to_xlsx_files> --no-input
```

