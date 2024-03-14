from GUI_Master import RootGUI, ComGui
from Serial_com_ctrl import SerialCtrl

MySerial = SerialCtrl()
RootMaster = RootGUI()
ComMaster = ComGui(RootMaster.root, MySerial)

RootMaster.root.mainloop()
