# Setup DEMO

## Configurazione Virtual Machine

Per la demo sono state utilizzate 4 VM VirtualBox: una esegue Elasticsearch/Kibana, un'altra per eseguire il controller SDN ONOS, una terza che instanzia lo switch emulato usando CORE e l'ultima per i container delle PMU/PDC.

I vari servizi comunicano tra di loro mediante lo switch emulato in CORE, e per connettere le VM allo switch sono state create 3 reti con NAT (192.168.101.0/24) con il DHCP inizialmente abilitato (per permettere di effettuare il build delle immagini Docker e configurare l'ambiente di esecuzione delle VM). 

![](images/VM%20Network%20setup.png)

Successivamente questo è stato disabilitato e l'assegnazione degli indirizzi IPV4 è avvenuta staticamente:

* VM ONOS IP Address 192.168.101.5, a cui è assegnata la rete con NAT *CORENetwork*
* VM Elasticsearch/Kibana IP Address 192.168.101.7, a cui è assegnata la rete con NAT *CORENetwork_1*
* VM PMU/PDC IP Address 192.168.101.8, a cui è assegnata la rete con NAT *CORENetwork_2*
* La VM con CORE Emulator non ha nessun IP Address assegnato staticamente. Questo viene assegnato allo switch emulato per connettersi con il controller SDN (vedere lo script *core/core.sh*). A questa VM sono assegnate tutte e 3 le reti create.

#### Importante: abilitare la modalità promiscua sulle schede di rete, sia nelle Impostazioni di VirtualBox sia internamente al SO con il comando ip link set <interface_name> promisc on

## Riprodurre la DEMO

Per riprodurre la demo si consiglia di eseguire i passi nel seguente ordine:

1. Eseguire ONOS (vedere cartella *onos*)
2. Emulare lo switch con CORE (vedere cartella *core*)
3. Eseguire Elasticsearch/Kibana (vedere cartella *ELK*)
4. Eseguire le PMU/PDC (vedere cartella *pmu-pdc* e *fog*)


## Limiti della demo e problemi irrisolti

1. L'attacco ICMP flood da parte della PMU verso la PDC è fittizio: le PMU/PDC sono eseguite in container Docker e visto l'isolamento i pacchetti ICMP non arrivano al servizio target. I dati di monitoraggio prodotti da packetbeat dalla PMU arrivano invece correttamente ad Elasticsearch;
2. ONOS rileva lo switch con gli indirizzi MAC delle interfacce dello switch emulato in CORE, e non gli indirizzi MAC virtuali delle PMU/PDC: packetbeat invia ad Elasticsearch l'indirizzo MAC virtuale dei container e non quello della VM. Per isolare quindi il nodo (la VM che esegue la PMU) si è dato per scontato quale fosse l'indirizzo MAC dela VM da isolare, scrivendolo staticamente nella action dell'alert di Kibana (non è quindi parametrizzato).
3. Le PMU/PDC sono eseguite sulla stessa VM. Isolando la VM che esegue la PMU "malevola", si isolano tutti i container che quindi non riescono più a inviare i loro dati di monitoraggio ad Elasticsearch e in generale a comunicare esternamente.





