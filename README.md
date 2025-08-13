
<h1>RiskGuard (en)</h1>

<p>Download and view climate datasets from <strong>Copernicus</strong> 
and <strong>CMCC</strong> in QGIS, apply advanced geographic and temporal 
filters, and export the results as <strong>Mesh Layer</strong> and 
<strong>Raster Layer</strong>.</p>

<p><strong>Copernicus</strong></p>

<p>Register on Copernicus via the following link:</p>

<a href="https://accounts.ecmwf.int/auth/realms/ecmwf/login-actions/registration?client_id=cds&tab_id=kMxnQgWIUUc">ECMWF Account</a><br>

<p>All information on how to create the .cdsapirc file, obtain the URL and API key, and install the cdsapi libraries is available here:</p>

<a href="https://cds.climate.copernicus.eu/how-to-api">CDS API</a><br>

<p>In Copernicus, to download some datasets you must accept the terms &amp; conditions.</p>

<p>You can do this directly within the program before downloading the datasets, or directly from your profile:</p>

<a href="https://cds.climate.copernicus.eu/profile?tab=licences">Create Profile</a><br>

<img src="https://www.ilcorsaronero.it/tesi/img1.png"/>

***Note: 
<p><strong>IF QGIS does not recognize cdsapi</strong></p>

<p>1. Open the folder: C:\Program Files\QGIS 3.34.9</p>
<p>2. Click on OSGeo4W to open the terminal</p>
<p>3. Type the following command in the command prompt and press Enter:</p>
<p>pip install cdsapi</p>
<p>Now QGIS will correctly recognize the library.</p>


<h2>CMCC-DDS</h2>

<p>Register on CMCC-DDS via the following link:</p>

<a href="https://auth02.cmcc.it/realms/DDS/login-actions/registration?client_id=ddsweb&tab_id=STW6rvWfB2c&client_data=eyJydSI6Imh0dHBzOi8vZGRzLmNtY2MuaXQvPyIsInJ0IjoiY29kZSIsInJtIjoiZnJhZ21lbnQiLCJzdCI6IjhkZGY4N2Q5LTk5NmEtNGM4Zi05OTE2LTZhODI3NzVhMDJmYiJ9">Create Profile</a><br>

<p>To create the .ddsapirc configuration file, obtain the URL and API key, and install the ddsapi libraries, refer to the official guide:</p>

<a href="https://dds.cmcc.it/#/docs">Official Guide</a><br>

<h2>How it works</h2>

<p>The interface allows you to choose the <strong>endpoint</strong> from 
which to download datasets via two radio buttons at the top.</p>

<p>If you select Copernicus, the available categories will appear 
(e.g., Analysis, Climate Indices, etc.). </p>
<p>After choosing a category, the dropdown will populate with the list of available datasets, indicating the total number. (Img 1.1)
</p>

<img src="https://www.ilcorsaronero.it/tesi/img2.png"/>
<p><strong>Img 1.1</strong></p>

<h2>Next steps</h2>

<p><strong>Dataset selection</strong>: After the list is populated, choose a dataset. 
A dynamic structure will be generated containing all variables, temporal parameters, download format, etc.</p>

<p><strong>Download</strong>: After selecting the mandatory parameters, start the download by clicking on <strong>Submit</strong>.</p>

<p><strong>Monitoring in QGIS</strong>: In QGIS's Python console, you can monitor the download status (accepted, running, successful).</p>


<h2>Managing downloaded files:</h2>

<p>Once downloaded, the <strong>file name is dynamically generated</strong> 
based on the current date and time, ensuring unique identification.</p>

<p>The application supports various file formats, including <strong>ZIP, 
NetCDF (.nc), and GRIB</strong>.</p>

<p>If the downloaded file is a ZIP archive, it is automatically extracted into the <strong>Documents</strong> destination directory.</p>

<p>If the downloaded or extracted files are in NetCDF (.nc) or GRIB format, they are automatically loaded as layers in QGIS.</p>


<h2>Geographic selection interface:</h2>

<p>The <strong>GlobeMapForm</strong> graphical interface was developed 
to allow interactive geographic selection, helping the user identify and 
delimit the area of interest.</p>

<p><strong>Zoom and Panning</strong>: The interface includes two +/- buttons 
for zooming in and out. The map scale adapts based on the zoom to maintain high resolution.</p>

<p><strong>Rectangular Area Selection:</strong> By enabling the Draw Rectangle 
mode, the user can draw a rectangle to delimit the area.</p>

<p>When activated, the user can select the desired area by clicking on the map to mark the starting and ending points of the rectangle.</p>

<p>The selection is displayed with a red outline to ensure visibility and precision.</p>

<p><strong>Coordinate Output:</strong> Using the <strong>Save</strong> button, 
the coordinates are saved in the main panel.</p>

<img src="https://www.ilcorsaronero.it/tesi/img3.png"/>
<br><br>


<h1>RiskGuard (it)</h1>

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




