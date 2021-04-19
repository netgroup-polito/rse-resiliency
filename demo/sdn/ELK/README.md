Nella demo per analizzare i dati raccolti da packetbeat, rilevare l'attacco ICMP flood e richiamare il modulo di ONOS mediante chiamata HTTP sono stati utilizzati gli *Alert* e le *Action* di Kibana.
Per abilitarli è necessario impostare 3 proprietà di sicurezza, riassunte in questo [link](https://www.elastic.co/guide/en/kibana/7.12/alert-action-settings-kb.html).

Per quanto riguarda le prime due proprietà (*1. Set up Kibana to work with Elastic Stack security features*; *2. Set up TLS encryption between Kibana and Elasticsearch*) è gia disponibile una [guida](https://www.elastic.co/guide/en/elastic-stack-get-started/current/get-started-docker.html) (sezione *Run in Docker with TLS enabled*) su come impostarle con Docker-Compose.

Ciò però non è sufficiente: come terza proprietà bisogna specificare un valore di tipo stringa per il campo *xpack.encryptedSavedObjects .encryptionKey*. Come per la generazione di utenti built-in, Kibana offre un [tool](https://www.elastic.co/guide/en/kibana/7.x/kibana-encryption-keys.html) CLI per la creazione di questa stringa di 32 caratteri (entrare nel container che esegue Kibana e lanciare il comando). Questo valore viene stampato sulla console sullo standard output e una volta generato, copiare il valore sulla variabile di ambiente *XPACK_ENCRYPTEDSAVEDOBJECTS_ENCRYPTIONKEY* nel docker-compose (file *elastic-docker-tls.yml*) e riavviare i container.

A questo punto è possibile loggarsi da Kibana (porta 5601) utilizzanto l'utente built-in *elastic*.
