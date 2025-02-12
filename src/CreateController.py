import maya.cmds as mc

####################################
#            Facilities            #
####################################
class Vector:
    def __init__(self, *args):
        self.x = args[0]
        self.y = args[1]
        self.z = args[2]

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)
    
    # operator - overload
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)
    
    # operator * overload  
    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def __truediv__(self, scalar):
        return Vector(self.x/scalar, self.y/scalar, self.z/scalar)
    
    def GetLength(self):
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5
    
    def GetNormalized(self):
        return self/self.GetLength()
    
    def __str__(self):
        return f"<{self.x},{self.y},{self.z}>"

def GetObjPos(obj):
    pos = mc.xform(obj, t=True, q=True, ws=True)
    return Vector(pos[0], pos[1], pos[2])

def SetObjPos(obj, pos: Vector):
    mc.setAttr(obj + ".translate", pos.x, pos.y, pos.z, type = "float3")

def CreateControllerForJnt(jnt, size = 10):
    ctrlName = "ac_" + jnt
    ctrlGrpName = ctrlName + "_grp"

    mc.circle(n=ctrlName, nr=(1,0,0), r = size)
    mc.group(ctrlName, n = ctrlGrpName)
    mc.matchTransform(ctrlGrpName, jnt)
    mc.orientConstraint(ctrlName, jnt)

    return ctrlName, ctrlGrpName


def CreateBox(name, size = 10):
    #curve -d 1 -p -0.5 0.5 0.5 -p 0.5 0.5 0.5 -p 0.5 0.5 -0.5 -p -0.5 0.5 -0.5 -p -0.5 0.5 0.5 -p -0.5 -0.5 0.5 -p 0.5 -0.5 0.5 -p 0.5 0.5 0.5 -p 0.5 -0.5 0.5 -p 0.5 -0.5 -0.5 -p 0.5 0.5 -0.5 -p 0.5 -0.5 -0.5 -p -0.5 -0.5 -0.5 -p -0.5 0.5 -0.5 -p -0.5 -0.5 -0.5 -p -0.5 -0.5 0.5 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 ;
    p = ((-0.5,0.5,0.5), (0.5,0.5,0.5), (0.5,0.5,-0.5), (-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5), (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (0.5, -0.5, 0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (0.5, -0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, 0.5, -0.5), (-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5))
    mc.curve(n=name, d=1, p = p)

    mc.setAttr(name + ".scale", size,size,size, type = "float3")
    mc.makeIdentity(name, apply = True)

def CreatePlus(name, size = 10):
    p = ((0.5,0,1),(0.5,0,0.5),(1,0,0.5),(1,0,-0.5),(0.5, 0,-0.5), (0.5, 0, -1),(-0.5, 0, -1),(-0.5,0,-0.5),(-1, 0, -0.5),(-1,0,0.5),(-0.5,0,0.5),(-0.5,0,1),(0.5,0,1))
    mc.curve(n=name, d=1, p = p)
    mc.setAttr(name + ".rx", 90)
    mc.setAttr(name + ".scale", size,size,size, type = "float3")
    mc.makeIdentity(name, apply = True)

class ThreeJntChain:
    def __init__(self):
        self.root = ""
        self.middle = ""
        self.end = ""
        self.controllerSize = 5

    def AutoFindJntsBasedOnSel(self):
        self.root = mc.ls(sl=True, type = "joint")[0]
        self.middle = mc.listRelatives(self.root, c=True, type = "joint")[0]
        self.end = mc.listRelatives(self.middle, c=True, type ="joint")[0]

    def RigThreeJntChain(self):
        rootCtrl, rootCtrlGrp = CreateControllerForJnt(self.root, self.controllerSize)
        middleCtrl, middleCtrlGrp = CreateControllerForJnt(self.middle, self.controllerSize)
        endCtrl, endCtrlGrp = CreateControllerForJnt(self.end, self.controllerSize)

        mc.parent(middleCtrlGrp, rootCtrl)
        mc.parent(endCtrlGrp, middleCtrl)

        ikEndCtrl = "ac_ik_" + self.end
        CreateBox(ikEndCtrl, self.controllerSize)
        ikEndCtrlGrp = ikEndCtrl + "_grp"
        mc.group(ikEndCtrl, n = ikEndCtrlGrp)
        mc.matchTransform(ikEndCtrlGrp, self.end)
        endOrientConstraint = mc.orientConstraint(ikEndCtrl, self.end)[0]
        
        ikHandleName = "ikHanle_" + self.end
        mc.ikHandle(n=ikHandleName, sj = self.root, ee=self.end, sol = "ikRPsolver") 

        ikMidCtrl = "ac_ik_" + self.middle
        mc.spaceLocator(n=ikMidCtrl)
    
        rootJntPos = GetObjPos(self.root)
        endJntPos = GetObjPos(self.end)
        poleVec = mc.getAttr(ikHandleName + ".poleVector")[0]
        poleVec = Vector(poleVec[0], poleVec[1], poleVec[2])

        armVec = endJntPos - rootJntPos
        halfArmLengh = armVec.GetLength()/2

        poleVecPos = rootJntPos + poleVec * halfArmLengh + armVec/2
        ikMidCtrlGrp = ikMidCtrl + "_grp"
        mc.group(ikMidCtrl, n = ikMidCtrlGrp)
        mc.setAttr(ikMidCtrl+".scale", self.controllerSize, self.controllerSize, self.controllerSize, type = "float3")
        SetObjPos(ikMidCtrlGrp, poleVecPos)     

        mc.poleVectorConstraint(ikMidCtrl, ikHandleName)
        mc.parent(ikHandleName, ikEndCtrl)
        
        ikfkBlendCtrl = "ac_" + self.root + "_ikfk_blend"
        CreatePlus(ikfkBlendCtrl, 2)
        ikfkBlendCtrlGrp = ikfkBlendCtrl + "_grp"
        mc.group(ikfkBlendCtrl, n = ikfkBlendCtrlGrp)

        dir = 1
        if rootJntPos.x < 0:
            dir = -1
            
        ikfkBlendPos = rootJntPos + Vector(dir * halfArmLengh/4, halfArmLengh/4, 0)
        SetObjPos(ikfkBlendCtrlGrp, ikfkBlendPos)

        ikfkBlendAttr = "ikfkBlend"
        mc.addAttr(ikfkBlendCtrl, ln = ikfkBlendAttr, k=True, at = "float", min = 0, max = 1)
        mc.connectAttr(ikfkBlendCtrl + "." + ikfkBlendAttr, ikHandleName + ".ikBlend")

        ikfkReverse = "reverse_" + self.root + "_ikfkblend"
        mc.createNode("reverse", n = ikfkReverse)

        mc.connectAttr(ikfkBlendCtrl+"."+ikfkBlendAttr, ikfkReverse+".inputX")
        mc.connectAttr(ikfkBlendCtrl+"."+ikfkBlendAttr, ikEndCtrlGrp + ".v")
        mc.connectAttr(ikfkBlendCtrl+"."+ikfkBlendAttr, ikMidCtrlGrp + ".v")
        mc.connectAttr(ikfkReverse+ ".outputX", rootCtrlGrp +".v")

        mc.connectAttr(ikfkReverse + ".outputX", endOrientConstraint + ".w0")
        mc.connectAttr(ikfkBlendCtrl + "." +ikfkBlendAttr, endOrientConstraint + ".w1")

        #group everything together and name it properly
        topGrpName = self.root + "_rig_grp"
        mc.group(rootCtrlGrp, ikEndCtrlGrp, ikMidCtrlGrp, ikfkBlendCtrlGrp, n = topGrpName)
        #hide useless stuff - ikHandle.
        mc.hide(ikHandleName)



####################################
#                UI                #
####################################

if int(mc.about(v=True)) <= 2024:
    from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QLineEdit, QHBoxLayout, QColorDialog
    from PySide2.QtGui import QDoubleValidator, QColor, QPainter, QPalette
else:
    from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QLineEdit, QHBoxLayout, QColorDialog
    from PySide6.QtGui import QDoubleValidator, QColor, QPainter, QPalette

import MayaUtilities

class ColorPickerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.color = QColor(0,0,0)
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)
        self.button = QPushButton()
        self.setAutoFillBackground(True)
        self.masterLayout.addWidget(self.button)
        #self.setFixedSize(100,20)

    def mousePressEvent(self, event):
        color = QColorDialog().getColor()
        #self.button.

class ThreeJntChainWiget(MayaUtilities.QMayaWidget):
    def GetWidgetHash(self):
        return "THreeJntChainWidget1313123123JT"

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Create Three Joint Chain")
        self.setGeometry(0, 0, 300, 300)
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout) 
        hintLabel = QLabel("Please Select the root of the joint chain:")        
        self.masterLayout.addWidget(hintLabel)

        autoFindBtn = QPushButton("Auto Find Jnts")
        self.masterLayout.addWidget(autoFindBtn)         
        autoFindBtn.clicked.connect(self.AutoFindBtnClicked)

        self.selectionDisplay = QLabel()
        self.masterLayout.addWidget(self.selectionDisplay)

        ctrlSettingLayout = QHBoxLayout()
        ctrlSizeLabel = QLabel("Controller Size: ")
        ctrlSettingLayout.addWidget(ctrlSizeLabel)

        self.ctrlSize = QLineEdit()
        self.ctrlSize.setValidator(QDoubleValidator())
        self.ctrlSize.setText("10")
        self.ctrlSize.textChanged.connect(self.CtrlSizeValueSet)
        ctrlSettingLayout.addWidget(self.ctrlSize)

        self.masterLayout.addLayout(ctrlSettingLayout)

        self.colorPicker = ColorPickerWidget()
        self.masterLayout.addWidget(self.colorPicker)

        rigThreeJntChainBtn = QPushButton("Rig Three Jnt Chain")
        self.masterLayout.addWidget(rigThreeJntChainBtn)
        rigThreeJntChainBtn.clicked.connect(self.RigThreeJntChainBtnClicked)


        self.adjustSize()
        self.threeJntChain = ThreeJntChain()

    def CtrlSizeValueSet(self, valStr:str):
        size = float(valStr)
        self.threeJntChain.controllerSize = size

    def RigThreeJntChainBtnClicked(self):
        self.threeJntChain.RigThreeJntChain()

    def AutoFindBtnClicked(self):
        print("button pressed")
        self.threeJntChain.AutoFindJntsBasedOnSel()
        self.selectionDisplay.setText(f"{self.threeJntChain.root}, {self.threeJntChain.middle}, {self.threeJntChain.end}") 

def Run():
    treeJntChainWidget = ThreeJntChainWiget()
    treeJntChainWidget.show()
