# -*- coding: utf-8 -*-

from __future__ import division

from psychopy import visual, core, event, gui, misc
import random
import math
import time


class TrackingObject():
        def __init__(self, is_target, window, tracking_area):
            self.is_target = is_target
            self.is_marked = False  # Objekt am Ende des Durchgangs als Target markiert
            self.tracking_area = tracking_area

            self.radius = 0.5
            self.innerradius=0.2
            outercircle = visual.Circle(win=window, radius=self.radius, fillColor=[1.0, 1.0, 1.0])
            self.shapes = [outercircle, outercircle]
            innercircle = visual.Circle(win=window, radius=self.innerradius, fillColor=[0.0, 0.0, 0.0])
            self.shapes+=[innercircle, innercircle]
            # Zufällige Startposition
            x = random.random() * (tracking_area[1] - tracking_area[0] - 4 * self.radius) + tracking_area[0] + (2*self.radius)  # random.randint(size, width-size)
            y = random.random() * (tracking_area[3] - tracking_area[2] - 2 * self.radius) + tracking_area[2] + self.radius  # random.randint(size, height-size)
            self.position = [x, y]

            start_direction = random.randrange(0, 360)
            radial_speed = 0.05  # ToDo: Hier Grad pro Frame, ändern in Grad pro Sekunde

            self.innerpos=[0,0]

            self.speed = [radial_speed*math.cos(math.radians(start_direction)),
                        radial_speed*math.sin(math.radians(start_direction))]

        def move(self):
            self._movement()
            self._boundaries()

        def draw(self):
            sc = lambda(x): (2*x)-1
            for i in range(2):
                self.shapes[i].setPos([self.position[0]+(sc(i)*self.radius), self.position[1]])
                self.shapes[i+2].setPos([self.position[0]+(sc(i)*self.radius)+self.innerpos[0], self.position[1]+self.innerpos[1]])
                self.shapes[i].draw()
                self.shapes[i+2].draw()



        def setColor(self, color):
            for s in self.shapes[:2]:
                s.setFillColor(color)
            #print ("setcolor")
            #print( self.shape.fillColor)

        def getDistToMouseIfHitByMouse(self, mouse):
             if mouse.isPressedIn(self.shapes[0]) or mouse.isPressedIn(self.shapes[1])  or mouse.isPressedIn(self.shapes[2])  or mouse.isPressedIn(self.shapes[3]):
                mouse_pos = mouse.getPos()
                #dist = ((mouse_pos[0] - self.shape.pos[0])**2 + (mouse_pos[1] - self.shape.pos[1])**2) ** 0.5
                dist = ((mouse_pos[0] - self.position[0])**2 + (mouse_pos[1] - self.position[1])**2) ** 0.5
                return (dist)
             else:
                return None

        def changeMarkedAsTargetState(self):
            self.is_marked = not self.is_marked
            if self.is_marked:
                self.setColor([1.0, -1.0, -1.0])
            else:
                self.setColor([1.0, 1.0, 1.0])

        def _movement(self):
            #print("-- before move --")
            #print(self.move)
            #print(self.speed)
            self.position[0] += self.speed[0]
            self.position[1] += self.speed[1]

            newinnerpos = [self.innerpos[0] + 1.1*self.speed[0], self.innerpos[1] + 1.1*self.speed[1]]
            #Ideally want to move along circle somehow - co-ordinates from main velocity, match to circle co-ordinates
            #instead use trig - tan(theta)=o/a then get theta, use sin and cos to get back circle co-ords
            #see if straight line movement seems realistic or want motion across circle

            if ((-1*self.radius)+self.innerradius <= newinnerpos[0] <= self.radius - self.innerradius) and  ((-1*self.radius)+self.innerradius <= newinnerpos[1] <= self.radius - self.innerradius):
                    self.innerpos[0] += 1.05*self.speed[0]
                    self.innerpos[1] += 1.05*self.speed[1]
            elif ((-1*self.radius)+self.innerradius <= newinnerpos[0] <= self.radius - self.innerradius) and not ((-1*self.radius)+self.innerradius <= newinnerpos[1] <= self.radius - self.innerradius):
                    self.innerpos[0] += 1.05*self.speed[0]
            #elif not ((-1*self.radius)+self.innerradius <= newinnerpos[0] <= self.radius - self.innerradius) and ((-1*self.radius)+self.innerradius <= newinnerpos[1] <= self.radius - self.innerradius):
                    #self.innerpos[1] += 1.05*self.speed[1]
                    # get co-ordinates back from main velocity, find outermost co-ordinates of circle which match this

        def _boundaries(self):  # abpraller
            if not (self.tracking_area[0] + (2*self.radius) <= self.position[0] <= self.tracking_area[1] - (2*self.radius)):
                self.speed[0] *= -1

            if not (self.tracking_area[2] + self.radius <= self.position[1] <= self.tracking_area[3] - self.radius):
                self.speed[1] *= -1
                #if not (0 <= self.rect[i] <= bounding_rect.size[i]-self.rect.size[i]):
                #    self.speed[i] *= -1

class Trial:
    def __init__(self, window):
        self.window = window

        # Tracking Bereich definieren, später evtl. wo anders und dann Trial übergeben
        tracking_area = [-4, 4, -4, 4]  # xmin, xmax, ymin, ymax
        self.tracking_area_rect = visual.Rect(window, width=tracking_area[1] - tracking_area[0], height=tracking_area[3] - tracking_area[2])
        self.tracking_area_rect.setPos([(tracking_area[0] + tracking_area[1]) / 2.0, (tracking_area[2] + tracking_area[3]) / 2.0 ])

        # Tracking-Objekte erzeugen
        number_of_tracking_objects = 8
        self.number_of_targets = 3
        self.tracking_objects = []
        for n in range(number_of_tracking_objects):
            if n < self.number_of_targets:
                is_target = True
            else:
                is_target = False
            tracking_object = TrackingObject(is_target, self.window, tracking_area)
            self.tracking_objects.append(tracking_object)

        self.mouse = event.Mouse(win=self.window)
        self.mouse.setVisible(False)

        self.done = False
        self.trial_time = core.Clock()
        self.time_start_still = 0.1
        self.time_mark_targets = 0.5
        self.time_movement = 8
        self.num_blink = 3

    def main(self):
        current_trial_phase = "start"
        mouse_pressed_last_frame = False

        while not self.done:
            current_time = self.trial_time.getTime()
            self.tracking_area_rect.draw()

            if current_time <= self.time_start_still:
                pass
           # Objektmarkierung
            elif current_time <= self.time_start_still + self.time_mark_targets:
                current_trial_phase = "mark"

                # Mittels Modulo Blink an- und ausschalten
                if int((current_time - self.time_start_still) / ((self.time_mark_targets / self.num_blink) / 2)) % 2 == 0:
                    for tracking_object in self.tracking_objects:
                        if tracking_object.is_target:
                            tracking_object.setColor([1.0, -1.0, -1.0])
                else:
                    for tracking_object in self.tracking_objects:
                        tracking_object.setColor([1.0, 1.0, 1.0])
            #Objektbewegung
            elif current_time <= self.time_start_still + self.time_mark_targets + self.time_movement:
                if current_trial_phase == "mark":
                    for tracking_object in self.tracking_objects:
                        tracking_object.setColor([1.0, 1.0, 1.0])

                current_trial_phase == "move"

                for tracking_object in self.tracking_objects:
                    tracking_object.move()

            # Objekte anklicken
            else:
                current_trial_phase == "mark_end"
                self.mouse.setVisible(True)
                # Mouse Klicks
                if self.mouse.getPressed()[0] and not mouse_pressed_last_frame:
                    clicked_object = None
                    dist_mouse_to_clicked_object = 0
                    for tracking_object in self.tracking_objects:
                        dist_to_mouse = tracking_object.getDistToMouseIfHitByMouse( self.mouse )
                        if dist_to_mouse is not None:
                            if clicked_object is None or dist_to_mouse < dist_mouse_to_clicked_object:
                                clicked_object = tracking_object
                                dist_mouse_to_clicked_object = dist_to_mouse
                    if clicked_object is not None:
                        clicked_object.changeMarkedAsTargetState()
                mouse_pressed_last_frame = self.mouse.getPressed()[0]

                # Prüfen, ob fertig ist
                num_marked_targets = 0
                num_marked_distractors = 0
                for tracking_object in self.tracking_objects:
                    if tracking_object.is_marked:
                        if tracking_object.is_target:
                            num_marked_targets = num_marked_targets + 1
                        else:
                            num_marked_distractors = num_marked_distractors + 1

                if num_marked_targets + num_marked_distractors == self.number_of_targets:
                    print("fertig: markierte targets: " + str(num_marked_targets) + "; markierte distraktoren: " + str(num_marked_distractors))
                    fout=open(expInfo['Versuchsperson']+"ses"+str(expInfo['Session'])+".csv", "w")
                    fout.write("# seed, markierte targets, markierte distraktoren\n")
                    fout.write(str(expInfo['Seed']) + ", " + str(num_marked_targets) + ", " + str(num_marked_distractors))
                    self.done = True

            # Immer alle Tracking Objekte malen
            for tracking_object in self.tracking_objects:
                tracking_object.draw()

            self.window.flip()

            if len(event.getKeys()) > 0:
                self.done = True

if __name__ == "__main__":

        try:
                expInfo = misc.fromFile('last_expInfo.pickle')
                expInfo['Session'] += 1
        except:
                expInfo = {'Versuchsleiter': 'Alisa', 'Versuchsperson': 'vp01', 'Session': 1, 'Seed': 1}

        starttime = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        expInfo['Datum'] = starttime
        expInfo['Seed'] = starttime

        # present a dialogue to change infos
        dlg = gui.DlgFromDict(expInfo, title='Motion Tracking Experiment', fixed=['Datum'])
        if dlg.OK:
            misc.toFile('last_expInfo.pickle', expInfo)
            # save params to file for next time
        else:
            core.quit()
            # the user hit cancel so exit

        random.seed(expInfo['Seed'])

            # Initialisierung vom Monitor erfolgt später in Experiment-Klasse, vorübergehend hier
        background_color = (-1, -1, -1)  # Achtung: -1 bis 1

        fenster = visual.Window((800, 600), rgb = background_color, monitor="testMonitor", units="deg")
        trial = Trial(fenster)
        trial.main()

        #cleanup
        fenster.close()
        core.quit()
