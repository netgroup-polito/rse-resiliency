Note importanti su tale deployment in versione 2:
- deployment dei containers applicativi nel network namespace del PDC (o PDCH); i servizi del DB (o DBH) e del mysql (o mysql) sono raggiungibili in localhost;
- un solo docker-compose per dispiegare i docker-container di servizi e applicativi;
- una sola immagine per l'esecuzione del docker-container DB (Logger) e del DBH; inoltre tali immagini comprendono pure un applicativo wait che viene eseguito         insieme all'applicativo DB (o DBH) affinchè questo aspetta di instaurare la connessione verso il mysql (o mysqlH) non appena esso è pronto ad accettarle;
- l'immagine del mysql è customizzata per creare lo schema al suo interno.
