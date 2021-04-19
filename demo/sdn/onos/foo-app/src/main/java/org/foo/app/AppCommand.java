/*
 * Copyright 2020-present Open Networking Foundation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.foo.app;

import org.apache.karaf.shell.api.action.Argument;
import org.apache.karaf.shell.api.action.Command;
import org.apache.karaf.shell.api.action.Completion;
import org.apache.karaf.shell.api.action.lifecycle.Service;
import org.apache.karaf.shell.impl.action.command.ManagerImpl;
import org.onlab.packet.MacAddress;
import org.onosproject.cli.AbstractShellCommand;

import org.onosproject.cli.net.HostIdCompleter;
import org.onosproject.core.ApplicationId;
import org.onosproject.core.CoreService;
import org.onosproject.net.DeviceId;
import org.onosproject.net.Host;
import org.onosproject.net.HostId;
import org.onosproject.net.device.DeviceService;
import org.onosproject.net.Device;
//import org.onosproject.snmp.SnmpController;
//import org.onosproject.snmp.ctl.DefaultSnmpDevice;
//import org.onosproject.openflow.controller.OpenFlowController;
//import org.onosproject.openflow.controller.OpenFlowSwitch;

import org.onosproject.net.flow.DefaultTrafficSelector;
import org.onosproject.net.flow.DefaultTrafficTreatment;
import org.onosproject.net.flow.TrafficSelector;
import org.onosproject.net.flow.TrafficTreatment;
import org.onosproject.net.flowobjective.DefaultForwardingObjective;
import org.onosproject.net.flowobjective.FlowObjectiveService;
import org.onosproject.net.flowobjective.ForwardingObjective;
import org.onosproject.net.host.HostService;
import org.onosproject.net.link.LinkService;
import org.slf4j.Logger;
import static org.slf4j.LoggerFactory.getLogger;
import org.osgi.service.component.annotations.Reference;
import org.osgi.service.component.annotations.ReferenceCardinality;
import static org.foo.app.OsgiPropertyConstant.OsgiPropertyConstants.FLOW_PRIORITY;
import static org.foo.app.OsgiPropertyConstant.OsgiPropertyConstants.FLOW_PRIORITY_DEFAULT;
import static com.google.common.base.Preconditions.checkNotNull;
import static com.google.common.base.Preconditions.checkArgument;


/**
 * Sample Apache Karaf CLI command
 */
@Service
@Command(scope = "onos", name = "use-case-1",
         description = "Sample Apache Karaf CLI command for isolating a host node")
public class AppCommand extends AbstractShellCommand {

    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    protected DeviceService deviceService;
    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    protected CoreService coreService;
    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    protected FlowObjectiveService flowObjectiveService;
    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    protected HostService hostService;
    private final Logger log = getLogger(getClass());
    /** Configure Flow Priority for installed flow rules; default is 10. */
    private int flowPriority = FLOW_PRIORITY_DEFAULT*10+10;
    private ApplicationId appId;
    /*@Reference(cardinality = ReferenceCardinality.MANDATORY)
    protected OpenFlowController controller;*/
    @Argument(index = 0, name = "one", description = "One host ID",
            required = true, multiValued = false)
    @Completion(HostIdCompleter.class)
    String one = null;

    private static final String NO_SEP_SPECIFIED =
            "Connect point not specified, Connect point must be in \"deviceUri/portNumber\" format";


    @Override
    protected void doExecute() {
        this.deviceService = AbstractShellCommand.get(DeviceService.class);
        this.coreService = AbstractShellCommand.get(CoreService.class);
        this.flowObjectiveService = AbstractShellCommand.get(FlowObjectiveService.class);
        this.hostService = AbstractShellCommand.get(HostService.class);
        //TrafficSelector.Builder selectorBuilder = DefaultTrafficSelector.builder();
        appId = coreService.registerApplication("org.foo.app");
        //this.controller = AbstractShellCommand.get(OpenFlowController.class);
        //DefaultSnmpDevice snmpDevice;
        //SnmpController snmpController = AbstractShellCommand.get(SnmpController.class);
        //snmpController.getDevices().forEach(d->System.out.println("Snmp id: "+d.deviceId()));
        HostId oneId = HostId.hostId(one);
        System.out.println(oneId.mac().toString());
        TrafficSelector.Builder selectorBuilder = DefaultTrafficSelector.builder().matchEthSrc(oneId.mac());
        Iterable<Device> devices = deviceService.getDevices();
        /*for (OpenFlowSwitch sw : controller.getSwitches()) {
            print("Sono qui");
        }*/
        TrafficTreatment treatment = DefaultTrafficTreatment.builder().drop()
                .build();
        ForwardingObjective forwardingObjective = DefaultForwardingObjective.builder()
                .withSelector(selectorBuilder.build())
                .withTreatment(treatment)
                .withPriority(flowPriority)
                .withFlag(ForwardingObjective.Flag.VERSATILE)
                .fromApp(appId)
                .add();

        Host host = this.hostService.getHost(oneId);
        checkNotNull(host.location().toString());
        int idx = host.location().toString().lastIndexOf("/");
        checkArgument(idx != -1, NO_SEP_SPECIFIED);

        String stringId = host.location().toString().substring(0, idx);
        DeviceId deviceId = DeviceId.deviceId(stringId);
        flowObjectiveService.forward(deviceId,
                forwardingObjective);
    }
}
