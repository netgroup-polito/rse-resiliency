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

import com.fasterxml.jackson.databind.node.ObjectNode;
import org.onlab.packet.MacAddress;
import org.onosproject.cli.AbstractShellCommand;
import org.onosproject.core.ApplicationId;
import org.onosproject.core.CoreService;
import org.onosproject.net.DeviceId;
import org.onosproject.net.Host;
import org.onosproject.net.HostId;
import org.onosproject.net.device.DeviceService;
import org.onosproject.net.flow.DefaultTrafficSelector;
import org.onosproject.net.flow.DefaultTrafficTreatment;
import org.onosproject.net.flow.TrafficSelector;
import org.onosproject.net.flow.TrafficTreatment;
import org.onosproject.net.flowobjective.DefaultForwardingObjective;
import org.onosproject.net.flowobjective.FlowObjectiveService;
import org.onosproject.net.flowobjective.ForwardingObjective;
import org.onosproject.net.host.HostService;
import org.onosproject.rest.AbstractWebResource;
import org.osgi.service.component.annotations.Reference;
import org.osgi.service.component.annotations.ReferenceCardinality;
import org.slf4j.Logger;

import javax.ws.rs.*;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;


import static com.google.common.base.Preconditions.checkArgument;
import static com.google.common.base.Preconditions.checkNotNull;
import static org.foo.app.OsgiPropertyConstant.OsgiPropertyConstants.FLOW_PRIORITY_DEFAULT;
import static org.slf4j.LoggerFactory.getLogger;

/**
 * Sample web resource.
 */
@Path("use-case-1")
public class AppWebResource extends AbstractWebResource {

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

    private static final String NO_SEP_SPECIFIED =
            "Connect point not specified, Connect point must be in \"deviceUri/portNumber\" format";

    /*
     * Isolate the specified host mac address.
     *
     * @param host mac
     * @return status of the request - CREATED if the JSON is correct,
     * BAD_REQUEST if the JSON is invalid
     */

    @PUT
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    @Path("")
    public Response IsolateHost(@QueryParam("mac") String mac) {
        if (mac == null) {
            throw new WebApplicationException(
                    Response.status(Response.Status.BAD_REQUEST)
                            .entity("name parameter is mandatory")
                            .build()
            );
        }
        this.deviceService = AbstractShellCommand.get(DeviceService.class);
        this.coreService = AbstractShellCommand.get(CoreService.class);
        this.flowObjectiveService = AbstractShellCommand.get(FlowObjectiveService.class);
        this.hostService = AbstractShellCommand.get(HostService.class);
        appId = coreService.registerApplication("org.foo.app");

        //this.hostService.getHostsByMac(MacAddress.valueOf(mac));
        HostId oneId = HostId.hostId(mac);
        System.out.println(oneId.mac().toString());
        TrafficSelector.Builder selectorBuilder = DefaultTrafficSelector.builder().matchEthSrc(oneId.mac());

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

        return Response.ok().build();
    }

    /**
     * Get hello world greeting.
     *
     * @return 200 OK
     */
    @GET
    @Path("")
    public Response getGreeting() {
        ObjectNode node = mapper().createObjectNode().put("hello", "world");
        return ok(node).build();
    }

}
