Note importanti su tale deployment:
- deployment dei containers applicativi come container differenti insistenti sulla stessa network virtuale (non sono in localhost);
- 2 differenti docker-compose (apps, services);
- 2 differenti immagini per l'esecuzione del docker-container DB (Logger) per differenziare le connessioni verso mysql e mysqlH;
- script per inizializzare i DBMS mysql e mysqlH.
