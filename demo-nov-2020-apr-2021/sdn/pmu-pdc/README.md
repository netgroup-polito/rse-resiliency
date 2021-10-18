I Dockerfile delle PMU/PDC sono gli stessi presenti nella sezione *fog*, con l'aggiunta dei tool per la generazione dei dati di monitoraggio (packetbeat) e per simulare l'attacco della PMU verso la PDC (hping).

L'unico fatto degno di nota è relativo al file packetbeat.yml: in questo file bisogna specificare come autenticarsi con Elasticsearch per inviare i dati di monitoraggio, dato che sono state abilitate delle proprietà di sicurezza per abilitare gli Alert in Kibana.

Esempio: nella cartella PMU, nel file packetbeat.yml sono presenti i campi:
* username: "elastic" 
* password: "tSsopuYRy2sevCd5fuKM"
* ssl.verification_mode: none

*elastic* rappresenta l'utente built-in generato nella sezione 1 nella cartella *ELK*; cambiare il campo *password* con il corrispondente valore generato in fase di creazione degli utenti built-in.
