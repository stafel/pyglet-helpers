import pyglet
import json

class AsepriteSprite(pyglet.sprite.Sprite):
    """ Reads animation data from aseprite json export 
    
    Good export parameters for Aseprite:
    Layout: Sheet type Packed with Merge duplicates
    Sprite: Split by Layers and Tags
    Borders: with "Trim sprite" and "By grid" for best result
    Output: Set item filename to: {layer}_{tag}_{frame}
    Json name and Png name must match
    
    Non looping tags can be indicated with a frame duration of 1ms on last frame
    But there must be a looping animation at the end of the animation shedule stack
    Reaching a non looping animation without a follow up causes issues in pyglet
    """
    
    def __init__(self, image_path, json_path, posX, posY, drawBatch, startAnimation=None, startLayer=None, center_images_x=True, center_images_y=True):

        # wrong centering can lead to jittering
        self.center_images_x = center_images_x
        self.center_images_y = center_images_y
        
        self.spritesheetImage = pyglet.resource.image(image_path)
        
        self.animationSequences = {} # holds animation data itself accessed with {layer}_{animation}
        self.availableAnimations = [] # available animations of this sprite
        self.availableLayers = [] # available layers of this sprite
        
        jsonData = None
        with open(json_path, 'r') as jsonFile:
            jsonData = json.loads(jsonFile.read())
        
        # aseprite can split the export into layers, check if we have some available
        for layerData in jsonData['meta']['layers']:
            if not layerData['name'] in self.availableLayers:
                self.availableLayers.append(layerData['name'])
        if len(self.availableLayers) < 1: # we found no layer info, assume the user left everything on default
            self.availableLayers.append('Layer')
        
        individualFrameData = {}
        if type(jsonData['frames']) == dict: # if it is a dict this was exported with the Hash setting, else with List setting
            individualFrameData = self.loadFrameHash(jsonData['frames'])
        else:
            individualFrameData = self.loadFrameList(jsonData['frames'])
        
        for animData in jsonData['meta']['frameTags']:
            
            direction = animData['direction']

            for layer in self.availableLayers:
            
                framesToAdd = []
                
                animationSequenceName = f"{layer}_{animData['name']}"
                
                for imageId in range(int(animData['from']), int(animData['to']) + 1):
                    correctedImageId = imageId - int(animData['from']) # aseprite id is the index in the list and not the index in the animation itself
                    
                    imageIdStr = f"{layer}_{animData['name']}_{correctedImageId}"
                    
                    imageDuration = float(individualFrameData[imageIdStr]['duration']) / 1000.0 # ms to seconds
                    if imageDuration < 0.002: # if duration is one millisecond we assume its none and make the animation nonlooping
                        imageDuration = None
                        
                    framesToAdd.append(pyglet.image.AnimationFrame(individualFrameData[imageIdStr]['region'], duration=imageDuration))           
                
                if direction == 'reverse':
                    framesToAdd.reverse()
                elif direction == 'pingpong':
                    framesToAdd = framesToAdd + framesToAdd.reverse()
                
                self.animationSequences[animationSequenceName] = pyglet.image.Animation(frames=framesToAdd)
                
                if not animData['name'] in self.availableAnimations:
                    self.availableAnimations.append(animData['name'])
        
        if not startAnimation:
            startAnimation = self.availableAnimations[0]
            
        if not startLayer:
            startLayer = self.availableLayers[0]
        
        self.currentLayer = startLayer
        self.currentAnimation = startAnimation
        
        self.sheduledAnimations = []
        super().__init__(self.animationSequences[self.getAnimationSequenceName(self.currentLayer, self.currentAnimation)], x=posX, y=posY, batch=drawBatch)
        self.push_handlers(on_animation_end=self.loadNextAnimation)
        
    def loadFrame(self, imageMetaData):
        """ this cuts a region for a single frame from the aseprite meta frame data """
        
        imgData = imageMetaData['frame']
        
        recalculatedY = self.spritesheetImage.height - imgData['y'] - imgData['h']
        
        convertedRegionData = {'region': self.spritesheetImage.get_region(x=imgData['x'], y=recalculatedY, width=imgData['w'], height=imgData['h']), 'duration': imageMetaData['duration']}
        
        if self.center_images_x:
            convertedRegionData['region'].anchor_x = convertedRegionData['region'].width // 2
        if self.center_images_y:
            convertedRegionData['region'].anchor_y = convertedRegionData['region'].height // 2
            
        return convertedRegionData
        
    def loadFrameList(self, frameMetaList):
        """ converts the aseprite frames list into a dict with imageRegions """
        
        individualImages = {}
        for imgDataMeta in frameMetaList:
            imgKeyStr = imgDataMeta['filename']
            individualImages[imgKeyStr] = self.loadFrame(imgDataMeta)
            
        return individualImages
    
    def loadFrameHash(self, frameMetaHashDict):
        """ converts the aseprite frames hash dict into a dict with imageRegions """
        
        individualImages = {}
        for imgDataMetaKey in frameMetaHashDict:
            imgKeyStr = imgDataMetaKey
            individualImages[imgKeyStr] = self.loadFrame(frameMetaHashDict[imgDataMetaKey])
            
        return individualImages        
        
    def sheduleAnimation(self, animationName, layerName=None):
        if not self.currentAnimation: # we currently have no animation, shedule immediatly
            self.setAnimation(layerName=layerName, animationName=animationName)
        else:
            self.sheduledAnimations.append((layerName, animationName))
    
    def loadNextAnimation(self):
        if len(self.sheduledAnimations) > 0:
            layerName, animationName = self.sheduledAnimations.pop(0)
            
            if not layerName:
                layerName = self.currentLayer            
            
            self.setAnimation(layerName=layerName, animationName=animationName)
        else:
            if self.currentAnimation:
                if not self.animationSequences[self.getAnimationSequenceName(self.currentLayer, self.currentAnimation)].frames[-1].duration: # we stopped the last animation and have no backup ready
                    raise NotImplementedError(f"Animation '{self.currentLayer}_{self.currentAnimation}' is not looping, shedule another one before the first one stops")
        
    def getAnimationSequenceName(self, layerName, animationName):
        return f"{layerName}_{animationName}"
        
    def setAnimation(self, animationName=None, layerName=None, forceReset=False):
        if not layerName:
            layerName = self.currentLayer
        
        if not animationName:
            animationName = self.currentAnimation       
        
        if forceReset or self.currentAnimation != animationName or self.currentLayer != layerName:
            self.image = self.animationSequences[self.getAnimationSequenceName(layerName, animationName)]
            self.currentAnimation = animationName
            self.currentLayer = layerName

    def getDistance(self, position):
        return abs(position[0] - self.position[0])

    def getPosition(self):
        x = self.position[0]
        y = self.position[1]
        
        if self.center_images_x:
            x -= self.width//2
            
        if self.center_images_y:
            y -= self.height//2        
        
        return (x,y)

    def getSize(self):
        return (self.width, self.height)

    def getMidpoint(self):
        pos = self.getPosition()
        size = self.getSize()
        
        return (pos[0] + size[0]//2, pos[1] + size[1]//2)

    def getIconpoint(self):
        """ position to spawn icons in"""
        pos = self.getMidpoint()
        size = self.getSize()

        return (pos[0], pos[1] + size[1] + size[1]//5)
            
    def move(self, deltaX, deltaY):
        self.position = (self.position[0] + deltaX, self.position[1] + deltaY)
        
    def setPosition(self, posX, posY):
        self.update(x=posX, y=posY)
        
    def setBatch(self, batch):
        self.batch = batch

if __name__ == '__main__':
    window = pyglet.window.Window(600, 300)
    batch = pyglet.graphics.Batch()
    test_token = AsepriteSprite('res/test/token.png', 'res/test/token.json', 300, 160, batch, startAnimation='idle')

    @window.event
    def on_draw():
        window.clear()
        batch.draw()

    @window.event
    def on_key_release(symbol, modifiers):
        if symbol == pyglet.window.key.ENTER:
            test_token.setAnimation('derp', forceReset=True)
            test_token.sheduleAnimation('idle')

    pyglet.app.run()