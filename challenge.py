import turtle
import math
import time
import urllib.request
import ssl
import random


SCALE = 150
CENTER_PLANET = ""
PLANETS = []
comparePlanets = []
mode = None
simPlanets = []
running = True

scaleTurtle = turtle.Turtle()
scaleTurtle.hideturtle()
scaleTurtle.speed(0)
scaleTurtle.penup()
scaleTurtle.goto(-550, 300)
scaleTurtle.color("white")

turtle.speed(0)
turtle.hideturtle()
turtle.color("white")
turtle.pensize(0.5)

screen = turtle.Screen()
screen.setup(1200, 800)
screen.bgcolor("black")
screen.title("BPhO Computational Physics Challenge 2023")
screen.tracer(False)

KEY_PRESS = ""
def M():
    global KEY_PRESS
    KEY_PRESS = "M"

screen.onkey(M, "M")
screen.onkey(M, "m")

def set_scale(val):
    global SCALE
    SCALE = val
    scaleTurtle.clear()
    scaleTurtle.write("Press 'M' to access Menu\nScale: {} pixels / AU".format(SCALE), font=("Arial", 17, "bold"))

set_scale(150)

class polar_vect:
    def __init__(self, r, theta):
        self.r = r
        self.theta = theta
        self.isPolar = True

    def to_cartesian(self):
        if self.theta > 2 * math.pi or self.theta < 0:
            self.theta = self.theta % (2 * math.pi)
        return vector(self.r*math.cos(self.theta), self.r*math.sin(self.theta))
    
class vector:
    def __init__(self, x, y, z=0):
        self.x = x
        self.y = y
        self.z = z
        self.isPolar = False

    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def angle(self):
        if self.x == 0 and self.y >= 0:
            return 0.5 * math.pi
        elif self.x == 0:
            return 1.5 * math.pi
        
        a = math.atan(self.y / self.x)
        if self.x < 0:
            a += math.pi
        return a

    def to_polar(self):
        return polar_vect(self.magnitude(), self.angle())


CENTER = vector(0, 0)



class Planet:
    def __init__(self):
        self.turt = turtle.Turtle()
        self.turt.penup()
        self.turt.hideturtle()
        self.turt.speed(0)
        self.turt.shape("circle")
        self.turt.pensize(2)
        self.polarPosition = polar_vect(0,0)
        self.momentum = vector(0,0)
        self.color = hex(int("FFFFFF", 16))
        self.time = 0
        self.isStar = False

    def clone(self):
        clone = Planet()
        clone.name = self.name
        clone.mass = self.mass
        clone.orbitalRadius = self.orbitalRadius
        clone.period = self.period
        clone.eccentricity = self.eccentricity
        clone.inclination = self.inclination
        clone.turt.color("#" + self.color)
        clone.color = self.color
        clone.isStar = self.isStar
        return clone

    def get_color(self, depth):
        colors = [int(self.color[0:2], 16), int(self.color[2:4], 16), int(self.color[4:6], 16)]
        while colors[0] + colors[1] + colors[2] < 255 * 3 / 2 + depth and colors != [255, 255, 255]:
            if colors[0] < 255:
                colors[0] += 1
            if colors[1] < 255:
                colors[1] += 1
            if colors[2] < 255:
                colors[2] += 1
        
        while colors[0] + colors[1] + colors[2] > 255 * 3 / 2 + depth and colors != [0, 0, 0]:
            if colors[0] > 0:
                colors[0] -= 1
            if colors[1] > 0:
                colors[1] -= 1
            if colors[2] > 0:
                colors[2] -= 1
        
        color = 256*256*colors[0] + 256*colors[1] + colors[2]
        color = str(hex(color))[2:].upper()
        while len(color) < 6:
            color = "0" + color
        return color

    def show_label(self, height, dimension3 = True):
        self.turt.penup()
        if dimension3:
            self.turt.goto(-550, height)
            self.turt.pendown()
            r = 60000000000000
            for depth in range(-r, r, int(r/50)):
                self.turt.color("#" + self.get_color(int(depth / (1.496 * 10**11))))
                self.turt.forward(1)
            self.turt.penup()
            self.turt.goto(-435, height-5)
        else:
            self.turt.goto(-550, height)
            self.turt.dot(8, "#" + self.color)
            self.turt.goto(-540, height-5)
        self.turt.color("white")
        self.turt.write(self.name, font=("Arial", 10, "bold"))
        self.turt.color("#" + self.color)
        screen.update()
        

    def goto(self, vect):
        if vect.isPolar:
            vect = vect.to_cartesian()
        if mode == "compare eccentricity":
            vect.x += 300 * 1.496 * 10 ** 11 / SCALE

        # task 7
        if getPlanet(CENTER_PLANET).isStar == False:
            vect.x -= CENTER.x
            vect.y -= CENTER.y
        
        self.turt.goto(int(SCALE / (1.496 * 10 **11) * vect.x), int(SCALE / (1.496 * 10 **11) * vect.y))


    def clear(self):
        self.turt.clear()
        self.turt.hideturtle()

    def get_radius(self, angle):
        return self.orbitalRadius * (1 - self.eccentricity**2) / (1 - self.eccentricity * math.cos(angle))

# task 2
    def show_orbit(self, numSteps):
        if self.orbitalRadius == 0:
            numSteps = 1

        eccentricity = self.eccentricity
        
        self.turt.penup()
        pos = polar_vect(self.get_radius(0), 0)
        self.goto(pos)
        self.turt.pendown()
        
        for i in range(numSteps):
            pos.theta += 2 * math.pi / numSteps
            pos.r = self.get_radius(pos.theta)

            self.goto(pos)

# task 3
    def step_animation(self, speed, adjustSpeed = True):
        while self.time > self.period:
            self.time -= self.period
            
        if self.isStar == False:
            self.time += int(speed)
            if adjustSpeed:
                self.polarPosition.theta = self.get_angle()
            else:
                self.polarPosition.theta += speed * 2 * math.pi / self.period
            
            self.polarPosition.r = self.get_radius(self.polarPosition.theta)

# task 5
    def get_angle(self):
        while self.time > self.period:
            self.time -= self.period
        
        stepSize = 2 * math.pi / 5000
        angle = 0
        time = 0
        # slowly increase the angle until the current time is outputed from the integral
        while time < self.time:
            angle += stepSize
            time += self.period * (1 - self.eccentricity**2) ** (3/2) * stepSize / (2 * math.pi * (1 - self.eccentricity * math.cos(angle)) ** 2)
        return angle





def load_planets(data):
    global PLANETS
    global CENTER_PLANET
    global simPlanets
    global mode
    PLANETS = []
    for line in data:
        planet = Planet()
        planet.name = line[0]
        planet.mass = float(line[1]) * 5.97219 * 10**24
        planet.orbitalRadius = float(line[2]) * 1.496 * 10**11
        planet.period = float(line[3]) * 365.25 * 24 * 60**2
        planet.eccentricity = float(line[4])
        planet.inclination = float(line[5]) * 2 * math.pi / 360
        planet.turt.color("#" + line[6])
        planet.color = line[6]
        if len(line) == 8:
            planet.isStar = True
            CENTER_PLANET = planet.name
        PLANETS.append(planet)
    simPlanets = PLANETS.copy()
    
    init_sim(simPlanets)
    mode = "sim3D"



def clear_screen():
    for planet in PLANETS:
        planet.clear()
    turtle.clear()
    for planet in comparePlanets:
        planet.clear()
        planet.graphTurt.clear()
        planet.graphTurt.hideturtle()

def getPlanet(name):
    for planet in PLANETS:
        if planet.name == name:
            return planet

    return None




    
def show_inner_orbits(precision):
    try:
        set_scale(150)
        clear_screen()
        precision = int(precision)
        
        getPlanet("Mercury").show_orbit(precision)
        getPlanet("Venus").show_orbit(precision)
        getPlanet("Earth").show_orbit(precision)
        getPlanet("Mars").show_orbit(precision)
    except:
        turtle.textinput("Show Orbit Paths ERROR", "This feature only works when our solar system is loaded, not with exoplanets\nPress enter, 'OK' or 'Cancel' to hide this message")
    
def show_outer_orbits(precision):
    try:
        set_scale(8)
        clear_screen()
        precision = int(precision)
        
        getPlanet("Jupiter").show_orbit(precision)
        getPlanet("Saturn").show_orbit(precision)
        getPlanet("Uranus").show_orbit(precision)
        getPlanet("Neptune").show_orbit(precision)
        getPlanet("Pluto").show_orbit(precision)
    except:
        turtle.textinput("Show Orbit Paths ERROR", "This feature only works when our solar system is loaded, not with exoplanets\nPress enter, 'OK' or 'Cancel' to hide this message")
    




# task 7
def set_offsets(depth):
    global CENTER
    if getPlanet(CENTER_PLANET).isStar == False:
        planet = getPlanet(CENTER_PLANET)
        CENTER = planet.polarPosition.to_cartesian()
        if depth:
            CENTER.x *= math.cos(planet.inclination)
    
    


SPEED = 0
smallestPeriod = 0
frameStart = 0

# dynamically adjusts speed of simulation based on framerate
# the pause between frames is provided by the time it takes to make calculations
# and can change during the simulation
def update_speed():
    global frameStart
    global SPEED
    end = time.perf_counter()
    fps = 1 / (end - frameStart)
    SPEED = smallestPeriod / fps
    frameStart = time.perf_counter()




# Task 3
def init_sim(simPlanets, dimension3 = True):
    global SPEED
    global smallestPeriod
    global frameStart

    clear_screen()

    if getPlanet(CENTER_PLANET) not in simPlanets:
        simPlanets.append(getPlanet(CENTER_PLANET))
        
    if len(simPlanets) <= 1:
        return

    height = 250
    for planet in simPlanets:
        planet.show_label(height, dimension3)
        height -= 20
    if dimension3:
        turtle.penup()
        turtle.goto(-550, 260)
        turtle.color("white")
        turtle.write("Brightness indicates Z-axis height")

    SPEED = 0
    largestR = 0
    if simPlanets[0].isStar:
        smallestPeriod = simPlanets[1].period
    else:
        smallestPeriod = simPlanets[0].period

    
    for planet in simPlanets:
        if planet.isStar == False:
            if planet.orbitalRadius > largestR:
                largestR = planet.orbitalRadius
            if planet.period < smallestPeriod:
                smallestPeriod = planet.period

    largestR = largestR / (1.496 * 10**11) # convert to AU
    
    set_scale(int(350 / largestR))
    
    for planet in simPlanets:
        planet.polarPosition.r = planet.get_radius(0)
        planet.polarPosition.theta = 0
        planet.momentum = vector(0,0)
        planet.time = 0
        planet.turt.color("#" + planet.color)
        planet.turt.showturtle()
        planet.turt.penup()

    frameStart = time.perf_counter()


def simulate_frame(simPlanets, depth, adjustSpeed):
    
    if getPlanet(CENTER_PLANET) not in simPlanets:
        simPlanets.append(getPlanet(CENTER_PLANET))
    
    for planet in simPlanets:
        planet.step_animation(SPEED, adjustSpeed)
    
    set_offsets(depth)
    
    for planet in simPlanets:

# task 4
        if depth:
            pos = planet.polarPosition.to_cartesian()
            pos.z = pos.x * (math.sin(planet.inclination - getPlanet(CENTER_PLANET).inclination))
            pos.x = pos.x * math.cos(planet.inclination)

            planet.turt.color("#" + planet.get_color(int(3 * pos.z * SCALE / (1.496 * 10**11))))
            planet.goto(pos)
        
        else:
            planet.goto(planet.polarPosition)
        
        planet.turt.pendown()


# task 6

def pen_goto(v):
    if v.isPolar:
        v = v.to_cartesian()
    turtle.goto(int(SCALE / (1.496 * 10 **11) * v.x), int(SCALE / (1.496 * 10 **11) * v.y))

def spirograph_frame(planet1, planet2):
    planet1.turt.hideturtle()
    planet2.turt.hideturtle()
    planet1.step_animation(SPEED)
    planet2.step_animation(SPEED)
    
    turtle.penup()
    pen_goto(planet1.polarPosition)
    turtle.pendown()
    pen_goto(planet2.polarPosition)
    


def rescale(n, range1, range2):
    delta1 = range1[1] - range1[0]
    delta2 = range2[1] - range2[0]
    return (delta2 * (n - range1[0]) / delta1) + range2[0]
    

def change_visible_planets():
    prompt = "Enter the number next to a planet to change its visibility.\nPress 'Cancel' when you are done.\n\n\nnum | visible | name\n"
    for i in range(0, len(PLANETS)):
        prompt += " " + str(i) + "  "
        if i < 10:
            prompt += "  "
        
        if PLANETS[i] in simPlanets:
            prompt += "|    yes    | "
        else:
            prompt += "|    no      | "
        prompt += PLANETS[i].name + "\n"

    num = turtle.numinput("Configuration", prompt, minval = 0, maxval = len(PLANETS) - 1)
    if num == None:
        screen.listen()
    else:
        num = int(num)
        if PLANETS[num] in simPlanets:
            simPlanets.remove(PLANETS[num])
        else:
            simPlanets.append(PLANETS[num])
        change_visible_planets()

def choose_planet():
    prompt = "Enter the number next to the planet you want to select\n\n"
    for i in range(0, len(PLANETS)):
        prompt += " " + str(i) + ". "
        if i < 10:
            prompt += " "
        prompt += PLANETS[i].name + "\n"
    
    num = turtle.numinput("Configuration", prompt, minval = 0, maxval = len(PLANETS) - 1)
    return PLANETS[int(num)]

def menu():
    global mode
    global simPlanets
    global comparePlanets
    global CENTER_PLANET
    global frameStart
    global SPEED
    global running
    maxval = 8
    prompt = """
Menu

Select an option by pressing its number:


 0.   Quit Program
 1.   Start Spirograph
 2.   Start 2D simulation
 3.   Start 3D simulation
 4.   View inner orbit paths
 5.   View outer orbit paths
 6.   Compare orbital angle with eccentricity
 7.   Load our solar system
 8.   Load exoplanetary system"""
    if mode == "sim3D" or mode == "sim2D":
        maxval = 11
        prompt += """
 9.   Change scale
 10. Change origin
 11. Change visible planets
"""
    if mode == "spirograph":
        maxval = 9
        prompt += " \n 9.   Change scale\n"
        
    choice = turtle.numinput("menu", prompt, minval=0, maxval=maxval)

    
    if choice == 0:
        running = False
    if choice == 1:
        p1 = choose_planet()
        if p1 != None:
            p2 = choose_planet()
            if p2 != None and p1 != p2:
                init_sim([p1, p2])
                clear_screen()
                simPlanets = [p1, p2]
                turtle.penup()
                turtle.goto(-550, 250)
                turtle.write("Spirograph of {} and {}".format(p1.name, p2.name), font=("Arial", 15, "bold"))
                mode = "spirograph"
    if choice == 2:
        init_sim(simPlanets, False)
        mode = "sim2D"
    if choice == 3:
        init_sim(simPlanets)
        mode = "sim3D"
    if choice == 4:
        precision = turtle.numinput("Show inner orbits", "Enter the number of samples ablong the orbit path to make.\nLarger numbers will result in a higher precision", minval=3, maxval=10000, default=1000)
        if precision != None:
            show_inner_orbits(precision)
            mode = None
    if choice == 5:
        precision = turtle.numinput("Show outer orbits", "Enter the number of samples ablong the orbit path to make.\nLarger numbers will result in a higher precision", minval=3, maxval=10000, default=1000)
        if precision != None:
            show_outer_orbits(precision)
            mode = None
    if choice == 6:
        for planet in PLANETS:
            if planet.isStar:
                CENTER_PLANET = planet.name
        
        p1 = choose_planet().clone()
        if p1.isStar == False:
            p2 = p1.clone()
            p1.name += " - changing angular speed"
            p2.name += " - constant angular speed"
            p1.color = "FF0000"
            p2.color = "1111FF"
            init_sim([p1, p2], False)
            comparePlanets = [p1, p2]
            set_scale(SCALE/2)
            turtle.penup()
            turtle.color("white")
            turtle.pensize(5)
            turtle.goto(100, -350)
            turtle.pendown()
            turtle.goto(-500, -350)
            turtle.goto(-500, 200)
            turtle.penup()
            turtle.pensize(1)
            turtle.goto(-300, -370)
            turtle.write("Time / Years", font=("Arial", 15, "bold"))
            turtle.goto(-505, -100)
            turtle.write("Orbital\nAngle\n/ radians", align="right", font=("Arial", 15, "bold"))
            turtle.goto(-505, -370)
            turtle.write("0", align="right", font=("Arial", 15, "bold"))
            turtle.goto(-505, 180)
            turtle.write("2π", align="right", font=("Arial", 15, "bold"))
            turtle.goto(100, -370)
            turtle.write("{:.3}".format(p1.period / (60**2 * 24 * 365.25)), align="right", font=("Arial", 15, "bold"))

            for p in comparePlanets:
                p.graphTurt = turtle.Turtle()
                p.graphTurt.speed(0)
                p.graphTurt.shape("circle")
                p.graphTurt.turtlesize(0.25, 0.25, 0.25)
                p.graphTurt.penup()
                p.graphTurt.goto(-500, -350)
                p.graphTurt.color("#" + p.color)
                p.graphTurt.pendown()
            mode = "compare eccentricity"
        else:
            turtle.textinput("Simulation Input Error", "You cannot compare orbital speeds with eccentricity using the central star.\nPlease use a planet\nPress enter, 'OK' or 'Cancel' to hide this message")

    if choice == 7:
        clear_screen()
        load_solar_system()

    if choice == 8:
        loadTurtle = turtle.Turtle()
        loadTurtle.hideturtle()
        loadTurtle.speed(0)
        loadTurtle.color("white")
        loadTurtle.dot(500)
        loadTurtle.color("black")
        loadTurtle.write("Loading, Please wait", align="center", font=("Arial", 40, "bold"))
        screen.update()
        loadTurtle.clear()
        try:
            data = NASA_exoplanet_data()
        except:
            turtle.textinput("Exoplanet Data ERROR", "ERROR: Unable to access online database.\nPlease check your internet connection\nPlease use a planet\nPress enter, 'OK' or 'Cancel' to hide this message")
        else:
            screen.update()
            starName = turtle.textinput("Load Exoplanetary System", "Enter the name of the star you would like to simulate.\n\nThe star must have at least one planet orbiting it which is not missing any information in the database\nThere must only be one star in the system (no binary systems)\n\nData is sourced from the Exoplanet Archive,\nwhich is operated by the California Institute of Technology, under contract with the National Aeronautics and Space Administration\nunder the Exoplanet Exploration Program.\nMore information: https://exoplanetarchive.ipac.caltech.edu/docs/intro.html")
            data = construct_exo_system(data, starName)
            if data == None:
                turtle.textinput("Exoplanet Data ERROR", "ERROR: This star was not found in the data.\nPlease make sure that you spelled it correctly and that it met the criteria previously described.\nPress enter, 'OK' or 'Cancel' to hide this message")
            else:
                clear_screen()
                load_planets(data)
                
        

    if choice == 9:
        scale = turtle.numinput("Configuration", "Enter a new scale to use.\nThe unit is pixels per astronomical unit", default=SCALE)
        if scale != None:
            if mode == "sim2D":
                init_sim(simPlanets, False)
            else:
                init_sim(simPlanets, True)
            set_scale(scale)
    if choice == 10:
        p = choose_planet()
        if p != None:
            CENTER_PLANET = p.name
            if mode == "sim2D":
                init_sim(simPlanets, False)
            else:
                init_sim(simPlanets, True)
    if choice == 11:
        change_visible_planets()
        if mode == "sim2D":
            init_sim(simPlanets, False)
        else:
            init_sim(simPlanets, True)
    
    screen.listen()
    frameStart = time.perf_counter()


def load_solar_system():
    try:
        file = open("planet data.txt", "r")
        data = file.read().split("\n")
        for i in range(0, len(data)):
            data[i] = data[i].split("\t")


        data.pop(0)
        load_planets(data)

    except:
        print("\n\n")
        print("Error: 'planet data.txt' file could not be found, or is badly formated")
        print("This file is necessary to allow this program to run, since it contains important parameters")
        print()
        print("Goodbye")
        import sys
        sys.exit()

def NASA_exoplanet_data():
    url = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+hostname,st_mass,pl_name,pl_bmasse,pl_orbsmax,pl_orbper,pl_orbeccen,pl_orbincl%20+from+pscomppars+where+sy_snum+=+1+and+pl_controv_flag+=+0+order+by+pl_name&format=csv"
    req = urllib.request.Request(url)
    data = urllib.request.urlopen(req, context=ssl._create_unverified_context()).read().decode()
    data = data.split("\n")
    data.pop(0)

    # reformat response as array
    i = 0
    while i < len(data):
        data[i] = data[i].split(",")
        removed = False
        
        for pNum in range(0, len(data[i])):
            if removed == False:
                if data[i][pNum] == "": # remove exoplanets with missing data
                    removed = True
                    data.pop(i)
                elif '"' in data[i][pNum]:
                    data[i][pNum] = data[i][pNum].replace('"', "")
                else:
                    data[i][pNum] = float(data[i][pNum])
        
        if removed == False:
            i += 1
    
    return data


def construct_exo_system(data, starName):
    if starName == None:
        return None
    
    starMass = 0
    filtered = []
    starName = starName.upper()
    finName = ""
    if " " in starName:
        starName = starName.replace(" ", "")
    if "-" in starName:
        starName = starName.replace("-", "")
    
    for line in data:
        name = line[0].upper()
        if " " in name:
            name = name.replace(" ", "")
        if "-" in name:
            name = name.replace("-", "")
        
        if name == starName:
            filtered.append(line[2:].copy())
            starMass = line[1]
            finName = line[0]

    if len(filtered) == 0:
        return None

    angleOffset = filtered[0][5]
    for i in range(0, len(filtered)):
        filtered[i][5] -= angleOffset
    
    filtered.append([finName, starMass, 0, 0, 0, 0])

    for planet in filtered:
        planet.append(str(hex(random.randint(0, 256**3 - 1)))[2:].upper()) # set random color
        while len(planet[6]) < 6:
            planet[6] = "0" + planet[6]

    filtered[len(filtered)-1].append("") # mark star as center

    return filtered






load_solar_system()
screen.listen()

while running:
    screen.update()
    update_speed()
    
    if mode == "sim3D":
        simulate_frame(simPlanets, True, True)
    elif mode == "sim2D":
        simulate_frame(simPlanets, False, True)
    elif mode == "compare eccentricity":
        SPEED /= 5
        simulate_frame([comparePlanets[1]], False, True)
        simulate_frame([comparePlanets[0]], False, False)
        for p in comparePlanets:
            if p.graphTurt.distance(rescale(p.time, [0, p.period], [-500, 100]), rescale(p.polarPosition.theta, [0, 2*math.pi], [-350, 200])) > 100:
                p.graphTurt.penup()
            p.graphTurt.goto(rescale(p.time, [0, p.period], [-500, 100]), rescale(p.polarPosition.theta, [0, 2*math.pi], [-350, 200]))
            p.graphTurt.pendown()
    elif mode == "spirograph":
        spirograph_frame(simPlanets[0], simPlanets[1])
    else:
        time.sleep(0.5)

    if KEY_PRESS == "M":
        KEY_PRESS = ""
        menu()





turtle.bye()


