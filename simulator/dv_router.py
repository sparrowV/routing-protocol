"""
Your awesome Distance Vector router for CS 168
"""


import sim.api as api
import sim.basics as basics
import time


# We define infinity as a distance of 16.
INFINITY = 16


class DVRouter (basics.DVRouterBase):
  #NO_LOG = True # Set to True on an instance to disable its logging
  POISON_MODE = True # Can override POISON_MODE here
  #DEFAULT_TIMER_INTERVAL = 5 # Can override this yourself for testing

  def __init__ (self):
    """
    Called when the instance is initialized.

    You probably want to do some additional initialization here.
    """

    self.ports_info = {}

    #table entry -> "desttination":(port,cost,time_to_expire)
    self.table = {}
    self.start_timer() # Starts calling handle_timer() at correct rate

  def handle_link_up (self, port, latency):
    """
    Called by the framework when a link attached to this Entity goes up.

    The port attached to the link and the link latency are passed in.
    """
    self.ports_info[port] = latency

  def handle_link_down (self, port):
    """
    Called by the framework when a link attached to this Entity does down.

    The port number used by the link is passed in.
    """

    del self.ports_info[port]

    nodes_to_delete  = []
    for dst in self.table.keys():
        dst_info = self.table[dst]
        if(port == dst_info[0]):
            #change my cost to infinity

            nodes_to_delete.append(dst)
            if(self.POISON_MODE):
                #iterate over all ports except given port and send infinitu to neighbours
                for my_port in self.ports_info:
                    if(port != my_port):
                        r_packet = basics.RoutePacket(dst, INFINITY)
                        self.send(r_packet, my_port)

    for node in nodes_to_delete:
        del self.table[node]

  def handle_rx (self, packet, port):

    """
    Called by the framework when this Entity receives a packet.
    packet is a Packet (or subclass).
    port is the port number it arrived on.

    You definitely want to fill this in.
    """
    #self.log("RX %s on %s (%s)", packet, port, api.current_time())

   # print("in hangle_rx , router# = ",self.counter)
  #  print("table before",self.table)
    if isinstance(packet, basics.RoutePacket):

        if(packet.destination not in self.table.keys()):
           # if(self.counter <=1):
             #print("packet dest not in table",packet.destination)

            self.table[packet.destination] = (port, self.ports_info[port] + packet.latency, time.time(),True)
            self.send_updated_route_to_neighbours(packet.destination, self.ports_info[port] + packet.latency, port)
        else:
            destination_info = self.table[packet.destination]
            if(self.ports_info[port] + packet.latency < destination_info[1]):

         #       print("shorte way")
                self.table[packet.destination] = (port,self.ports_info[port] + packet.latency,time.time(),True)
                self.send_updated_route_to_neighbours(packet.destination,self.ports_info[port] + packet.latency,port)


            #if update came to port which is the same port as best routing for destionation still update
            elif(destination_info[0] == port):
                self.table[packet.destination] = (port, self.ports_info[port] + packet.latency, time.time(),True)
                self.send_updated_route_to_neighbours(packet.destination, self.ports_info[port] + packet.latency, port)

    elif isinstance(packet, basics.HostDiscoveryPacket):
        self.table[packet.src] = (port,self.ports_info[port],time.time(),False)
        self.send_updated_route_to_neighbours(packet.src, self.ports_info[port], port)


    else:
      # Totally wrong behavior for the sake of demonstration only: send
      # the packet back to where it came from!
      #self.send(packet, port=
      if(packet.dst in self.table.keys() and self.table[packet.dst][1] <INFINITY):
         # print("yeah!!\n",packet.dst)

          self.send(packet,port = self.table[packet.dst][0])



         # print("talbe after", self.table)

  def send_updated_route_to_neighbours(self,destination,latency,input_port):
      #should i send update to neighbour from where it came from?
      for port in self.ports_info.keys():
          if(port !=input_port):
              r_packet = basics.RoutePacket(destination,latency)
              self.send(r_packet,port)


  def handle_timer (self):
    """
    Called periodically.

    When called, your router should send tables to neighbors.  It also might
    not be a bad place to check for whether any entries have expired.
    """
   # if(self.counter <=1):
       # print("in handle_timer router",self.counter)
       # print("table ",self.table)
    nodes_to_delete_for_timeout = []
    for dest in self.table.keys():
        for port in self.ports_info.keys():
            time_now = time.time()
            dest_info = self.table[dest]
            if( (time_now - dest_info[2]) > 15 and dest_info[3] == True):

                if(dest not in nodes_to_delete_for_timeout):
                 nodes_to_delete_for_timeout.append(dest)
            else:
                r_packet = basics.RoutePacket(dest,dest_info[1])
                self.send(r_packet, port)

    #not delete nodes for timeout
    for node in nodes_to_delete_for_timeout:
       # print("expired", node)

        del self.table[node]