Una volta eseguito il container con ONOS, per replicare la demo è necessario caricare i moduli built-in *OpenFlow Provider Suite* e *Reactive Forwarding*. Questo è possibile 
utilizzando la GUI di ONOS, raggiungibile all'URL *<ip_address>:8181/onos/ui/#/app* come mostrato dall'immagine sottostante:

![](../images/ONOS%20fwd%20module.png)

Successivamente caricare il modulo custom per isolare il nodo (contenuto nella cartella *foo-app*). Entrare quindi nella bash shell del container, nella cartella /bin di onos ed eseguire il comando:

**~/onos/bin# ./onos-app -u onos -p rocks localhost install! /foo-app/target/foo-app-1.0-SNAPSHOT.oar**
