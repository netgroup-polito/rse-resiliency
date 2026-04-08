### Installazione (versione 20.04 di Ubuntu)

CORE fornisce uno script per automatizzare l'installazione dell'ambiente virtuale. Il processo di installazione automatico è indicato al seguente [link](https://coreemu.github.io/core/install.html#automated-install). In breve i comandi da eseguire sono:
* git clone https://github.com/coreemu/core.git
*  cd core
* ./install.sh 

Dopo che l'installazione è avvenuta con successo si dovrebbe essere in grado di eseguire core-daemon e core-pygui. 

### core-daemon 

Il demone core può essere avviato direttamente da command line, utile per vedere i log generati: **sudo core-daemon --ovs**. Il flag *--ovs* permette di creare tutti gli switch Ethernet istanziati sull'ambiente CORE usando openvswitch, eseguito non nel contesto del singolo nodo. Questo significa che nella macchina host su cui è eseguito CORE è possibile vedere tutte le interfacce che definiscono la rete. Per interconnettere le interfacce dei nodi vengono utilizzate coppie di *veth*.
Installazione diretta di openvswitch:
* sudo apt update
* sudo apt upgrade
* sudo apt install openvswitch-switch

Si ha in dotazione *ovs-vsctl*, l'utility che permette di aggiornare ed interrogare il demone che implementa lo switch ovs (*ovs-vswitchd*). Utilizzando il comando **ovs-vsctl show** si ha una overview del contenuto del database di ovs, che mostra i bridge creati, di solito denominati con il prefisso *b.* seguiti da una notazione decimale puntata. Potenzialmente tutti i bridge listati possono essere connessi al controller ONOS. Il protocollo OpenFlow non è abilitato di default e per configurare un bridge (e.g b.1.2) per supportare le versioni del protocollo è necessario lanciare il comando **ovs-vsctl set bridge b.1.2 protocols=OpenFlow10,OpenFlow12,OpenFlow13,OpenFlow14,OpenFlow15** (in questo modo si abilitano tutte e 5 le versioni del protocollo). A questo punto basterà specificare il controller responsabile della configurazione dello switch: **ovs-vsctl set-controller b.1.2 tcp:localhost:6653** (supponendo che il controller SDN sia eseguito sulla stessa macchina host di CORE e la porta su cui è in ascolto OF è la default 6653).

### core-pygui

Per la GUI di CORE si utilizza la versione BETA Python GUI e non la standard. Essa viene eseguita scrivendo da shell **core-pygui** (la GUI non necessita di essere eseguita come root) e si presenta in questo modo:

![](../images/CORE%20GUI.png)


I nodi, raffigurati dalle icone a destra della GUI nella toolbar, sono instanziati selezionandoli e trascinandoli sulla sfondo bianco. Il nodo Switch è situato nella sezione *Link Layer Nodes* e rappresentato da un'icona quadrata verde:

![](../images/Toolbar%20GUI%20CORE.png)

Una volta effettuato il drag-and-drop del nodo, avviare l'emulazione cliccando con il mouse la freccia verde in alto sulla toolbar. Infine, Il nodo Switch può essere configurato usando lo script *core.sh*.
