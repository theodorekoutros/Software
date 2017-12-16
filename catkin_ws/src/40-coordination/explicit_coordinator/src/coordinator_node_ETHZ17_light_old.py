#!/usr/bin/env python
from __future__ import print_function
from random import random
import rospy
from duckietown_msgs.msg import CoordinationClearance, FSMState, BoolStamped, Twist2DStamped
from duckietown_msgs.msg import SignalsDetection, CoordinationSignal
from std_msgs.msg import String
from time import time

UNKNOWN = 'UNKNOWN'

class State:
    LANE_FOLLOWING = 'LANE_FOLLOWING'
    AT_STOP_CLEARING = 'AT_STOP_CLEARING'
    SACRIFICE = 'SACRIFICE'
    SOLVING_UNKNOWN = 'SOLVING_UNKNOWN'
    GO = 'GO'
    KEEP_CALM = 'KEEP_CALM'	
    TL_SENSING = 'TL_SENSING'
    INTERSECTION_NAVIGATION = 'INTERSECTION_NAVIGATION'

class VehicleCoordinator():
    """The Vehicle Coordination Module for Duckiebot"""

    T_MAX_RANDOM = 4.0 # seconds
    T_CROSS = 6.0      # seconds
    T_SENSE = 2.0      # seconds
    T_UNKNOWN = 1.0    # seconds
    T_MIN_RANDOM = 1.0 # seconds

# We communicate that the coordination mode has started
    def __init__(self):
        rospy.loginfo('The Coordination Mode has Started')

# Determine the state of the bot
        self.state = State.AT_STOP_CLEARING
        self.last_state_transition = time()
        self.random_delay = 0

        self.intersection_go_published = False

        self.node = rospy.init_node('veh_coordinator', anonymous=True)

        # Parameters

	# Are we in a situation with traffic lights? Initially always false.

        if rospy.get_param("~intersectionType") == "trafficLight":
            self.traffic_light_intersection = True
        else:
            self.traffic_light_intersection = False

        rospy.loginfo('[simple_coordination_node]: trafficLight=%s' % str(self.traffic_light_intersection))

        # Subscriptions

        self.mode = 'LANE_FOLLOWING'
        rospy.Subscriber('~mode', FSMState, lambda msg: self.set('mode', msg.state))

        self.traffic_light = UNKNOWN

	# Do we detect a vehicle?

   	self.right_veh = UNKNOWN
        self.opposite_veh = UNKNOWN
	# self.veh_detected = UNKNOWN

	# Initializing the unknown presence of a car
	#self.detected_car = UNKNOWN
        rospy.Subscriber('~signals_detection', SignalsDetection, self.process_signals_detection) # see below for the def. of process_signals_detection

        # Publishing
        self.clearance_to_go = CoordinationClearance.NA
	# state of the clearance
        self.clearance_to_go_pub = rospy.Publisher('~clearance_to_go', CoordinationClearance, queue_size=10)
	# signal for the intersection
        self.pub_intersection_go = rospy.Publisher('~intersection_go', BoolStamped, queue_size=1)
        self.pub_coord_cmd = rospy.Publisher('~car_cmd', Twist2DStamped, queue_size=1)

	# set the light to be off
        self.roof_light = CoordinationSignal.OFF
	# publish that
        self.roof_light_pub = rospy.Publisher('~change_color_pattern', String, queue_size=10)
        self.coordination_state_pub = rospy.Publisher('~coordination_state', String, queue_size=10)

        while not rospy.is_shutdown():
            self.loop()
            rospy.sleep(0.1)

#############################################################################################################
    def set_state(self, state):

	# update only when changing state
        if self.state != state:
            self.last_state_transition = time()
	self.state = state

        if self.state == State.AT_STOP_CLEARING:
   	   # self.reset_signals_detection()
           self.roof_light = CoordinationSignal.SIGNAL_A

	   #after setting everything to unknown, we turn on the light
	    #self.roof_light = CoordinationSignal.ON
	   #self.roof_light = CoordinationSignal.ON	
           #self.roof_light = CoordinationSignal.SIGNAL_A
        #elif self.state == State.RESERVING:
            #self.roof_light = CoordinationSignal.SIGNAL_B
        elif self.state == State.SACRIFICE:
            #self.roof_light = CoordinationSignal.SIGNAL_A
	    self.roof_light = CoordinationSignal.OFF
        elif self.state == State.KEEP_CALM:
	     self.roof_light = CoordinationSignal.SIGNAL_A	
        elif self.state == State.GO and not self.traffic_light_intersection:
            #self.roof_light = CoordinationSignal.ON
	     self.roof_light = CoordinationSignal.SIGNAL_A

	    # self.random_delay = 5
            # while self.time_at_current_state() < self.random_delay:
	    #    continue
       # else:
           # self.roof_light = CoordinationSignal.OFF

       # if self.state == State.GO:
	#	print(self.time_at_current_state())
	#	if self.time_at_current_state() > 5:
	#		self.clearance_to_go = CoordinationClearance.GO
       # else:
       #     self.clearance_to_go = CoordinationClearance.WAIT

        rospy.logdebug('[coordination_node_ETHZ17] Transitioned to state' + self.state)
#################################################################################################################
	
    # Define the time at this current state
    def time_at_current_state(self):
        return time() - self.last_state_transition

    def set(self, name, value):
        self.__dict__[name] = value

    # Definition of each signal detection
    def process_signals_detection(self, msg):
        self.set('traffic_light', msg.traffic_light_state)
        self.set('right_veh', msg.right)
        self.set('opposite_veh', msg.front)
	#self.set('veh_detected', msg.led_detected)
	#self.set('veh_not_detected',msg.no_led_detected)

    # definition which resets everything we know
    def reset_signals_detection(self):
        self.traffic_light = UNKNOWN
        self.right_veh = UNKNOWN
        self.opposite_veh = UNKNOWN
	#self.veh_detected = UNKNOWN
	#self.veh_not_detected = UNKNOWN

    # publishing the topics
    def publish_topics(self):
        now = rospy.Time.now()
        self.clearance_to_go_pub.publish(CoordinationClearance(status=self.clearance_to_go))
        # Publish intersection_go flag
        if (self.clearance_to_go == CoordinationClearance.GO):
            msg = BoolStamped()
            msg.header.stamp = now
            msg.data = True
            self.pub_intersection_go.publish(msg)
            # TODO: publish intersection go only once.
        self.roof_light_pub.publish(self.roof_light)

        car_cmd_msg = Twist2DStamped(v=0.0,omega=0.0)
        car_cmd_msg.header.stamp = now
        self.pub_coord_cmd.publish(car_cmd_msg)
        self.coordination_state_pub.publish(data=self.state)

    # definition of the loop
    def loop(self):
	#print(self.time_at_current_state())
        self.reconsider()
        self.publish_topics()

    def reconsider(self):
        if self.state == State.LANE_FOLLOWING:
            if self.mode == 'COORDINATION':
                self.reset_signals_detection()
                if self.traffic_light_intersection:
                    self.set_state(State.TL_SENSING)
                else:
		    # our standard case: setting at stop clearing!
                    self.set_state(State.AT_STOP_CLEARING)

        elif self.state == State.AT_STOP_CLEARING:
            #if self.right_veh != SignalsDetection.NO_CAR or self.opposite_veh == SignalsDetection.SIGNAL_B or self.opposite_veh == SignalsDetection.SIGNAL_C:
	    print(self.right_veh)
	    print(self.opposite_veh)
	    if self.right_veh == UNKNOWN or self.opposite_veh == UNKNOWN: #if first measurement not seen yet 
                self.roof_light = CoordinationSignal.OFF
	        self.random_delay = 1+random() * self.T_UNKNOWN
	        self.set_state(State.SOLVING_UNKNOWN)
            elif self.right_veh == SignalsDetection.SIGNAL_A or self.opposite_veh == SignalsDetection.SIGNAL_A:  # if we are seeing other cars (i.e. we cannot go)
		self.roof_light = CoordinationSignal.OFF
 		self.random_delay = self.T_MIN_RANDOM + random() * self.T_MAX_RANDOM
 		print ("Other vehicle are waiting as well. Will wait for %.2f s" % self.random_delay)	
                self.set_state(State.SACRIFICE)
            
           # elif self.time_at_current_state() > self.T_CROSS + self.T_SENSE:
            #    self.set_state(State.AT_STOP_CLEAR)

       # elif self.state == State.AT_STOP_CLEAR:
            #if self.right_veh != SignalsDetection.NO_CAR or self.opposite_veh == SignalsDetection.SIGNAL_B or self.opposite_veh == SignalsDetection.SIGNAL_C:
 	#    if self.veh_detected == SignalsDetection.CARS:  # if we are seeing other cars (i.e. we cannot go)
         #       self.set_state(State.AT_STOP_CLEARING)
            else:
                 self.set_state(State.KEEP_CALM)

        #elif self.state == State.RESERVING:
          #  if self.right_veh != SignalsDetection.NO_CAR:
           #     self.set_state(State.AT_STOP_CLEARING)
           # elif self.time_at_current_state() > 2 * self.T_SENSE:
            #    if self.opposite_veh == SignalsDetection.SIGNAL_B:
             #       self.random_delay = random() * self.T_MAX_RANDOM
              #      print ("Other vehicle reserving as well. Will wait for %.2f s" % self.random_delay)
               #     self.set_state(State.SACRIFICE)
               # else:
                #    self.set_state(State.GO)

        elif self.state == State.GO:
	#    self.set_state(State.KEEP_CALM)
       # elif self.state == State.KEEP_CALM:
		print(self.time_at_current_state())
               	if self.time_at_current_state() > 5:
			self.clearance_to_go = CoordinationClearance.GO
           # if self.time_at_current_state() > 5 and self.mode == 'LANE_FOLLOWING':
			if self.mode == 'LANE_FOLLOWING': 	
				self.set_state(State.LANE_FOLLOWING)

        elif self.state == State.SACRIFICE:
            #if self.right_veh != SignalsDetection.NO_CAR or self.opposite_veh == SignalsDetection.SIGNAL_B or self.opposite_veh == SignalsDetection.SIGNAL_C:
               # self.set_state(State.AT_STOP_CLEARING)
            if self.time_at_current_state() > self.random_delay:
                self.set_state(State.AT_STOP_CLEARING) #changed from CLEAR to CLEARING

	elif self.state == State.KEEP_CALM:
		if self.right_veh == SignalsDetection.SIGNAL_A or self.opposite_veh == SignalsDetection.SIGNAL_A:
			self.roof_light = CoordinationSignal.OFF
			self.set_state(State.SACRIFICE)
		else:
			self.set_state(State.GO)

        elif self.state == State.SOLVING_UNKNOWN:
            if self.time_at_current_state() > self.random_delay:
                self.set_state(State.AT_STOP_CLEARING) #changed from CLEAR to CLEARING

        elif self.state == State.TL_SENSING:
            if self.traffic_light == SignalsDetection.GO:
                self.set_state(State.GO)
	
	
	if self.state != State.GO:
		self.clearance_to_go = CoordinationClearance.WAIT

if __name__ == '__main__':
    car = VehicleCoordinator()
    rospy.spin()
