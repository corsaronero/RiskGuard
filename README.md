<h1>RiskGuard</h1>

<p>Scarica e visualizza dataset climatici di <strong>Copernicus</strong>
e <strong>CMCC</strong> in QGIS, applica filtri geografici e temporali
avanzati e esporta i risultati come <strong>Layer Mesh</strong> e
<strong>Layer Raster</strong>.</p>

<p><strong>Copernicus</strong></p>

<p>Registrati su Copernicus tramite il seguente link:</p>

<a href="https://accounts.ecmwf.int/auth/realms/ecmwf/login-actions/registration?client_id=cds&tab_id=kMxnQgWIUUc">Account ecmf</a><br>

<p>Tutte le informazioni su come creare il file .cdsapirc, ottenere l’URL e la chiave API, e installare le librerie cdsapi sono disponibili qui:</p>

<a href="https://cds.climate.copernicus.eu/how-to-api">CDS API</a><br>

<p>In Copernicus per effettuare il download di alcuni dataset bisogna
accettare i terms&amp;conditions.</p>

<p>Puoi farlo direttamente all’interno del programma prima di effettuare
il download dei dataset, oppure direttamente dal tuo profilo:</p>

<a href="https://cds.climate.copernicus.eu/profile?tab=licences">Crea Profilo</a><br>

<img src="https://www.ilcorsaronero.it/tesi/img1.png"/>

***Nota: 
<p><strong>SE QGIS non riconosce cdsapi</strong></p>

<p>1. Apri la cartella: C:\Program Files\QGIS 3.34.9</p>
<p>2. Clicca su OSGeo4W per aprire il terminale</p>
<p>3. Digita il seguente comando nel prompt dei comandi e premi
Invio:</p>
<p>pip install cdsapi</p>
<p>Ora QGIS riconoscerà correttamente la libreria.</p>


<h2>CMCC-DDS</h2>

<p>Registrati su CMCC-DDS tramite il seguente link:</p>

<a href="https://auth02.cmcc.it/realms/DDS/login-actions/registration?client_id=ddsweb&tab_id=STW6rvWfB2c&client_data=eyJydSI6Imh0dHBzOi8vZGRzLmNtY2MuaXQvPyIsInJ0IjoiY29kZSIsInJtIjoiZnJhZ21lbnQiLCJzdCI6IjhkZGY4N2Q5LTk5NmEtNGM4Zi05OTE2LTZhODI3NzVhMDJmYiJ9">Crea Profilo</a><br>

<p>Per creare il file di configurazione .ddsapirc, ottenere l’URL e la
chiave API, e installare le librerie ddsapi, consulta la guida
ufficiale:</p>

<a href="https://dds.cmcc.it/#/docs">Guida Ufficiale</a><br>

<h2>Funzionamento</h2>

<p>L’interfaccia permette di scegliere l’<strong>endpoint</strong> da
cui scaricare i dataset tramite due radio button nella parte
superiore.</p>

<p>Se selezioni Copernicus, appariranno le categorie disponibili
(es. Analysis, Climate Indices, etc.). </p>
<p>Dopo aver scelto una categoria, la dropdown si popolerà con
la lista dei dataset disponibili, indicando il numero totale. (Img 1.1)
</p>

<img src="https://www.ilcorsaronero.it/tesi/img2.png"/>
<p><strong>Img 1.1</strong></p>

<h2>Passaggi successivi</h2>

<p><strong>Selezione del dataset</strong>: Dopo aver popolato la lista,
scegli un dataset. verrà generata una struttura dinamica contenente
tutte le variabili, parametri temporali, formato download etc..</p>

<p><strong>Download</strong>: Dopo aver selezionato i parametri
obbligatori, avvia il download cliccando su <strong>Submit</strong>.</p>

<p><strong>Monitoraggio in QGIS</strong>: Nella console Python di QGIS
puoi monitorare lo stato del download (accepted, running,
successful).</p>


<h2>Gestione file scaricati:</h2>

<p>Effettuato il download, il <strong>nome del file viene generato
dinamicamente</strong> in base alla data e all'ora correnti, garantendo
un'identificazione univoca.</p>

<p>L’applicazione gestisce diversi formati di file, inclusi <strong>ZIP,
NetCDF(.nc) e GRIB </strong>.</p>

<p>Se il file scaricato è un archivio ZIP, viene automaticamente
estratto nella directory di destinazione <strong>Documents.</strong></p>

<p>Se i file scaricati o estratti sono in formato NetCDF (.nc) o GRIB,
vengono automaticamente caricati come layer in QGIS.</p>


<h2>Interfaccia per la selezione geografica:</h2>

<p>L’interfaccia grafica <strong>GlobeMapForm</strong> è stata
sviluppata per consentire una selezione geografica interattiva, aiutando
l'utente a identificare e delimitare l’area d'interesse.</p>

<p><strong>Zoom e Panning</strong>: L’interfaccia include due bottoni
+/- per lo zoom in e out. La scala della mappa si adatta in base allo
zoom per mantenere un'alta risoluzione.</p>

<p><strong>Selezione Rettangolare dell’Area: </strong>Attivando la
modalità Draw Rectangle, l’utente può disegnare un rettangolo
per delimitare l’area.</p>

<p>Quando viene attivata, l’utente può selezionare l’area desiderata
cliccando sulla mappa per segnare il punto di partenza e di fine del
rettangolo.</p>

<p>La selezione viene visualizzata con un contorno rosso per garantire
visibilità e precisione.</p>

<p><strong>Emissione delle Coordinate:</strong> Tramite il pulsante
<strong>Save</strong>, le coordinate vengono salvate nel pannello
principale.</p>

<img src="https://www.ilcorsaronero.it/tesi/img3.png"/>
<br><br>




