import pygame
import os
import sys
import random
import subprocess
import shlex

from TrackPieces.Junction import Junction
from TrackPieces.LongLeft import LongLeft
from TrackPieces.LongRight import LongRight
from TrackPieces.LongStraight import LongStraight
from TrackPieces.ShortLeft import ShortLeft
from TrackPieces.ShortRight import ShortRight
from TrackPieces.ShortStraight import ShortStraight
from TrackPieces.Station import Station
from Trains.carriage import carriage
from Trains.train import train
import trainMover
from train_pddl import TrainPDDLProblem


directory = os.getcwd()

# These variables define the height and width of the display window. They start as a reduced size to make the window display properly on small screens.
screenWidth = 1000
screenHeight = 880

# button width and height
buttonWidth = 115
buttonHeight = 55
trackButtonWidth = 190
trackButtonHeight = 55

# Add these variables at the beginning of your script or in your game class
train_pos = 0
train_speed = 2
track_y = screenHeight - 100  # Position of the track

# These are colours for various elements.
# trackColour = (255, 128, 0)
trackColour = (169, 169, 169)
menuColour = (31, 40, 51)
# buttonColour = (140,140,140)
# menuColour = (166, 166, 166)
buttonColour = (102, 252, 241)
textColour = (197, 198, 199)

icon = pygame.image.load(directory + '/Images/train_blue.png')
pygame.display.set_icon(icon)
pygame.display.set_caption('Model Railway Management System')

# These two variables are used to keep track of where the most recent piece of track was generated. They are constantly changing, but start in the middle of the screen.
currentCoX = screenWidth/2
currentCoY = screenHeight/2

# This variable is used to tell the system when to generate the track.
generateTrack = False


def getTrack(trackID):
    for t in track:
        if t.getID() == trackID:
            return t
    print("Track with the given id not found!")


def openTrack(trackName):
    """
    Loads track information from a specified file and populates relevant dictionaries.

    This function clears the existing data in `trackDictionary`, `track`, and `tracksDict`
    and then reads the track data from the specified file located in the `ExampleTracks`
    directory. Each line in the file is expected to be a semicolon-separated list of
    track attributes. The function parses each line, constructs a dictionary with the
    parsed data, and appends this dictionary to `trackDictionary`.

    Args:
        trackName (str): The name of the track file to be opened and loaded.

    Raises:
        FileNotFoundError: If the specified track file does not exist.
        IOError: If there is an error reading the file.

    Note:
        - The function assumes the global variables `trackDictionary`, `track`,
          and `tracksDict` are defined elsewhere in the code.
        - The file's format is assumed to have semicolon-separated values in the
          following order: TrackType, TrackID, PreviousID, NextID, Branch.
    """

    trackDictionary.clear()
    track.clear()
    tracksDict.clear()
    with open(directory+"/ExampleTracks/"+trackName, "r") as file:
        for x in file:
            temp = x.split(";")
            tempDictionary = {
                "TrackType": temp[0],
                "TrackID": temp[1],
                "PreviousID": temp[2],
                "NextID": temp[3],
                "Branch": temp[4]
            }
            trackDictionary.append(tempDictionary)


def loadTrack():
    global branchCount
    for T in trackDictionary:
        if 'LongRight' in T['TrackType']:
            track.append(
                LongRight(screen, T['TrackID'], T['PreviousID'], T['NextID'], T['Branch']))
        elif 'LongStraight' in T['TrackType']:
            track.append(LongStraight(
                screen, T['TrackID'], T['PreviousID'], T['NextID'], T['Branch']))
        elif 'ShortStraight' in T['TrackType']:
            track.append(ShortStraight(
                screen, T['TrackID'], T['PreviousID'], T['NextID'], T['Branch']))
        elif 'Station' in T['TrackType']:
            track.append(
                Station(screen, T['TrackID'], T['PreviousID'], T['NextID'], T['Branch']))
        elif 'LongLeft' in T['TrackType']:
            track.append(
                LongLeft(screen, T['TrackID'], T['PreviousID'], T['NextID'], T['Branch']))
        elif 'ShortRight' in T['TrackType']:
            track.append(ShortRight(
                screen, T['TrackID'], T['PreviousID'], T['NextID'], T['Branch']))
        elif 'ShortLeft' in T['TrackType']:
            track.append(
                ShortLeft(screen, T['TrackID'], T['PreviousID'], T['NextID'], T['Branch']))
        elif 'Junction' in T['TrackType']:
            temp = T['NextID'].split(",")
            track.append(Junction(
                screen, T['TrackID'], T['PreviousID'], temp[0], temp[1], T['Branch']))
    # Generating a new track will clear the trains, so this will ensure all tracks are set to unoccupied.
    for x in track:
        x.setOccupied(False)


def draw_button(screen, borderColor, x, y, width, height, text="", center=(), textcolor=textColour, border_width=3, border_radius=0, backgroundColor=None):
    if len(center) == 0:
        center = (x + width // 2, y + height // 2)

    # Create a surface for the button
    button_surface = pygame.Surface((width, height), pygame.SRCALPHA)

    # Fill the entire surface with a transparent color
    button_surface.fill(menuColour)

    # Draw the border on the button surface
    pygame.draw.rect(button_surface, borderColor, [
                     0, 0, width, height], border_width, border_radius)

    # Blit the button surface onto the screen
    screen.blit(button_surface, (x, y))

    # Draw the text on top of the button
    if text:
        text_surface = buttonText.render(
            text, True, textcolor, backgroundColor)
        text_rect = text_surface.get_rect(center=center)
        screen.blit(text_surface, text_rect)


def write_text(text, center, color=textColour, title=False):
    text_surface = None
    if title:
        text_surface = headingText.render(text, True, color)
    else:
        text_surface = buttonText.render(text, True, color)
    text_rect = text_surface.get_rect(center=center)
    screen.blit(text_surface, text_rect)


def showLaunchScreen():
    global train_pos
    draw_button(screen, menuColour, 0, 0, screenWidth,
                screenHeight)
    draw_button(screen, buttonColour, (screenWidth/2) -
                (105/2), (screenHeight/2)-(55/2), buttonWidth, buttonHeight, text='Open', center=(screenWidth/2, screenHeight/2), border_radius=10)
    write_text("Model Railway Design and Management", (500, 50), color=textColour, title=True)
    write_text("CS948 Project", (500, 80), color=textColour, title=True)
    write_text("Niskarsha Ghimire - 202390729", (500, 110), color=textColour)

    # Draw track
    pygame.draw.line(screen, (100, 100, 100), (0, track_y), (screenWidth, track_y), 5)
    
    # Draw train
    train_width = 100
    train_height = 50
    train_x = (train_pos % (screenWidth + train_width)) - train_width
    
    # Train body
    pygame.draw.rect(screen, (200, 0, 0), (train_x, track_y - train_height, train_width, train_height))
    
    # Train wheels
    wheel_radius = 10
    pygame.draw.circle(screen, (50, 50, 50), (int(train_x + 20), track_y), wheel_radius)
    pygame.draw.circle(screen, (50, 50, 50), (int(train_x + train_width - 20), track_y), wheel_radius)
    
    # Update train position
    train_pos += train_speed

    # Add some smoke effect (optional)
    for i in range(5):
        smoke_x = train_x + train_width + 10 + i * 15
        smoke_y = track_y - train_height - 20 - i * 10
        smoke_radius = 5 + i * 2
        opacity = 255 - i * 50
        smoke_surface = pygame.Surface((smoke_radius * 2, smoke_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(smoke_surface, (200, 200, 200, opacity), (smoke_radius, smoke_radius), smoke_radius)
        screen.blit(smoke_surface, (smoke_x - smoke_radius, smoke_y - smoke_radius))
    pygame.display.flip()


def handleOpenLaunchScreen(mousepos):
    global isLaunchScreen
    global isSpawnScreen
    open_x = (screenWidth/2) - (105/2)
    open_y = (screenHeight/2)-(55/2)

    if (mousepos[0] > open_x and mousePos[0] < (open_x + buttonWidth)) and (mousepos[1] > open_y and mousePos[1] < (open_y + buttonHeight)):
        isLaunchScreen = False
        isSpawnScreen = True


def showMainScreen():
    # show menu buttons
    spawn_menu_buttons = ['Spawn Train',
                          'Start sim', 'Track', 'Back', 'Reverse']
    y = 105
    for menu in spawn_menu_buttons:
        draw_button(screen, buttonColour, 5, y,
                    buttonWidth, buttonHeight, menu, border_radius=10)
        y += 60

    # Add information box
    draw_button(screen, menuColour, 0, 0, screenWidth, 100)
    write_text('Information Box', center=(200, 20))
    write_text(infotext, center=(190, 45))

    # Draw console button
    draw_button(screen, buttonColour, 5, 5, buttonWidth,
                buttonHeight, text="Console", center=(55, 25), border_radius=10)


def showConsole(messages):
    draw_button(screen, menuColour, 0, 105, 1000, 600)
    draw_button(screen, (150, 150, 150), 0, 105, 10, 600)
    draw_button(screen, (100, 100, 100), 0, 105, 10, 57)
    draw_button(screen, buttonColour, 870, 640, buttonWidth,
                buttonHeight, text="Clear", center=(932, 670), border_radius=10)

    if not isClearConsole:
        x = 150
        y = 120
        if len(messages) == 0:
            messages.add('Opened console')
        for message in messages:
            write_text(message, (x, y))
            y += 20


def handleOpenConsoleButtonClick(mousepos):
    consoleX = 5
    consoleY = 5
    if (mousePos[0] > consoleX and mousePos[0] < (consoleX + buttonWidth)) and (mousepos[1] > consoleY and mousePos[1] < (consoleY + buttonHeight)):
        global isOpenConsole
        global isClearConsole
        isOpenConsole = not isOpenConsole
        isClearConsole = False


def handleConsoleClearButtonClick(mousepos):
    clearX = 890
    clearY = 640
    if (mousePos[0] > clearX and mousePos[0] < (clearX + buttonWidth)) and (mousepos[1] > clearY and mousePos[1] < (clearY + buttonHeight)):
        global isClearConsole
        consoleMessage.clear()
        isClearConsole = True


def showTrackScreen(imageSelected):
    runningY = 125
    draw_button(screen, menuColour, 130, 115, 550, 480)

    draw_button(screen, (150, 150, 150), 130, 115, 10, 480)
    draw_button(screen, (100, 100, 100), 130, scrollBarY, 10, 57)

    # show all the tracks for selection
    if len(tracksList) > 7:
        for f in range(startScroll, startScroll + 7):
            draw_button(screen, buttonColour, 150, runningY, trackButtonWidth,
                        trackButtonHeight, text=tracksList[f][0:len(tracksList[f])-4], center=(240, runningY + (55/2)), border_radius=10)
            tracksCountButton.append(
                (150, runningY, trackButtonWidth, trackButtonHeight, tracksList[f]))
            runningY += 65
    else:
        for f in tracksList:
            draw_button(screen, buttonColour, 150, runningY, trackButtonWidth,
                        trackButtonHeight, text=f[0:len(f)-4], center=(240, runningY + (55/2)), backgroundColor=buttonColour, border_radius=10)
            tracksCountButton.append(
                (150, runningY, trackButtonWidth, trackButtonHeight, f))
            runningY += 65

    # if track selected show selected track image
    if imageSelected:
        tempString = selectedTrack[0:len(selectedTrack)-4]
        if os.path.isfile("Images/"+tempString+".png"):
            trackImage = pygame.image.load("Images/"+tempString+".png")
        else:
            trackImage = pygame.image.load("Images/placeholder.png")
        screen.blit(trackImage, (410, 130))
        write_text(tempString, (540, 400))
    else:
        draw_button(screen, (255, 255, 255), 410, 130, 250, 250)

    # draw select and cancel button
    draw_button(screen, buttonColour, 420, 450, buttonWidth,
                buttonHeight, text="Select", center=(470, 475), border_radius=10)
    draw_button(screen, buttonColour, 540, 450, buttonWidth,
                buttonHeight, text="Cancel", center=(590, 475), border_radius=10)


def scrollEffectTrackSelection(event, mousePos):
    global startScroll
    global scrollBarY

    if (mousePos[0] > 140 and mousePos[0] < 330) and (mousePos[1] > 125 and mousePos[1] < 585):
        if event.y == -1:
            if startScroll < len(tracksList) - 7:
                startScroll += 1
                scrollBarY += 423/(len(tracksList)-7)

        elif event.y == 1:
            if startScroll > 0:
                startScroll -= 1
                scrollBarY -= 423/(len(tracksList)-7)


def generateTrainTrack():
    global startPointX
    global startPointY
    # The compass is used to tell the program what rotation the next track should be placed in.
    compass = "E"
    savePoints = []

    currentCoX, currentCoY = startPointX, startPointY

    # This iterates through all the tracks in the current branch.
    for c in track:
        toDraw = True
        for s in savePoints:
            if c.getID() == s[0]:
                if not s[-1]:
                    currentCoX = s[1]
                    currentCoY = s[2]
                    compass = s[3]
                toDraw = False
        if not toDraw:
            continue
        # If the next track is a junction, it will create a "save point" containing the coordinates and compass direction.
        if c.getType() == "Junction":
            nextTrackId = c.getNextID()
            secondNextTrackID = c.getSecondNextID()
            next, secondNext = c.drawTrack(
                currentCoX, currentCoY, compass, screen, getTrack(nextTrackId), getTrack(secondNextTrackID), trackColour=trackColour)
            currentCoX, currentCoY = next[1], next[2]
            compass = next[3]
            savePoints.append(next)
            savePoints.append(secondNext)
        # If it isn't a junction then change the coordinates and compass as normal.
        else:
            # The drawTrack function is what actually draws the track pies on the screen, it returns the new coordinates to draw the next track.
            currentCoX, currentCoY = c.drawTrack(
                currentCoX, currentCoY, compass, screen, trackColour=trackColour)
            compass = c.adjustCompass(compass)
        # These if statements move the track if it gets too close to the edge of the screen.
        if currentCoX > screenWidth - 50:
            startPointX = startPointX - (currentCoX - screenWidth + 50)
            currentCoX = screenWidth-50
        if currentCoY > screenHeight-50:
            startPointY = startPointY - \
                (currentCoY - screenHeight + 50)
            currentCoY = screenHeight - 50
        if currentCoY < 120:
            startPointY = startPointY + (120 - currentCoY)
            currentCoY = 120


def stationSelectionMenu():
    global stationCount
    stationCount.clear()
    runningX = 135
    for x in track:
        if x.getType() == "Station":
            draw_button(screen, buttonColour, runningX, 105, 100, 55,
                        text='Station '+x.getID(), center=(runningX + 50, 105 + (55/2)), border_radius=10)
            stationCount.append((runningX, 105, 100, 55, x.getID()))
            runningX += 115

# handle track selection in selection menu (display image when track is selected)


def handleTrackSelection(mousePos):
    global imageSelected
    global selectedTrack
    for trackButton in tracksCountButton:
        if (mousePos[0] > trackButton[0] and mousePos[0] < (trackButton[0] + trackButton[2])) and (mousePos[1] > trackButton[1] and (mousePos[1] < (mousePos[1] + trackButton[3]))):
            imageSelected = True
            selectedTrack = trackButton[4]


def clearTrackSelection():
    pass


def handleTrackButton(mousePos):
    trackX = 5
    trackY = 225
    if (mousePos[0] > trackX and mousePos[0] < (trackX + buttonWidth)) and (mousePos[1] > trackY and mousePos[1] < (trackY + buttonHeight)):
        global showTrackSelection
        clearTrackSelection()
        showTrackSelection = not showTrackSelection

# A track has been selected at this point so this calls the necessary functions and resets all global variables to their default state.


def handleSelectButtonInTrack(mousePos):
    selectX = 420
    selectY = 450
    if (mousePos[0] > selectX and mousePos[0] < (selectX + buttonWidth)) and (mousePos[1] > selectY and mousePos[1] < (selectY + buttonHeight)):
        global trackSelected
        global generateTrack
        global moveKeyPressed
        global showTrackSelection

        global currentTrack
        global nextTrack
        global trainCompass
        global startPointX
        global startPointY
        global spawnTimer
        global spawnIteration
        global waiting
        global spawning
        global spawnMenu
        global spawningCompass
        global startingTrack
        global startingNextTrack
        global tempStartPointX
        global tempStartPointY
        global startScroll
        global selectTrack
        global trackChosen
        global selectedImage
        global displayImage
        global scrollBarY
        global isOpenConsole
        global pathSelect
        global initialStation
        global moveSkip
        global launchScreen
        global infoText
        global selectedTrack
        global reverseTrain

        trackSelected = True
        openTrack(selectedTrack)
        loadTrack()
        generateTrack = True
        moveKeyPressed = False
        circleCenter.clear()
        showTrackSelection = False

        currentTrack = track[0]
        nextTrack = track[1]
        angle.clear()
        trainCompass = "E"
        swapTrainCompass.clear()
        tracksDict.clear()
        trainCompassDict.clear()
        junctionDirection.clear()
        startPointX = screenWidth/2
        startPointY = screenHeight/2
        stationStop.clear()
        timer.clear()
        spawnTimer = 0
        spawnIteration = 0
        waiting = False
        spawning = False
        carriageStop.clear()
        spawnMenu = False
        stationCount.clear()
        spawningCompass = "E"
        startingTrack = "null"
        startingNextTrack = "null"
        tempStartPointX = 0
        tempStartPointY = 0
        startScroll = 0
        selectTrack = False
        trackChosen = False
        selectedTrack = "null"
        selectedImage = "null"
        trainList.clear()
        displayImage = False
        selectedTrack = "null"
        scrollBarY = 115
        isOpenConsole = False
        consoleMessage.clear()
        pathSelect = False
        initialStation = ""
        stationList.clear()
        instructions.clear()
        currentInstruction.clear()
        instructionCounter.clear()
        switch.clear()
        moveSkip = False
        launchScreen = False
        reverseTrain = False
        infoText = ""
        occupiedSpawns.clear()
        infoText = "Spawn a train."
        consoleMessage.add("- New track generated")


def handleSpawnTrainButton(mousePos):
    selectX = 5
    selectY = 105
    if (mousePos[0] > selectX and mousePos[0] < (selectX + buttonWidth)) and (mousePos[1] > selectY and mousePos[1] < (selectY + buttonHeight)):
        global showSpawnMenu
        showSpawnMenu = True


def handleStartSimButton(mousePos):
    startSimX = 5
    startSimY = 165
    if (mousePos[0] > startSimX and mousePos[0] < (startSimX + buttonWidth)) and (mousePos[1] > startSimY and mousePos[1] < (startSimY + buttonHeight)):
        global moveKeyPressed
        global infoText
        global showSpawnMenu
        if moveKeyPressed == False:
            infoText = "Simulation started. Select a new track to reset system."
            moveKeyPressed = True
            showSpawnMenu = False
        else:
            infoText = "Simulation stopped."
            moveKeyPressed = False
            showSpawnMenu = True


def handleBackButton(mousePos):
    backX = 5
    backY = 285

    if (mousePos[0] > backX and mousePos[0] < (backX + buttonWidth)) and (mousePos[1] > backY and mousePos[1] < (backY + buttonHeight)):
        global isLaunchScreen
        isLaunchScreen = True


def handleReverseButton(mousePos):
    reverseX = 5
    reverseY = 350
    if (mousePos[0] > reverseX and mousePos[0] < (reverseX + buttonWidth)) and (mousePos[1] > reverseY and mousePos[1] < (reverseY + buttonHeight)):
        global reverseTrain
        reverseTrain = not reverseTrain


def onStationHover(mousePos):
    for x in stationCount:
        # This is used to draw a line from the station button to the actual station when the mouse hovers over it.
        if (mousePos[0] > x[0] and mousePos[0] < x[0] + x[2] and mousePos[1] > x[1] and mousePos[1] < x[1] + x[3]):
            for t in track:
                if t.getID() == x[4]:
                    pygame.draw.line(
                        screen, (255, 102, 102), (x[0]+50, x[1]+55), (t.getCoordinates()[0], t.getCoordinates()[1]), 2)


def showStopStationSelectionSidebar():
    global infoText
    global initialStation
    infoText = "Select the stations you want the train to stop at. You cannot select duplicate or occupied stations."

    draw_button(screen, buttonColour, 5, 165, 205, 600,
                text="Station " + str(initialStation.getID()), center=(100, 193), border_radius=10)
    runningY = 215
    for s in stationList:
        write_text("v", (100, runningY))
        runningY += 22
        write_text("Station " + str(s.getID()), (100, runningY))
        runningY += 22
    draw_button(screen, buttonColour, 55, 628,
                buttonWidth, buttonHeight, text="Remove", center=(110, 658), border_width=2, border_radius=10)
    draw_button(screen, buttonColour, 55, 695,
                buttonWidth, buttonHeight, text="Create Plan", center=(110, 720), border_width=2, border_radius=10)


def handleRemoveButtonInSidebar(mousePos):
    removeX = 55
    removeY = 628

    if (mousePos[0] > removeX and mousePos[0] < (removeX + buttonWidth)) and (mousePos[1] > removeY and mousePos[1] < (removeY + buttonHeight)) and len(stationList) >= 1:
        stationList.pop(len(stationList) - 1)


def generatePddlPath():
    global infoText
    global pathSelect
    global spawnMenu
    # Initialize the variables that will be used to create the plan file.
    junctionList = []
    stations = []
    connected = []
    branches = []
    stationWBranches = []
    branches.append("1")
    stopPoints = []

    for t in track:
        # This is used to add the information about each stop to a dictionary.
        if t in stationList:
            stopPoints.append(t.getID())
        # This is used to add a new branch from the junctions.
        if t.getType() == "Junction":
            junctionList.append(t.getID())
            for g in track:
                if g.getID() == t.getSecondNextID():
                    connected.append(
                        (t.getBranch()[0:len(t.getBranch())-1], t.getID(), (str(int(g.getBranch())))))
                    branches.append((str(int(g.getBranch()))))
        # This creates a list of all stations and combines them with what branch they are on.
        if t.getType() == "Station":
            stations.append(t.getID())
            stationWBranches.append(
                (t.getID(), t.getBranch()[0:len(t.getBranch())-1]))
    # This appends the initial station to the stop list.
    stopPoints.append(startingTrack.getID())
    stationList.append(startingTrack)

    # This creates a new object that is an instance of the train_pddl.py file.
    problem = TrainPDDLProblem(junctionList, connected, stations, stationWBranches,
                               branches, stopPoints, startingTrack.getBranch()[0:len(startingTrack.getBranch())-1])
    # This generates the problem file using the information above.
    problem.generate_problem_pddl()
    # This converts a piece of text to something the command line can read.
    # This is used to generate a PDDL plan using a domain that I wrote and the previously generated problem file.
    command = shlex.split("python -B -m pddl_parser.planner '" +
                          directory+"/domain.pddl' '"+directory+"/problem.pddl'")
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    plan = process.communicate()

    # # Decode byte strings and keep regular strings as they are
    plan = ''.join(
        [part.decode('utf-8').replace('\n', '\\n') if isinstance(part,
                                                                 bytes) else part.replace('\n', '\\n') for part in plan]
    )

    # The following lines of code are used to trim the output of the previous command into a format that my system can read.
    tempPlan = plan.split("\\n")
    consoleMessage.add("- Plan found in " +
                       tempPlan[0][9:13] + " seconds")
    plan = plan.split('\\n')
    plan.pop(0)
    plan.pop(0)
    plan.pop(len(plan)-1)
    for p in range(0, len(plan)):
        plan[p] = plan[p].replace("track", "")
        plan[p] = plan[p].replace("tn ", "")

    tempPlan = []
    for p in plan:
        p = p.replace("station", "")
        p = p.replace("branch", "")
        p = p.replace("junction", "")
        tempPlan.append(p.split(" "))

    if tempPlan[0][1] != startingTrack.getID():
        temp = tempPlan[0]
        tempPlan[0] = tempPlan[len(tempPlan)-1]
        tempPlan[len(tempPlan)-1] = temp

    # This section will append a final instruction to switch at the next junction when the initial station is not on the first branch.
    # This is required to send the train back to the appropriate starting station after it has completed the list of instructions.
    # This is not required if the train starts on the first branch because all branches eventually connect to the first.
    if startingTrack.getBranch() != 1:
        for t in track:
            if t.getType() == "Junction":
                if int(t.getBranch()) + 1 == int(startingTrack.getBranch()):
                    tempPlan.append(("switch", t.getID(), t.getBranch()[
                                    0:len(t.getBranch())-1], str(int(t.getBranch()) + 1)))

    # Three sets of instructions need to be appended to account for trains being sets of 3.
    # The other two sets of instructions will not be used.

    instructions.append(tempPlan)
    instructions.append(tempPlan)
    instructions.append(tempPlan)

    currentInstruction.append(instructions[len(instructions)-1][0])
    currentInstruction.append(instructions[len(instructions)-1][0])
    currentInstruction.append(instructions[len(instructions)-1][0])

    instructionCounter.append(0)
    instructionCounter.append(0)
    instructionCounter.append(0)

    # Empties the list of stops and closes the spawning menu.
    stationList.clear()
    spawnMenu = False
    pathSelect = False

    infoText = "Train spawned and plan generated. Start simulation or spawn another train."


def handleCreateButtonInSidebar(mousePos):
    createX = 55
    createY = 695
    if (mousePos[0] > createX and mousePos[0] < (createX + buttonWidth)) and (mousePos[1] > createX and mousePos[1] < (createY + buttonHeight)):
        generatePddlPath()


def onStationSelect(mousePos):
    """
    This method is used to check what station the user has clicked on and when.
    """
    global pathSelect
    global occupiedSpawns
    global stationList
    global tempStartPointX
    global tempStartPointY
    global spawningCompass
    global startingTrack
    global initialStation
    global startingNextTrack
    global spawning
    for station in stationCount:
        # This if statement checks if the user has clicked on a station, the x values are the coordinates of the buttons
        if (mousePos[0] > station[0] and mousePos[0] < station[0] +
                station[2] and mousePos[1] > station[1] and mousePos[1] < station[1] + station[3]):
            # If pathSelect is false it means that it's dealing with the spawn station. It also ensures that the station isn't already occupied.
            if pathSelect == False and station[4] not in occupiedSpawns:
                # This finds the spawning station from the track list.
                for t in track:
                    if t.getID() == station[4]:
                        # This adds the station to the list of occupied stations.
                        occupiedSpawns.append(t.getID())
                        # These are temporary variables used for spawning the train.
                        tempStartPointX = t.getCoordinates()[0]
                        tempStartPointY = t.getCoordinates()[1]
                        spawningCompass = t.getCompass()
                        # These are used for the PDDL section
                        startingTrack = t
                        initialStation = t
                        # This for loop gets the id for the next track. If the next track is a junction and the train needs to turn, it will derail.
                        # But, this data is overwritten before the train starts to move so it will not be a problem.
                        for t2 in track:
                            if t2.getID() == t.getNextID():
                                startingNextTrack = t2
                                break
                        spawning = True
            else:
                # This goes through the track list and adds the station the user clicked on to the path.
                for t in track:
                    if t.getID() == station[4] and t not in stationList and t != initialStation:
                        stationList.append(t)
                        break


# initilize pygame
pygame.init()
# Initialize fonts
buttonText = pygame.font.Font('calibri.ttf', 20)
headingText = pygame.font.Font('calibri.ttf', 30)
titleText = pygame.font.Font('calibri.ttf', 52)

# The following is various variables that will be used throughout the program.

# Stores readable information about tracks.
trackDictionary = []
# Stores instances of track classes.
track = []
# This holds the current track and the next track for each train.
tracksDict = []
# This holds all the tracks in the "ExampleTracks" folder.
tracksList = []
# This is used to display buttons for the tracks
tracksCountButton = []
# This holds the angle each train is currently facing. This is used for train rotation around a curve.
angle = []
# This holds the compass direction each train is facing. This is used define how a train should move around a curve.
trainCompass = "E"
# Train movement around a curve uses a vector, which gives coordinates around a circle. This holds the centre point of the circle.
circleCenter = []
# This keeps track of available spawning stations for display.
stationCount = []
# This holds a list of stations that already have a train spawned at them.
occupiedSpawns = []
# Holds a list of stations to stop at.
stationList = []
# This holds the colour that a train will spawn in. This does not need to be reset as it is random.
spawnColour = []
# This will hold a list of active trains.
trainList = []
# This holds the current compass for each train.
trainCompassDict = []
# This holds a boolean value for each train that defines whether or not to change its compass.
swapTrainCompass = []
# This is used to tell trains which direction to turn at a junction.
junctionDirection = []
# This tells a train to stop at a station.
stationStop = []
# This timer states how long a train has been stopped at a station for.
timer = []
# Tells a train that it needs to turn at the next junction.
switch = []
# This is used to stop carriages at stations.
carriageStop = []
# Holds the list of PDDL instructions for each train.
instructions = []
# Holds the current instruction each train is working on.
currentInstruction = []
# Holds the index of the instruction each train is working on.
instructionCounter = []
# This holds the coordinates to spawn a train at. Both of these are overwritten before spawning.
startPointX = screenWidth/2
startPointY = screenHeight/2
# These define the start point for train spawning.
tempStartPointX = 0
tempStartPointY = 0
# This stores the compass direction to spawn the trains at. This is defined by the station you choose.
spawningCompass = "E"
# These define the starting and next tracks on train spawning. Both are overwritten on spawn.
startingTrack = "null"
startingNextTrack = "null"
# Holds the name of the first station as this isn't added to the list of stops until the list gets moved to the PDDL file.
initialStation = ""
# This is used for spawning the carriages of a train. It ensures the carriages are spawned one after the other and not on top of each other.
spawnTimer = 0
# This is used to change what type of train is spawned. 0 = train, 1 and 2 = carriages.
spawnIteration = 0

# Flags to control what to display
# This stops the spawning code from running while the spawnTimer isn't complete.
waiting = False
isLaunchScreen = True
isOpenConsole = False
showTrackSelection = False
isClearConsole = False
isSpawnScreen = False
trackSelected = False
imageSelected = False
moveKeyPressed = False
showSpawnMenu = False
pathSelect = False
# This is used to tell the system when a train is spawning.
spawning = False
reverseTrain = False
# store the selected track

# this is the info text
infotext = "Select a track"

# some of the variables required
startScroll = 0
scrollBarY = 115


# This loads in every file name inside the directory "ExampleTracks".
for file in os.listdir("ExampleTracks"):
    tracksList.append(file)

# A set to keep track of console messages
consoleMessage = set()
selectedTrack = None


# This will run the pygame while loop.
mainLoop = True
# This is a display screen. This is where everything that the user can see will be drawn to.
screen = pygame.display.set_mode(
    (screenWidth, screenHeight))
# for full screen (ui bigrincha full screen ma it was never designed with full screen in mind)
# screen = pygame.display.set_mode(
#     (screenWidth, screenHeight), pygame.FULLSCREEN)


# This is the main loop. Every iteration is one frame of the display.
while mainLoop:
    counter = 0

    # This holds the position of the mouse pointer and is updated on every frame.
    mousePos = pygame.mouse.get_pos()

    # Makes the background of the screen black. This has to happen before anything is drawn on the screen as it will overwrite it
    screen.fill((21, 30, 41))

    # Loops through the events of the last frame
    for event in pygame.event.get():
        # This checks if a key has been pressed.
        if event.type == pygame.KEYDOWN:
            # If the key that was pressed was escape, it exits the main loop which closes the program.
            if event.key == pygame.K_ESCAPE or event.type == pygame.QUIT:
                mainLoop = False
        # Checks if the right mouse button has been clicked.
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if isLaunchScreen:
                handleOpenLaunchScreen(mousePos)
            elif isOpenConsole and not isClearConsole:
                # if console is open and clear button is pressed clear the console
                handleConsoleClearButtonClick(mousePos)
                handleOpenConsoleButtonClick(mousePos)
            elif isSpawnScreen:
                handleOpenConsoleButtonClick(mousePos)
                handleTrackButton(mousePos)
                handleSpawnTrainButton(mousePos)
                handleStartSimButton(mousePos)
                handleBackButton(mousePos)
                handleTrackSelection(mousePos)
                if selectedTrack:
                    handleSelectButtonInTrack(mousePos)
                handleSpawnTrainButton(mousePos)
                if showSpawnMenu:
                    onStationSelect(mousePos)
                if pathSelect:
                    handleCreateButtonInSidebar(mousePos)
                    handleRemoveButtonInSidebar(mousePos)
                if moveKeyPressed:
                    handleReverseButton(mousePos)

        elif event.type == pygame.MOUSEWHEEL:
            scrollEffectTrackSelection(
                event, mousePos)
    if isLaunchScreen:
        showLaunchScreen()
    elif isSpawnScreen:
        showMainScreen()
        if isOpenConsole:
            showConsole(consoleMessage)
        elif showTrackSelection:
            showTrackScreen(imageSelected)
        elif generateTrack:
            generateTrainTrack()
            if showSpawnMenu:
                stationSelectionMenu()
                onStationHover(mousePos)
            # This is run if a train is to be spawned.
        if spawning == True:
            # This adds one to the timer that stops trains and carriages from spawning on top of each other.
            spawnTimer += 1
            # If the spawn timer is 190 (enough time for train to clear spawn point), reset the timer and stop the train from moving.
            if spawnTimer == 190:
                waiting = False
                spawnTimer = 0

            # This is used to change the angle the trains spawn at based on what compass direction they are on.
            spawningAngle = 0
            if spawningCompass == "N":
                spawningAngle = 90
            elif spawningCompass == "NE":
                spawningAngle = 45
            elif spawningCompass == "E":
                spawningAngle = 0
            elif spawningCompass == "SE":
                spawningAngle = 315
            elif spawningCompass == "S":
                spawningAngle = 270
            elif spawningCompass == "SW":
                spawningAngle = 225
            elif spawningCompass == "W":
                spawningAngle = 180
            elif spawningCompass == "NW":
                spawningAngle = 135
            # This ensures no trains or carriages appear while the timer is counting.
            if waiting == False:
                # Spawn iteration 0 will spawn a train.
                if spawnIteration == 0:
                    tempColour = random.randint(1, 5)
                    if tempColour == 1:
                        spawnColour.append("red")
                        spawnColour.append("red")
                        spawnColour.append("red")
                    if tempColour == 2:
                        spawnColour.append("blue")
                        spawnColour.append("blue")
                        spawnColour.append("blue")
                    if tempColour == 3:
                        spawnColour.append("yellow")
                        spawnColour.append("yellow")
                        spawnColour.append("yellow")
                    if tempColour == 4:
                        spawnColour.append("green")
                        spawnColour.append("green")
                        spawnColour.append("green")
                    if tempColour == 5:
                        spawnColour.append("purple")
                        spawnColour.append("purple")
                        spawnColour.append("purple")
                    # The following will append necessary information to various dictionaries for the train.
                    trainList.append(
                        train(screen, tempStartPointX, tempStartPointY))
                    tracksDict.append((startingTrack, startingNextTrack))
                    trainCompassDict.append(spawningCompass)
                    angle.append(spawningAngle)
                    swapTrainCompass.append(False)
                    circleCenter.append((0, 0))
                    junctionDirection.append(0)
                    track[0].setOccupied(True)
                    stationStop.append(False)
                    timer.append(0)
                    spawnIteration = 1
                    waiting = True
                    moveKeyPressed = True
                    carriageStop.append(False)
                    switch.append(False)
                # Spawn iterations 1 and 2 are carriages. Essentially the same as trains but will have different priviliges later.
                elif spawnIteration == 1:
                    trainList.append(
                        carriage(screen, tempStartPointX, tempStartPointY))
                    tracksDict.append((startingTrack, startingNextTrack))
                    trainCompassDict.append(spawningCompass)
                    angle.append(spawningAngle)
                    swapTrainCompass.append(False)
                    circleCenter.append((0, 0))
                    junctionDirection.append(0)
                    track[0].setOccupied(True)
                    stationStop.append(False)
                    timer.append(0)
                    spawnIteration = 2
                    waiting = True
                    moveKeyPressed = True
                    carriageStop.append(False)
                    switch.append(False)
                elif spawnIteration == 2:
                    trainList.append(
                        carriage(screen, tempStartPointX, tempStartPointY))
                    tracksDict.append((startingTrack, startingNextTrack))
                    trainCompassDict.append(spawningCompass)
                    angle.append(spawningAngle)
                    swapTrainCompass.append(False)
                    circleCenter.append((0, 0))
                    junctionDirection.append(0)
                    track[0].setOccupied(True)
                    stationStop.append(False)
                    timer.append(0)
                    spawnIteration = 0
                    spawning = False
                    waiting = True
                    pathSelect = True
                    carriageStop.append(False)
                    moveKeyPressed = False
                    switch.append(False)
                    consoleMessage.add("- Train spawned at a Station")
        # This holds the list of generated trains.
    trainImageList = []
    # For loop that loads in the images for each train. This has to happen after the track is generated otherwise the train will be under the track.
    colourCounter = 0
    for x in trainList:
        trainImageList.append(x.generateTrain(spawnColour[colourCounter]))
        colourCounter += 1

    # This for loop will draw each train on the screen.
    spawnCounter = 0
    for x in trainList:
        x.spawnTrain(x.getCurrentPosition()[0], x.getCurrentPosition()[
                     1], screen, trainImageList[spawnCounter], angle[spawnCounter])
        spawnCounter += 1

    # The following is everything that occurs when the simulation is running.
    if moveKeyPressed == True:

        # This iterates through the list of trains and carries out instructions accordingly.
        for x in trainList:
            # If the current train is at a station then increase the stop timer.
            if stationStop[counter] == True:
                timer[counter] += 1
            # If the timer is at 1000 then perform the actions to start the train again.
            if timer[counter] >= 1000:
                # This loads the next instruction for the train.
                currentInstruction[counter] = instructions[counter][instructionCounter[counter]]
                # if the next instruction is to switch at a junction, activate the switch variable for the train and the next two carriages.
                if "switch" in currentInstruction[counter][0]:
                    switch[counter] = True
                    switch[counter+1] = True
                    switch[counter+2] = True
                # If the next instruction is to return then move into the next instruction.
                elif "return" in currentInstruction[counter][0]:
                    instructionCounter[counter] += 1
                    currentInstruction[counter] = instructions[counter][instructionCounter[counter]]
                # Reset the station stop variable for the train.
                stationStop[counter] = False

            # This is used to find out if the next track is occupied, if it is it will stop the train accordingly.
            # Only runs if there is more than one train running as otherwise there are no trains to stop for.
            tempT = tracksDict[counter][1]
            for t in track:
                if t.getID() == tracksDict[counter][1].getNextID():
                    tempT = t
            if tempT.isOccupied() == True and x.getType() == "Train" and spawning == False and len(trainList) > 3:
                carriageStop[counter] = True
            elif tempT.isOccupied() == False and x.getType() == "Train" and spawning == False:
                carriageStop[counter] = False

            # The next four if statements are made to copy the instructions of a train to the two following carriages.
            if carriageStop[counter] == True and x.getType() == "Train" and spawning == False:
                carriageStop[counter+1] = True
                carriageStop[counter+2] = True
            if carriageStop[counter] == False and x.getType() == "Train" and spawning == False:
                carriageStop[counter+1] = False
                carriageStop[counter+2] = False
            if stationStop[counter] == False and x.getType() == "Train" and spawning == False:
                stationStop[counter+1] = False
                stationStop[counter+2] = False
            elif stationStop[counter] == True and x.getType() == "Train" and spawning == False:
                stationStop[counter+1] = True
                stationStop[counter+2] = True

            # This section will activate the moveSkip variable according to if and what is spawning.
            moveSkip = False
            if spawning == True:
                if spawnIteration == 0:
                    if counter != len(trainList)-1:
                        moveSkip = True
                if spawnIteration == 1:
                    if counter < len(trainList)-1:
                        moveSkip = True
                if spawnIteration == 2:
                    if counter < len(trainList)-2:
                        moveSkip = True

            # This makes sure trains don't move if they're at stations or behind occupied tracks.
            if stationStop[counter] == False and carriageStop[counter] == False and moveSkip == False:

                # These if statements adjust the angle of the current train based on what the current track piece is.
                if tracksDict[counter][0].getType() == "LongRight" or (tracksDict[counter][0].getType() == "JunctionRight" and junctionDirection[counter] == 1):
                    angle[counter] = angle[counter] - 0.1
                if tracksDict[counter][0].getType() == "ShortRight":
                    angle[counter] = angle[counter] - 0.2
                if tracksDict[counter][0].getType() == "LongLeft" or (tracksDict[counter][0].getType() == "JunctionLeft" and junctionDirection[counter] == 1):
                    angle[counter] = angle[counter] + 0.1
                if tracksDict[counter][0].getType() == "ShortLeft":
                    angle[counter] = angle[counter] + 0.2

               # This if statement is triggered when a train has reached the end of the current track. The numbers don't line up exactly, so they are rounded to four decimal places.
                trainPosX = float("{:.4f}".format(x.getCurrentPosition()[0]))
                trainPosY = float("{:.4f}".format(x.getCurrentPosition()[1]))
                nextTrackX = float("{:.4f}".format(
                    tracksDict[counter][1].getCoordinates()[0]))
                nextTrackY = float("{:.4f}".format(
                    tracksDict[counter][1].getCoordinates()[1]))

                if (trainPosX == nextTrackX and trainPosY == nextTrackY) or ((trainPosX < nextTrackX and trainPosX + 0.3 > nextTrackX) and trainPosY == nextTrackY):
                    # This if statement checks if a train is stopped and at a station, then loads in the next instruction for it.
                    if tracksDict[counter][0].getType() == "Station" and timer[counter] < 1000 and x.getType() == "Train":
                        if "stop" in currentInstruction[counter][0] and tracksDict[counter][0].getID() == currentInstruction[counter][1]:
                            stationStop[counter] = True
                            instructionCounter[counter] += 1
                            if instructionCounter[counter] == len(instructions[counter]):
                                instructionCounter[counter] = 0
                    else:
                        # If the train isn't at a station then the timer should always be 0.
                        timer[counter] = 0
                    # This stops the train if the next track is occupied.
                    if tracksDict[counter][1].isOccupied() == True and x.getType() == "Train":
                        carriageStop[counter] = True
                    # If the current track is not any kind of straight and the next track is, it needs to adjust the current trains compass once.
                    # This is to fix a problem in that the compass wasn't being set properly when a train transitions from a curve to a straight.
                    if (tracksDict[counter][0].getType() != "LongStraight" or tracksDict[counter][0].getType() != "ShortStraight" or tracksDict[counter][0].getType() != "Station") and (tracksDict[counter][1].getType() == "LongStraight" or tracksDict[counter][1].getType() == "ShortStraight" or tracksDict[counter][1].getType() == "Station"):
                        trainCompassDict[counter] = tracksDict[counter][0].adjustCompass(
                            trainCompassDict[counter])

                    # If the next track is a junction and the train has been instructed to switch branch, then it enables the variable that is actually used to change the junction.
                    # It also adjusts the compass to match the track piece on the end of the curve.
                    # Finally, it loads in the next instruction.
                    if tracksDict[counter][1].getType() == "Junction" and switch[counter] == True:
                        for t in track:
                            if t.getID() == tracksDict[counter][1].getSecondNextID():
                                tracksDict[counter] = (
                                    tracksDict[counter][0], t)
                                break

                        if tracksDict[counter][1].getID() == currentInstruction[counter][1]:
                            if x.getType() == "Train":
                                junctionDirection[counter] = 1
                                junctionDirection[counter+1] = 1
                                junctionDirection[counter+2] = 1
                                r = tracksDict[counter][0].adjustCompass(
                                    trainCompassDict[counter])
                                trainCompassDict[counter] = r
                                trainCompassDict[counter+1] = r
                                trainCompassDict[counter+2] = r
                                switch[counter] = False
                                switch[counter+1] = False
                                switch[counter+2] = False
                                instructionCounter[counter] += 1
                                if instructionCounter[counter] == len(instructions[counter]):
                                    instructionCounter[counter] = 0
                                currentInstruction[counter] = instructions[counter][instructionCounter[counter]]

                    # If the next track is a junction and the train doesn't have to turn, it resets the variable.
                    elif tracksDict[counter][1].getType() == "Junction" and switch[counter] == False:
                        for t in track:
                            if t.getID() == tracksDict[counter][1].getNextID():
                                tracksDict[counter] = (
                                    tracksDict[counter][0], t)
                                break
                        if x.getType() == "Train":
                            junctionDirection[counter] = 0
                            junctionDirection[counter+1] = 0
                            junctionDirection[counter+2] = 0
                    # This loop will replace the current track with the next track and fetch the new next track.
                    # It will also set and reset track occupation accordingly.
                    for t in track:
                        if int(t.getID()) == int(tracksDict[counter][1].getNextID()):
                            tracksDict[counter][1].setOccupied(False)
                            tracksDict[counter] = (tracksDict[counter][1], t)
                            if x.getType() == "Train":
                                tracksDict[counter][0].setOccupied(True)
                            break
                        if x.getType() == "Train":
                            if (tracksDict[counter][1].getNextID() == t.getNextID()) and (tracksDict[counter][1].getID() != t.getID()):
                                t.setOccupied(True)
                            else:
                                t.setOccupied(False)
                            for c in track:
                                if c.getID() == tracksDict[counter][1].getNextID() and c.getBranch() != tracksDict[counter][1].getBranch():
                                    c.setOccupied(True)

                    # If the current track is a curve then it collects information for the vector it will use to move the train around it.
                    if tracksDict[counter][0].getType() == "LongRight" or tracksDict[counter][0].getType() == "LongLeft" or tracksDict[counter][0].getType() == "ShortRight" or tracksDict[counter][0].getType() == "ShortLeft" or (tracksDict[counter][0].getType() == "JunctionLeft" and junctionDirection[counter] == 1) or (tracksDict[counter][0].getType() == "JunctionRight" and junctionDirection[counter] == 1):
                        circleCenter[counter], angle[counter], swapTrainCompass[counter] = trainMover.setValues(
                            tracksDict[counter][0].getType(), tracksDict[counter][0], trainCompassDict[counter])

                # This moveTrain function will take in all of the information gathered until this point and redraw the train at a new angle and coordinate.
                if reverseTrain:
                    trainImageList[counter] = x.reverseTrain(x.getCurrentPosition()[0], x.getCurrentPosition()[1], tracksDict[counter][0].getType(
                    ), screen, trainCompassDict[counter], trainImageList[counter], angle[counter], circleCenter[counter], junctionDirection[counter])
                else:
                    trainImageList[counter] = x.moveTrain(x.getCurrentPosition()[0], x.getCurrentPosition()[1], tracksDict[counter][0].getType(
                    ), screen, trainCompassDict[counter], trainImageList[counter], angle[counter], circleCenter[counter], junctionDirection[counter])

                # This adjusts the current trains compass.
                if swapTrainCompass[counter] == True:

                    if ("Right" in tracksDict[counter][1].getType() or "Left" in tracksDict[counter][1].getType()) and "Junction" not in tracksDict[counter][1].getType():
                        trainCompassDict[counter] = tracksDict[counter][0].adjustCompass(
                            trainCompassDict[counter])

                    else:
                        trainCompassDict[counter] = tracksDict[counter][1].adjustCompass(
                            trainCompassDict[counter])

                    swapTrainCompass[counter] = False

            # This counter represents the train that is being run through the system.
            counter += 1

    if pathSelect:
        showStopStationSelectionSidebar()

    # Update the display
    pygame.display.flip()
    pygame.display.update()

# quit pygame
pygame.quit()
sys.exit()
